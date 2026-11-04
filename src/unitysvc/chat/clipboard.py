"""What Ctrl-V attaches in the chat: an image, or files copied in a file manager.

macOS and Windows read the clipboard through Pillow (``ImageGrab``), which also
returns files copied in Finder or Explorer. Linux uses ``wl-paste`` (Wayland)
or ``xclip`` (X11) when installed. Over SSH the clipboard is the remote
machine's, so ``/attach PATH`` is the way to send a file there.
"""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
from typing import Any

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class ClipboardUnavailable(Exception):
    """This machine can't read images from the clipboard (says how to fix it)."""


def read() -> bytes | list[str] | None:
    """PNG bytes of a clipboard image, a list of copied file paths, or None
    when the clipboard holds neither."""
    if sys.platform in ("darwin", "win32"):
        return _read_with_pillow()
    return _read_on_linux()


def _read_with_pillow() -> bytes | list[str] | None:
    try:
        from PIL import ImageGrab
    except ImportError as exc:
        raise ClipboardUnavailable('Pasting images needs Pillow: pip install "unitysvc-py[chat]"') from exc
    grabbed: Any = ImageGrab.grabclipboard()
    if grabbed is None:
        return None
    if isinstance(grabbed, list):  # files copied in Finder or Explorer
        return [str(path) for path in grabbed]
    buffer = io.BytesIO()
    grabbed.save(buffer, format="PNG")
    return buffer.getvalue()


def _read_on_linux() -> bytes | None:
    commands = (
        ["wl-paste", "--no-newline", "--type", "image/png"],
        ["xclip", "-selection", "clipboard", "-target", "image/png", "-out"],
    )
    available = [command for command in commands if shutil.which(command[0])]
    if not available:
        raise ClipboardUnavailable("Pasting images needs wl-paste (Wayland) or xclip (X11); or use /attach PATH")
    for command in available:
        try:
            done = subprocess.run(command, capture_output=True, timeout=5, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if done.returncode == 0 and done.stdout.startswith(PNG_SIGNATURE):
            return done.stdout
    return None
