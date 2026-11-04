"""Tests for :mod:`unitysvc.attachments` (unitysvc#2883): building a post's
files against the platform's limits, and saving a received one safely."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from unitysvc import attachments


def test_a_file_becomes_a_base64_entry_under_its_name(tmp_path: Path) -> None:
    (tmp_path / "shot.png").write_bytes(b"\x89PNG data")
    [entry] = attachments.prepare([tmp_path / "shot.png"])
    assert entry == {"base64": base64.b64encode(b"\x89PNG data").decode(), "filename": "shot.png"}


def test_urls_are_links_and_built_entries_pass_through() -> None:
    entries = attachments.prepare(["https://example.com/a.pdf", attachments.from_bytes(b"hi", "note.txt")])
    assert entries == [{"url": "https://example.com/a.pdf"}, {"base64": "aGk=", "filename": "note.txt"}]
    with pytest.raises(ValueError, match="http"):
        attachments.from_url("file:///etc/passwd")


def test_the_platform_limits_are_checked_before_upload(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(attachments, "MAX_FILE_BYTES", 10)
    monkeypatch.setattr(attachments, "MAX_MESSAGE_BYTES", 15)
    with pytest.raises(ValueError, match="at most"):
        attachments.from_bytes(b"x" * 11, "big.bin")
    with pytest.raises(ValueError, match="total"):
        attachments.prepare([attachments.from_bytes(b"x" * 8, "a"), attachments.from_bytes(b"x" * 8, "b")])
    with pytest.raises(ValueError, match="at most 10 attachments"):
        attachments.prepare([attachments.from_bytes(b"x", str(i)) for i in range(11)])
    with pytest.raises(ValueError, match="not a file"):
        attachments.from_path(tmp_path / "missing.png")


def test_received_names_cannot_escape_the_directory() -> None:
    for hostile in ("../../.ssh/authorized_keys", "..\\evil\x1b[31m.exe", "/etc/passwd", "C:\\x", ".bashrc"):
        name = attachments.safe_filename(hostile)
        assert not any(sep in name for sep in "/\\:") and "\x1b" not in name
        assert not name.startswith(".")
    assert attachments.safe_filename(None) == "attachment"


@pytest.mark.asyncio
@respx.mock
async def test_save_downloads_without_credentials_and_never_overwrites(tmp_path: Path) -> None:
    route = respx.get("https://s3.example/shot").mock(return_value=httpx.Response(200, content=b"PNG"))
    entry = {"filename": "../shot.png", "url": "https://s3.example/shot"}
    first = await attachments.save(entry, tmp_path)
    second = await attachments.save(entry, tmp_path)

    assert first == tmp_path / "_shot.png" and first.read_bytes() == b"PNG"
    assert second == tmp_path / "_shot (1).png"
    assert "authorization" not in route.calls[0].request.headers


@pytest.mark.asyncio
@respx.mock
async def test_save_refuses_expired_files_and_leaves_no_partial_download(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    with pytest.raises(ValueError, match="no longer available"):
        await attachments.save({"filename": "a", "url": "https://s3.example/a", "expired": True}, tmp_path)
    with pytest.raises(ValueError, match="no longer available"):
        await attachments.save({"filename": "a", "url": "data:text/html,hi"}, tmp_path)

    monkeypatch.setattr(attachments, "MAX_FILE_BYTES", 4)
    respx.get("https://s3.example/big").mock(return_value=httpx.Response(200, content=b"x" * 10))
    with pytest.raises(ValueError, match="larger"):
        await attachments.save({"filename": "big", "url": "https://s3.example/big"}, tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.asyncio
@respx.mock
async def test_concurrent_saves_of_one_name_both_keep_their_files(tmp_path: Path) -> None:
    """The review's probe: two saves of the same name at once, interleaved
    (each response arrives after the other request has started). The name is
    reserved before the download, so each gets its own file and neither's
    cleanup can remove the other's."""
    import asyncio

    def slow(content: bytes) -> Any:
        async def respond(request: httpx.Request) -> httpx.Response:
            await asyncio.sleep(0.01)  # both requests are now in flight
            return httpx.Response(200, content=content)

        return respond

    respx.get("https://s3.example/a").mock(side_effect=slow(b"A"))
    respx.get("https://s3.example/b").mock(side_effect=slow(b"B"))
    first, second = await asyncio.gather(
        attachments.save({"filename": "shot.png", "url": "https://s3.example/a"}, tmp_path),
        attachments.save({"filename": "shot.png", "url": "https://s3.example/b"}, tmp_path),
    )
    assert first != second
    assert sorted(p.read_bytes() for p in tmp_path.iterdir()) == [b"A", b"B"]


@pytest.mark.asyncio
@respx.mock
async def test_a_failed_save_removes_only_its_own_file(tmp_path: Path) -> None:
    """A file another writer creates while this request is in flight survives
    this call failing: only the file this call created is removed."""

    def other_writer_then_refuse(request: httpx.Request) -> httpx.Response:
        # Another save takes the first free name, as save() itself does.
        for name in ("shot.png", "shot (1).png"):
            try:
                with (tmp_path / name).open("xb") as out:
                    out.write(b"someone else's")
                break
            except FileExistsError:
                continue
        return httpx.Response(403)

    respx.get("https://s3.example/gone").mock(side_effect=other_writer_then_refuse)
    with pytest.raises(httpx.HTTPStatusError):
        await attachments.save({"filename": "shot.png", "url": "https://s3.example/gone"}, tmp_path)
    [survivor] = list(tmp_path.iterdir())
    assert survivor.read_bytes() == b"someone else's"


def test_a_message_needs_text_or_a_file() -> None:
    """A URL is kept as a link: with blank text it alone is refused, as the
    platform refuses it (unitysvc#2893)."""
    url = attachments.from_url("https://example.com/spec.pdf")
    with pytest.raises(ValueError, match="URL alone needs text"):
        attachments.check_content("  ", [url])
    attachments.check_content("the spec", [url])
    attachments.check_content("", [attachments.from_bytes(b"hi", "a.txt"), url])
