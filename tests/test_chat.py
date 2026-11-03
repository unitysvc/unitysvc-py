"""Tests for :mod:`unitysvc.chat` (unitysvc#2885 Phase 1).

A fake rooms client stands in for ``AsyncRooms``; the session's output is
collected as plain text.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from rich.text import Text

from unitysvc.chat import ChatError, ChatSession, format_message
from unitysvc.chat import session as chat_session
from unitysvc.exceptions import PermissionError as ForbiddenError

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
        self.readonly: set[str] = set()  # rooms that refuse posts
        self.fail_posts = 0
        self.capped = 0  # how many mark_active answers come back capped
        self.hold: dict[str, asyncio.Event] = {}  # forward reads of a room wait for its event

    async def list(self, **filters: Any) -> Any:
        self.calls.append(("list", filters))
        rooms = [{**room, "has_new_activity": room["id"] in self.activity} for room in (A, B)]
        return SimpleNamespace(data=rooms)

    async def get(
        self,
        target: str,
        *,
        after: int | None = None,
        limit: int = 50,
        tail: int | None = None,
        before: int | None = None,
    ) -> dict[str, Any]:
        self.calls.append(("get", target, after, tail) if before is None else ("get", target, after, tail, before))
        room = {"a": A, "b": B}[target]
        stored = self.messages[target]
        if tail is not None:
            # The server returns the latest N (below ``before``), resuming after its
            # stored bound, with ``previous`` (its oldest offset) when the page is full.
            below = [m for m in stored if before is None or m["offset"] < before]
            data = below[-tail:]
            page = {
                "data": data,
                "next": stored[-1]["offset"] if stored else None,
                "previous": data[0]["offset"] if len(data) >= tail else None,
            }
        else:
            if target in self.hold:
                await self.hold[target].wait()
            newer = [m for m in stored if after is None or m["offset"] > after][:limit]
            page = {"data": newer, "next": newer[-1]["offset"] if newer else after}
        return {**room, "last_active_offset": self.last_active[target], "messages": page}

    async def post(self, target: str, *, body: str, fallback: bool = True, **message: Any) -> dict[str, Any]:
        self.calls.append(("post", target, body, message["client_message_id"], fallback))
        if self.fail_posts:
            self.fail_posts -= 1
            raise httpx.ConnectError("dropped")
        if target in self.readonly:
            assert fallback is False, "a chat post must never fall back to me"
            raise ForbiddenError("You can't post in this room", status_code=403)
        return {"room_id": target, "message_id": "new", "offset": 99, "routed": "room_id"}

    async def mark_active(self, target: str, offset: int) -> dict[str, Any]:
        self.calls.append(("active", target, offset))
        if self.capped:
            self.capped -= 1
            return {"last_active_offset": offset - 1, "capped": True}
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
async def test_open_reads_only_the_latest_messages() -> None:
    many = [_msg(i, f"m{i}") for i in range(5000)]
    rooms = FakeRooms({"a": many, "b": []}, {"a": None, "b": None})
    session, out = _session(rooms)
    session.history = 5
    await session.open("a")

    assert [call for call in rooms.calls if call[0] == "get"] == [("get", "a", None, 5)]
    shown = [line for line in out if "] alice" in line]
    assert [line.rsplit(" ", 1)[-1] for line in shown] == [f"m{i}" for i in range(4995, 5000)]
    assert session.cursor == 4999


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
    # Polls never record activity (#2877): a terminal left open keeps it new...
    assert ("active", "a", 2) not in rooms.calls
    # ...until the room stops being shown.
    await session.close()
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
    assert all(post[4] is False for post in posts)  # never the me fallback
    assert sum("you  hello" in line for line in out) == 1
    # The stored copy arriving later is not shown twice.
    rooms.messages["a"].append({**_msg(3, "hello", sender=ME), "id": "new"})
    out.clear()
    await session.poll()
    assert out == []


@pytest.mark.asyncio
async def test_a_room_that_cannot_take_the_post_is_an_error_not_a_me_post() -> None:
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    rooms.readonly = {"a"}
    session, out = _session(rooms)
    await session.open("a")
    out.clear()
    with pytest.raises(ChatError, match="can't post"):
        await session.send("hello")
    assert out == []  # nothing echoed as posted


@pytest.mark.asyncio
async def test_a_capped_mark_on_open_is_retried_once(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    monkeypatch.setattr(chat_session, "MARK_RETRY_SECONDS", 0)
    rooms = FakeRooms({"a": [_msg(7, "hi")], "b": []}, {"a": None, "b": None})
    rooms.capped = 1
    session, _ = _session(rooms)
    await session.open("a")
    await asyncio.sleep(0.01)
    assert [call for call in rooms.calls if call[0] == "active"] == [("active", "a", 7), ("active", "a", 7)]
    assert session.marked == 7


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


@pytest.mark.asyncio
async def test_a_poll_in_flight_across_a_switch_is_discarded() -> None:
    """A poll of A answered after /open B must not show A's message in B, nor
    move B's cursor or read marker past B's own messages."""
    rooms = FakeRooms({"a": [_msg(1, "a1")], "b": [_msg(10, "b10")]}, {"a": 1, "b": None})
    session, out = _session(rooms)
    await session.open("a")
    rooms.messages["a"].append(_msg(900, "a900"))
    rooms.hold["a"] = asyncio.Event()
    poll = asyncio.create_task(session.poll())
    await asyncio.sleep(0)  # the poll is now waiting on A's answer

    await session.open("b")
    rooms.hold["a"].set()
    assert await poll == 0

    assert "a900" not in "\n".join(out)
    assert session.cursor == 10 and session.seen == 10
    await session.close()
    assert not any(call[:2] == ("active", "b") and call[2] > 10 for call in rooms.calls)


@pytest.mark.asyncio
async def test_older_pages_back_to_the_start_of_the_conversation() -> None:
    rooms = FakeRooms({"a": [_msg(i, f"m{i}") for i in range(120)], "b": []}, {"a": 119, "b": None})
    session, out = _session(rooms)
    await session.open("a")  # the latest 50: 70..119
    assert session.previous == 70

    assert await session.older() == 50  # 20..69
    assert ("get", "a", None, 50, 70) in rooms.calls
    assert await session.older() == 20  # 0..19: a short page, nothing older
    assert session.previous is None
    assert "start of the stored conversation" in out[-1]
    assert await session.older() == 0
    assert out[-1] == "No older messages"

    bodies = [line.rsplit(" ", 1)[-1] for line in out if "] alice" in line]
    assert sorted(bodies, key=lambda body: int(body[1:])) == [f"m{i}" for i in range(120)]
    assert session.cursor == 119  # paging back never moves the forward cursor


@pytest.mark.asyncio
async def test_the_watcher_keeps_polling_after_a_transport_failure() -> None:
    from unitysvc.chat.terminal import _watch

    polls = 0

    class Flaky:
        async def poll(self) -> int:
            nonlocal polls
            polls += 1
            if polls == 1:
                raise httpx.ReadTimeout("slow")
            return 0

        async def refresh_rooms(self) -> list[Any]:
            raise httpx.ConnectError("down")

    watcher = asyncio.create_task(_watch(Flaky(), 0.001, 0.002))  # type: ignore[arg-type]
    while polls < 4:
        await asyncio.sleep(0.005)
    assert not watcher.done()
    watcher.cancel()


@pytest.mark.asyncio
async def test_terminal_older_shows_history_before_the_latest() -> None:
    """With 60 stored messages the chat opens at 11-60; /older shows 1-10."""
    import io

    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput
    from rich.console import Console

    from unitysvc.chat import run_chat

    rooms = FakeRooms({"a": [_msg(i, f"m{i}") for i in range(1, 61)], "b": []}, {"a": 60, "b": None})
    buffer = io.StringIO()
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        pipe.send_text("/older\r/quit\r")
        await run_chat(rooms, "a", interval=60, console=Console(file=buffer, width=120))

    text = buffer.getvalue()
    assert "Unknown command" not in text
    assert "alice  m1\n" in text and "10 earlier message(s)" in text
    assert "start of the stored conversation" in text
