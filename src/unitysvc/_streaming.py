"""Streaming-response primitives for ``Services.stream`` / ``Groups.stream``.

Provides lazy iteration over HTTP response bodies — SSE, NDJSON, plain
lines, or raw bytes — selected by ``Content-Type``. Sibling to the
buffered :meth:`dispatch` path; same auth and interface resolution,
but ``httpx.Client.stream()`` instead of ``request()`` so the caller
sees chunks as they arrive.

The dominant use case is LLM SSE streaming (``data: {...}\\n\\n``
frames terminated by ``data: [DONE]``); the same surface handles
NDJSON and arbitrary binary streams.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


__all__ = [
    "StreamEvent",
    "StreamingResponse",
    "AsyncStreamingResponse",
]


@dataclass
class StreamEvent:
    """One frame from a streaming response body.

    Attributes:
        kind: ``"sse"`` | ``"ndjson"`` | ``"line"`` | ``"bytes"`` | ``"done"``.
            See :meth:`StreamingResponse.iter_events` for the taxonomy.
        parsed: JSON-decoded payload for ``"sse"`` / ``"ndjson"``, else ``None``.
        raw: The raw bytes of this frame (the full SSE frame for
            ``"sse"``, the line including delimiter-stripped bytes for
            ``"ndjson"`` / ``"line"``, or the chunk for ``"bytes"``).
        text: Decoded UTF-8 text for ``"line"`` events; ``None`` otherwise.
    """

    kind: str
    parsed: Any = None
    raw: bytes = b""
    text: str | None = None


# ---------------------------------------------------------------------------
# Content-type dispatch
# ---------------------------------------------------------------------------

def _classify(content_type: str) -> str:
    """Map a ``Content-Type`` header to an iter_events strategy.

    Returns one of ``"sse"`` / ``"ndjson"`` / ``"line"`` / ``"bytes"``.
    Unknown / missing types fall back to ``"bytes"`` per the spec.
    """
    ct = (content_type or "").split(";", 1)[0].strip().lower()
    if ct == "text/event-stream":
        return "sse"
    if ct in ("application/x-ndjson", "application/jsonl", "application/ndjson"):
        return "ndjson"
    if ct.startswith("text/"):
        return "line"
    return "bytes"


# ---------------------------------------------------------------------------
# SSE frame parsing
# ---------------------------------------------------------------------------

def _parse_sse_frame(frame: bytes) -> StreamEvent | None:
    """Parse one SSE frame (bytes between ``\\n\\n`` separators).

    Joins all ``data:`` lines with ``\\n`` per the SSE spec, then
    attempts JSON decode. Returns ``None`` for frames with no
    ``data:`` lines (comment-only / heartbeat frames).
    """
    text = frame.replace(b"\r\n", b"\n").replace(b"\r", b"\n").decode("utf-8", errors="replace")
    data_parts: list[str] = []
    for line in text.split("\n"):
        if line.startswith(":"):
            # SSE comment / heartbeat — ignore.
            continue
        if line.startswith("data:"):
            data_parts.append(line[5:].lstrip(" "))
        elif line == "data":
            data_parts.append("")
    if not data_parts:
        return None
    payload = "\n".join(data_parts)
    if payload.strip() == "[DONE]":
        return StreamEvent(kind="done", parsed=None, raw=b"[DONE]")
    try:
        parsed: Any = json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        parsed = payload
    return StreamEvent(kind="sse", parsed=parsed, raw=frame)


def _sse_split(buffer: bytes) -> tuple[list[bytes], bytes]:
    """Split an SSE buffer into complete frames and a remainder.

    Frames are separated by ``\\n\\n`` (or ``\\r\\n\\r\\n``). Anything
    after the final separator stays in the remainder for the next
    chunk to complete.
    """
    # Normalize CRLF separators to LF so we only need one search pattern.
    norm = buffer.replace(b"\r\n", b"\n")
    frames: list[bytes] = []
    while b"\n\n" in norm:
        frame, norm = norm.split(b"\n\n", 1)
        frames.append(frame)
    return frames, norm


# ---------------------------------------------------------------------------
# Sync streaming response
# ---------------------------------------------------------------------------

class StreamingResponse:
    """Sync context-managed wrapper around an ``httpx.Response`` stream.

    Created by :meth:`Services.stream` / :meth:`Groups.stream`. Opens
    the underlying ``httpx.Client.stream()`` on ``__enter__`` and
    closes it on ``__exit__``. Status/headers are available before
    iteration; the body is consumed lazily by ``iter_events`` /
    ``iter_bytes`` / ``iter_lines``.
    """

    __slots__ = ("_httpx_client", "_method", "_url", "_kwargs", "_cm", "_response")

    def __init__(
        self,
        httpx_client: httpx.Client,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> None:
        self._httpx_client = httpx_client
        self._method = method
        self._url = url
        self._kwargs = kwargs
        self._cm: Any = None
        self._response: httpx.Response | None = None

    def __enter__(self) -> StreamingResponse:
        self._cm = self._httpx_client.stream(self._method, self._url, **self._kwargs)
        self._response = self._cm.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> Any:
        cm = self._cm
        self._cm = None
        self._response = None
        if cm is None:
            return None
        return cm.__exit__(exc_type, exc, tb)

    @property
    def response(self) -> httpx.Response:
        """The underlying ``httpx.Response``. Only valid inside the ``with`` block."""
        if self._response is None:
            raise RuntimeError("StreamingResponse is only valid inside its `with` block.")
        return self._response

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def headers(self) -> httpx.Headers:
        return self.response.headers

    def iter_bytes(self, chunk_size: int | None = None) -> Iterator[bytes]:
        """Yield raw body chunks as they arrive."""
        yield from self.response.iter_bytes(chunk_size)

    def iter_lines(self) -> Iterator[str]:
        """Yield ``\\n``-delimited decoded text lines."""
        yield from self.response.iter_lines()

    def iter_events(self) -> Iterator[StreamEvent]:
        """Yield :class:`StreamEvent` objects, discriminated by ``Content-Type``.

        - ``text/event-stream`` → ``"sse"`` per frame, ``"done"`` on
          ``data: [DONE]``. Frames split across TCP chunks are
          reassembled before yielding.
        - ``application/x-ndjson`` / ``application/jsonl`` → ``"ndjson"`` per line.
        - ``text/*`` → ``"line"`` per line (text in ``event.text``).
        - anything else → ``"bytes"`` per chunk.
        """
        strategy = _classify(self.response.headers.get("content-type", ""))
        if strategy == "sse":
            yield from self._iter_sse()
        elif strategy == "ndjson":
            yield from self._iter_ndjson()
        elif strategy == "line":
            for line in self.response.iter_lines():
                yield StreamEvent(kind="line", parsed=None, raw=line.encode("utf-8"), text=line)
        else:
            for chunk in self.response.iter_bytes():
                yield StreamEvent(kind="bytes", parsed=None, raw=chunk)

    def _iter_sse(self) -> Iterator[StreamEvent]:
        buffer = b""
        for chunk in self.response.iter_bytes():
            if not chunk:
                continue
            buffer += chunk
            frames, buffer = _sse_split(buffer)
            for frame in frames:
                event = _parse_sse_frame(frame)
                if event is None:
                    continue
                yield event
                if event.kind == "done":
                    return
        if buffer.strip():
            event = _parse_sse_frame(buffer)
            if event is not None:
                yield event

    def _iter_ndjson(self) -> Iterator[StreamEvent]:
        for line in self.response.iter_lines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed: Any = json.loads(stripped)
            except (json.JSONDecodeError, ValueError):
                parsed = None
            yield StreamEvent(kind="ndjson", parsed=parsed, raw=stripped.encode("utf-8"))


# ---------------------------------------------------------------------------
# Async streaming response
# ---------------------------------------------------------------------------

class AsyncStreamingResponse:
    """Async sibling of :class:`StreamingResponse`. ``async with`` to enter."""

    __slots__ = ("_httpx_client", "_method", "_url", "_kwargs", "_cm", "_response")

    def __init__(
        self,
        httpx_client: httpx.AsyncClient,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> None:
        self._httpx_client = httpx_client
        self._method = method
        self._url = url
        self._kwargs = kwargs
        self._cm: Any = None
        self._response: httpx.Response | None = None

    async def __aenter__(self) -> AsyncStreamingResponse:
        self._cm = self._httpx_client.stream(self._method, self._url, **self._kwargs)
        self._response = await self._cm.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> Any:
        cm = self._cm
        self._cm = None
        self._response = None
        if cm is None:
            return None
        return await cm.__aexit__(exc_type, exc, tb)

    @property
    def response(self) -> httpx.Response:
        if self._response is None:
            raise RuntimeError("AsyncStreamingResponse is only valid inside its `async with` block.")
        return self._response

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def headers(self) -> httpx.Headers:
        return self.response.headers

    async def iter_bytes(self, chunk_size: int | None = None) -> AsyncIterator[bytes]:
        async for chunk in self.response.aiter_bytes(chunk_size):
            yield chunk

    async def iter_lines(self) -> AsyncIterator[str]:
        async for line in self.response.aiter_lines():
            yield line

    async def iter_events(self) -> AsyncIterator[StreamEvent]:
        """Async sibling of :meth:`StreamingResponse.iter_events`."""
        strategy = _classify(self.response.headers.get("content-type", ""))
        if strategy == "sse":
            async for event in self._iter_sse():
                yield event
        elif strategy == "ndjson":
            async for event in self._iter_ndjson():
                yield event
        elif strategy == "line":
            async for line in self.response.aiter_lines():
                yield StreamEvent(kind="line", parsed=None, raw=line.encode("utf-8"), text=line)
        else:
            async for chunk in self.response.aiter_bytes():
                yield StreamEvent(kind="bytes", parsed=None, raw=chunk)

    async def _iter_sse(self) -> AsyncIterator[StreamEvent]:
        buffer = b""
        async for chunk in self.response.aiter_bytes():
            if not chunk:
                continue
            buffer += chunk
            frames, buffer = _sse_split(buffer)
            for frame in frames:
                event = _parse_sse_frame(frame)
                if event is None:
                    continue
                yield event
                if event.kind == "done":
                    return
        if buffer.strip():
            event = _parse_sse_frame(buffer)
            if event is not None:
                yield event

    async def _iter_ndjson(self) -> AsyncIterator[StreamEvent]:
        async for line in self.response.aiter_lines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed: Any = json.loads(stripped)
            except (json.JSONDecodeError, ValueError):
                parsed = None
            yield StreamEvent(kind="ndjson", parsed=parsed, raw=stripped.encode("utf-8"))


# ---------------------------------------------------------------------------
# Shared URL / kwargs builder
# ---------------------------------------------------------------------------

def build_stream_kwargs(
    *,
    token: str | None,
    base_url: str | None,
    path: str,
    json: Any,
    data: Any,
    headers: dict[str, str] | None,
    timeout: float | None,
) -> tuple[str, dict[str, Any]]:
    """Compose ``(url, kwargs)`` for ``httpx_client.stream(...)``.

    Mirrors the request shape used by :func:`unitysvc.groups._http_dispatch`
    so the streaming path stays consistent with buffered dispatch
    (auth header, URL composition, body selection).
    """
    if not base_url:
        raise ValueError(
            "Interface has no resolved base_url; cannot stream. "
            "Check that the gateway is configured upstream."
        )
    url = base_url.rstrip("/")
    if path:
        url = f"{url}/{path.lstrip('/')}"

    merged_headers = dict(headers) if headers else {}
    if token:
        merged_headers.setdefault("Authorization", f"Bearer {token}")

    kwargs: dict[str, Any] = {"headers": merged_headers}
    if json is not None:
        kwargs["json"] = json
    elif data is not None:
        kwargs["content"] = data
    if timeout is not None:
        kwargs["timeout"] = timeout
    return url, kwargs
