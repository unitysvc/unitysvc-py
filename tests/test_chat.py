"""Tests for :mod:`unitysvc.chat` (unitysvc#2885 Phase 1).

A fake rooms client stands in for ``AsyncRooms``; the session's output is
collected as plain text.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from rich.text import Text

from unitysvc.chat import ChatError, ChatSession, format_message
from unitysvc.chat.session import PAGE

ME = "m-me"
A = {"id": "a", "member_id": ME, "kind": "chat", "name": "Acme support", "handle": "acme", "role": "member"}
B = {"id": "b", "member_id": ME, "kind": "helpdesk", "name": "Helpdesk", "handle": "helpdesk", "role": "member"}


def _msg(offset: int, body: str, sender: str = "m-alice", name: str = "alice") -> dict[str, Any]:
    return {
        "id": f"id-{offset}",
        "offset": offset,
        "sent_at": "2026-11-03T10:00:00+00:00",
        "sender_member_id": sender,
        "sender_name": name,
        "body": body,
    }


class FakeRooms:
    def __init__(self, messages: dict[str, list[dict[str, Any]]], last_active: dict[str, int | None]) -> None:
        self.messages = messages
        self.last_active = last_active
        self.activity: set[str] = set()
        self.calls: list[tuple[Any, ...]] = []
        self.post_room: str | None = None  # where a post lands (None = the target)
        self.fail_posts = 0

    async def list(self, **filters: Any) -> Any:
        self.calls.append(("list", filters))
        rooms = [{**room, "has_new_activity": room["id"] in self.activity} for room in (A, B)]
        return SimpleNamespace(data=rooms)

    async def get(self, target: str, *, after: int | None = None, limit: int = 50) -> dict[str, Any]:
        self.calls.append(("get", target, after))
        room = {"a": A, "b": B}[target]
        newer = [m for m in self.messages[target] if after is None or m["offset"] > after][:limit]
        next_offset = newer[-1]["offset"] if newer else after
        page = {"data": newer, "next": next_offset}
        return {**room, "last_active_offset": self.last_active[target], "messages": page}

    async def post(self, target: str, *, body: str, **message: Any) -> dict[str, Any]:
        self.calls.append(("post", target, body, message["client_message_id"]))
        if self.fail_posts:
            self.fail_posts -= 1
            raise httpx.ConnectError("dropped")
        landed = self.post_room or target
        return {"room_id": landed, "message_id": "new", "offset": 99, "routed": "room_id", "reason": "readonly"}

    async def mark_active(self, target: str, offset: int) -> dict[str, Any]:
        self.calls.append(("active", target, offset))
        self.last_active[target] = offset
        return {"last_active_offset": offset, "capped": False}


def _session(rooms: FakeRooms) -> tuple[ChatSession, list[str]]:
    out: list[str] = []
    session = ChatSession(rooms, emit=lambda line: out.append(line.plain if isinstance(line, Text) else line))
    return session, out


@pytest.mark.asyncio
async def test_open_shows_tail_with_divider_and_marks_seen() -> None:
    rooms = FakeRooms({"a": [_msg(1, "old"), _msg(5, "new one")], "b": []}, {"a": 1, "b": None})
    session, out = _session(rooms)
    await session.refresh_rooms()
    await session.open("@acme")

    text = "\n".join(out)
    assert text.index("old") < text.index("new since your last visit") < text.index("new one")
    assert ("active", "a", 5) in rooms.calls


@pytest.mark.asyncio
async def test_open_reads_forward_to_the_end_and_keeps_the_tail() -> None:
    many = [_msg(i, f"m{i}") for i in range(PAGE + 10)]
    rooms = FakeRooms({"a": many, "b": []}, {"a": None, "b": None})
    session, out = _session(rooms)
    session.history = 5
    await session.open("a")

    shown = [line for line in out if "] alice" in line]
    assert [line.rsplit(" ", 1)[-1] for line in shown] == [f"m{i}" for i in range(PAGE + 5, PAGE + 10)]
    assert session.cursor == PAGE + 9


@pytest.mark.asyncio
async def test_poll_shows_only_new_messages() -> None:
    rooms = FakeRooms({"a": [_msg(1, "hi")], "b": []}, {"a": 1, "b": None})
    session, out = _session(rooms)
    await session.open("a")
    out.clear()

    assert await session.poll() == 0
    rooms.messages["a"].append(_msg(2, "any update?"))
    assert await session.poll() == 1
    assert any("any update?" in line for line in out)
    assert ("active", "a", 2) in rooms.calls


@pytest.mark.asyncio
async def test_send_echoes_once_and_is_idempotent_on_retry() -> None:
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    rooms.fail_posts = 1
    session, out = _session(rooms)
    await session.open("a")
    await session.send("hello")

    posts = [call for call in rooms.calls if call[0] == "post"]
    assert len(posts) == 2 and posts[0][3] == posts[1][3]  # same client_message_id
    assert sum("you  hello" in line for line in out) == 1
    # The stored copy arriving later is not shown twice.
    rooms.messages["a"].append({**_msg(3, "hello", sender=ME), "id": "new"})
    out.clear()
    await session.poll()
    assert out == []


@pytest.mark.asyncio
async def test_send_refuses_a_post_that_landed_elsewhere() -> None:
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    rooms.post_room = "me-room"
    session, _ = _session(rooms)
    await session.open("a")
    with pytest.raises(ChatError, match="me room"):
        await session.send("hello")


@pytest.mark.asyncio
async def test_next_opens_another_room_with_activity() -> None:
    rooms = FakeRooms({"a": [], "b": [_msg(4, "help!")]}, {"a": None, "b": 2})
    session, out = _session(rooms)
    await session.open("a")
    assert await session.next_with_activity() is False

    rooms.activity = {"a", "b"}
    assert await session.next_with_activity() is True
    assert session.room and session.room["id"] == "b"
    assert any("help!" in line for line in out)


@pytest.mark.asyncio
async def test_resolve_by_number_handle_and_name_prefix() -> None:
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    session, _ = _session(rooms)
    await session.refresh_rooms()
    assert session.resolve("2") == "b"
    assert session.resolve("@acme") == "a"
    assert session.resolve("help") == "b"
    assert session.resolve("@unknown-handle") == "unknown-handle"  # left to the server


def test_remote_text_is_never_markup_or_escape_sequences() -> None:
    line = format_message(
        {"sender_name": "[bold]eve\x1b[31m", "body": "\x1b]0;pwned\x07[link=x]hi[/link]", "sent_at": "bad"}
    )
    assert "\x1b" not in line.plain and "\x07" not in line.plain
    assert "[bold]eve" in line.plain and "[link=x]hi[/link]" in line.plain


@pytest.mark.asyncio
async def test_terminal_loop_posts_switches_and_quits() -> None:
    """The real prompt_toolkit loop, fed through a pipe."""
    import io

    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput
    from rich.console import Console

    from unitysvc.chat import run_chat

    rooms = FakeRooms({"a": [_msg(1, "hi")], "b": [_msg(2, "help!")]}, {"a": 1, "b": None})
    buffer = io.StringIO()
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text("hello\r/open @helpdesk\r/bogus\r/quit\r")
        await run_chat(rooms, "a", interval=60, console=Console(file=buffer, width=120))

    text = buffer.getvalue()
    assert any(call[:3] == ("post", "a", "hello") for call in rooms.calls)
    assert "help!" in text and "Unknown command /bogus" in text
    assert ("active", "b", 2) in rooms.calls
