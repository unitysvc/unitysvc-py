"""Files for room messages (unitysvc#2883): build what ``rooms.post`` sends, and
save what other members sent.

A post carries msg-format entries: ``{"base64", "filename"}`` for a file, which
the platform stores for 7 days, or ``{"url", "filename"}``, which it keeps as a
link. The platform sniffs each file's type from its bytes and refuses what it
doesn't accept; the size and count limits are also checked here so a large
file fails before it is encoded and uploaded.

A received attachment is ``{"filename", "mime_type", "size", "url", "expired"}``,
where ``url`` is a short-lived signed link. Another member chose its name and
bytes: :func:`save` writes it under a cleaned name in a directory you choose
and never opens it.
"""

from __future__ import annotations

import base64
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any, BinaryIO

import httpx

# The platform's limits (backend ``room_attachments``).
MAX_FILES = 10
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_MESSAGE_BYTES = 25 * 1024 * 1024

_UNSAFE = re.compile(r"[\x00-\x1f\x7f/\\:]+")


def from_bytes(data: bytes, filename: str) -> dict[str, Any]:
    """An attachment of ``data`` named ``filename``."""
    if len(data) > MAX_FILE_BYTES:
        raise ValueError(f"{filename} is {_mib(len(data))}; a file may be at most {_mib(MAX_FILE_BYTES)}")
    return {"base64": base64.b64encode(data).decode("ascii"), "filename": filename, "size": len(data)}


def from_path(path: str | Path) -> dict[str, Any]:
    """An attachment of the file at ``path``, under its own name."""
    file = Path(path).expanduser()
    if not file.is_file():
        raise ValueError(f"{path} is not a file")
    size = file.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError(f"{file.name} is {_mib(size)}; a file may be at most {_mib(MAX_FILE_BYTES)}")
    return from_bytes(file.read_bytes(), file.name)


def from_url(url: str, filename: str | None = None) -> dict[str, Any]:
    """A link the platform keeps with the message (it doesn't fetch it)."""
    if not url.startswith(("https://", "http://")):
        raise ValueError("A URL attachment must be http(s)")
    return {"url": url} if filename is None else {"url": url, "filename": filename}


def prepare(items: Iterable[Any]) -> list[dict[str, Any]]:
    """The ``attachments`` of a post, from paths, ``http(s)`` URLs or entries
    already built, checked against the per-message limits."""
    entries: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            entries.append(dict(item))
        elif isinstance(item, str) and item.startswith(("https://", "http://")):
            entries.append(from_url(item))
        else:
            entries.append(from_path(item))
    if len(entries) > MAX_FILES:
        raise ValueError(f"A message may carry at most {MAX_FILES} attachments")
    total = sum(entry.get("size") or 0 for entry in entries)
    if total > MAX_MESSAGE_BYTES:
        raise ValueError(f"Attachments total {_mib(total)}; a message may carry at most {_mib(MAX_MESSAGE_BYTES)}")
    # ``size`` is only for these checks: the platform measures the bytes itself.
    return [{key: value for key, value in entry.items() if key != "size"} for entry in entries]


def safe_filename(name: Any, default: str = "attachment") -> str:
    """A received file's name, made safe to write: no directories, control
    characters or leading dots."""
    cleaned = _UNSAFE.sub("_", str(name or "")).strip().lstrip(".")
    return cleaned[:200] or default


async def save(attachment: dict[str, Any], directory: str | Path = ".") -> Path:
    """Download a received attachment into ``directory`` and return its path.
    The signed URL needs no credentials, and none are sent. An existing file is
    never overwritten: a numbered name is used instead."""
    url = str(attachment.get("url") or "")
    if attachment.get("expired") or not url.startswith(("https://", "http://")):
        raise ValueError("This attachment is no longer available")
    folder = Path(directory).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    # Reserve the name before downloading: the exclusive create claims it, so
    # a concurrent save picks the next number, and on failure only the file
    # this call created is removed.
    target, out = _reserve(folder / safe_filename(attachment.get("filename")))
    try:
        with out:
            async with httpx.AsyncClient(timeout=60, follow_redirects=False) as http:
                async with http.stream("GET", url) as response:
                    response.raise_for_status()
                    written = 0
                    async for chunk in response.aiter_bytes():
                        written += len(chunk)
                        if written > MAX_FILE_BYTES:
                            raise ValueError("The download is larger than an attachment can be")
                        out.write(chunk)
    except BaseException:
        target.unlink(missing_ok=True)  # ours, created above: no partial file left
        raise
    return target


def _reserve(path: Path) -> tuple[Path, BinaryIO]:
    """Create ``path``, or the first free ``name (N).ext``, exclusively."""
    candidate, n = path, 1
    while True:
        try:
            return candidate, candidate.open("xb")
        except FileExistsError:
            candidate = path.with_name(f"{path.stem} ({n}){path.suffix}")
            n += 1


def _mib(size: int) -> str:
    return f"{size / (1024 * 1024):.1f} MiB"
