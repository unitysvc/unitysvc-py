"""Unit tests for :mod:`unitysvc._streaming`.

Covers the SSE/NDJSON/line/bytes taxonomy on :class:`StreamingResponse`
and :class:`AsyncStreamingResponse`, plus the dominant SSE-client bug
class: a frame whose bytes arrive split across two
``iter_bytes()`` deliveries.

The tests drive the streaming wrapper directly against an
``httpx.Client`` backed by a ``MockTransport`` — no SDK auth /
interface-resolution machinery, since that path is shared verbatim
with :meth:`Services.dispatch` and already covered.
"""

from __future__ import annotations

from collections.abc import Iterable

import httpx
import pytest

from unitysvc._streaming import (
    AsyncStreamingResponse,
    StreamingResponse,
    _parse_sse_frame,
    _sse_split,
)


def _stream_body(chunks: list[bytes], *, content_type: str) -> httpx.MockTransport:
    """Build a MockTransport that yields ``chunks`` as a streaming body."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": content_type},
            stream=_ByteStream(chunks),
        )

    return httpx.MockTransport(handler)


class _ByteStream(httpx.SyncByteStream, httpx.AsyncByteStream):
    """Yield pre-canned bytes; works for both sync and async clients."""

    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks

    def __iter__(self) -> Iterable[bytes]:
        yield from self._chunks

    async def __aiter__(self):  # type: ignore[override]
        for c in self._chunks:
            yield c

    def close(self) -> None:
        return None

    async def aclose(self) -> None:
        return None


# ---------------------------------------------------------------------------
# Pure-function unit tests — frame parser + buffer splitter
# ---------------------------------------------------------------------------

def test_parse_sse_frame_json_data() -> None:
    event = _parse_sse_frame(b'data: {"x": 1}')
    assert event is not None
    assert event.kind == "sse"
    assert event.parsed == {"x": 1}


def test_parse_sse_frame_done_sentinel() -> None:
    event = _parse_sse_frame(b"data: [DONE]")
    assert event is not None
    assert event.kind == "done"


def test_parse_sse_frame_multiline_data_joined_with_newline() -> None:
    # Per the SSE spec, multiple data: lines in one frame are joined with \n.
    event = _parse_sse_frame(b"data: line1\ndata: line2")
    assert event is not None
    assert event.kind == "sse"
    # "line1\nline2" is not valid JSON → falls back to the raw string.
    assert event.parsed == "line1\nline2"


def test_parse_sse_frame_ignores_comments_and_event_field() -> None:
    # Comment-only frame yields nothing.
    assert _parse_sse_frame(b": heartbeat") is None
    # Frame with no data lines also yields nothing.
    assert _parse_sse_frame(b"event: ping\nid: 7") is None


def test_sse_split_holds_back_incomplete_trailer() -> None:
    frames, rest = _sse_split(b"data: a\n\ndata: b\n\ndata: c")
    assert frames == [b"data: a", b"data: b"]
    assert rest == b"data: c"


def test_sse_split_handles_crlf_separator() -> None:
    frames, rest = _sse_split(b"data: a\r\n\r\ndata: b")
    assert frames == [b"data: a"]
    assert rest == b"data: b"


# ---------------------------------------------------------------------------
# Sync StreamingResponse — Content-Type taxonomy
# ---------------------------------------------------------------------------

def _open_stream(chunks: list[bytes], content_type: str) -> StreamingResponse:
    client = httpx.Client(transport=_stream_body(chunks, content_type=content_type))
    return StreamingResponse(client, "GET", "http://test/stream", {})


def test_sse_happy_path_yields_one_event_per_frame() -> None:
    chunks = [
        b'data: {"i": 0}\n\n',
        b'data: {"i": 1}\n\n',
        b'data: {"i": 2}\n\n',
    ]
    with _open_stream(chunks, "text/event-stream") as r:
        assert r.status_code == 200
        events = list(r.iter_events())
    assert [e.kind for e in events] == ["sse", "sse", "sse"]
    assert [e.parsed for e in events] == [{"i": 0}, {"i": 1}, {"i": 2}]


def test_sse_done_terminates_iteration_after_yielding_sentinel() -> None:
    chunks = [
        b'data: {"i": 0}\n\n',
        b"data: [DONE]\n\n",
        b'data: {"never": "yielded"}\n\n',  # arrives after [DONE]
    ]
    with _open_stream(chunks, "text/event-stream") as r:
        events = list(r.iter_events())
    assert [e.kind for e in events] == ["sse", "done"]


def test_sse_reassembles_frame_split_across_iter_bytes_chunks() -> None:
    """The dominant SSE-client bug: ``data:`` line split mid-frame."""
    payload = b'data: {"hello": "world"}\n\n'
    # Split the payload at byte 7 — mid-JSON, mid-frame.
    chunks = [payload[:7], payload[7:14], payload[14:]]
    with _open_stream(chunks, "text/event-stream") as r:
        events = list(r.iter_events())
    assert len(events) == 1
    assert events[0].kind == "sse"
    assert events[0].parsed == {"hello": "world"}


def test_ndjson_yields_one_event_per_line() -> None:
    chunks = [b'{"i": 0}\n{"i": 1}\n', b'{"i": 2}\n']
    with _open_stream(chunks, "application/x-ndjson") as r:
        events = list(r.iter_events())
    assert [e.kind for e in events] == ["ndjson", "ndjson", "ndjson"]
    assert [e.parsed for e in events] == [{"i": 0}, {"i": 1}, {"i": 2}]


def test_text_plain_yields_line_events() -> None:
    chunks = [b"hello\nworld\n"]
    with _open_stream(chunks, "text/plain") as r:
        events = list(r.iter_events())
    assert [e.kind for e in events] == ["line", "line"]
    assert [e.text for e in events] == ["hello", "world"]


def test_unknown_content_type_falls_back_to_bytes() -> None:
    chunks = [b"\x00\x01\x02", b"\x03\x04"]
    with _open_stream(chunks, "application/octet-stream") as r:
        events = list(r.iter_events())
    assert [e.kind for e in events] == ["bytes", "bytes"]
    assert [e.raw for e in events] == chunks


def test_status_and_headers_available_before_iteration() -> None:
    with _open_stream([b"data: {}\n\n"], "text/event-stream") as r:
        assert r.status_code == 200
        assert r.headers.get("content-type") == "text/event-stream"


def test_response_property_raises_outside_context() -> None:
    r = _open_stream([b""], "text/event-stream")
    with pytest.raises(RuntimeError):
        _ = r.response


# ---------------------------------------------------------------------------
# Mid-stream errors surface to the caller
# ---------------------------------------------------------------------------

class _ExplodingStream(httpx.SyncByteStream):
    """Yields one chunk, then raises — simulating a dropped connection."""

    def __iter__(self) -> Iterable[bytes]:
        yield b'data: {"i": 0}\n\n'
        raise httpx.ReadError("connection dropped")

    def close(self) -> None:
        return None


def test_mid_stream_error_propagates() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ExplodingStream(),
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    r = StreamingResponse(client, "GET", "http://test/stream", {})
    with r:
        it = r.iter_events()
        first = next(it)
        assert first.parsed == {"i": 0}
        with pytest.raises(httpx.ReadError):
            next(it)


# ---------------------------------------------------------------------------
# Async sibling — minimal coverage to prove the surface works
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_sse_happy_path_and_done() -> None:
    chunks = [b'data: {"i": 0}\n\n', b"data: [DONE]\n\n"]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ByteStream(chunks),
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    r = AsyncStreamingResponse(client, "GET", "http://test/stream", {})
    async with r:
        kinds: list[str] = []
        parsed: list = []
        async for event in r.iter_events():
            kinds.append(event.kind)
            parsed.append(event.parsed)
    assert kinds == ["sse", "done"]
    assert parsed[0] == {"i": 0}


@pytest.mark.asyncio
async def test_async_ndjson() -> None:
    chunks = [b'{"i": 0}\n{"i": 1}\n']

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/x-ndjson"},
            stream=_ByteStream(chunks),
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    r = AsyncStreamingResponse(client, "GET", "http://test/stream", {})
    async with r:
        parsed: list = []
        async for event in r.iter_events():
            parsed.append(event.parsed)
    assert parsed == [{"i": 0}, {"i": 1}]
