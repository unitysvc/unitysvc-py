"""Tests for :mod:`unitysvc.chat` (unitysvc#2885).

A fake rooms client stands in for ``AsyncRooms``: rooms' stored messages, and a
feed over everything ``deliver``ed (a log; its cursor is a position in it).
The session's output is collected as plain text.
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
from unitysvc.exceptions import ValidationError

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
        self.log: list[dict[str, Any]] = []  # what the feed has seen stored, in order
        self.feed_hold: asyncio.Event | None = None  # a feed request waits for it
        self.can_post: dict[str, bool] = {"a": True, "b": True}
        self.posted_files: list[Any] = []
        self.refuse_files = False

    def deliver(self, room_id: str, message: dict[str, Any]) -> None:
        """A message stored in a room: history and the feed both see it."""
        self.messages[room_id].append(message)
        self.log.append({**message, "room_id": room_id})
        self.activity.add(room_id)

    async def list(self, **filters: Any) -> Any:
        self.calls.append(("list", filters))
        rooms = [
            {**room, "has_new_activity": room["id"] in self.activity, "can_post": self.can_post[room["id"]]}
            for room in (A, B)
        ]
        if filters.get("new_activity"):
            rooms = [room for room in rooms if room["has_new_activity"]]
        return SimpleNamespace(data=rooms)

    async def feed(self, *, since: str | None = None, wait: float = 0, limit: int = 100) -> dict[str, Any]:
        self.calls.append(("feed", since, wait))
        if since == "bad":
            raise ValidationError("Invalid cursor", status_code=400)
        start = len(self.log) if since is None else int(since)
        if self.feed_hold is not None:
            await self.feed_hold.wait()
        elif start >= len(self.log) and wait > 0:
            await asyncio.sleep(min(wait, 0.01))  # a long-poll with nothing new
        new = self.log[start : start + limit]
        return {"messages": new, "cursor": str(start + len(new)), "rooms_with_new_activity": len(self.activity)}

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
            newer = [m for m in stored if after is None or m["offset"] > after][:limit]
            page = {"data": newer, "next": newer[-1]["offset"] if newer else after}
        return {**room, "last_active_offset": self.last_active[target], "messages": page}

    async def post(self, target: str, *, body: str, fallback: bool = True, **message: Any) -> dict[str, Any]:
        self.calls.append(("post", target, body, message["client_message_id"], fallback))
        self.posted_files.append(message.get("attachments"))
        if self.refuse_files and message.get("attachments"):
            raise ValidationError("This file type isn't accepted", status_code=422)
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


@pytest.mark.asyncio
async def test_the_feed_shows_only_new_messages_of_the_open_room() -> None:
    rooms = FakeRooms({"a": [_msg(1, "hi")], "b": []}, {"a": 1, "b": None})
    session, out = _session(rooms)
    await session.start_feed()
    await session.open("a")
    out.clear()

    assert await session.follow(wait=0) == 0
    rooms.deliver("a", _msg(2, "any update?"))
    assert await session.follow(wait=0) == 1
    assert any("any update?" in line for line in out)
    assert await session.follow(wait=0) == 0  # the cursor moved past it
    # The feed never records activity (#2877): a terminal left open keeps it new...
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
    # The stored copy arriving later through the feed is not shown twice.
    rooms.deliver("a", {**_msg(3, "hello", sender=ME), "id": "new"})
    out.clear()
    await session.follow(wait=0)
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
    assert ("list", {"new_activity": True}) in rooms.calls  # the server picks the queue
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
        await run_chat(rooms, "a", wait=0.01, console=Console(file=buffer, width=120))

    text = buffer.getvalue()
    assert any(call[:3] == ("post", "a", "hello") for call in rooms.calls)
    assert "help!" in text and "Unknown command /bogus" in text
    assert ("active", "b", 2) in rooms.calls


@pytest.mark.asyncio
async def test_a_feed_answer_that_spans_a_switch_shows_the_new_rooms_message_once() -> None:
    """A feed request started in A and answered after /open B is applied to B:
    a B message that came with B's history and again in the feed shows once."""
    rooms = FakeRooms({"a": [_msg(1, "a1")], "b": [_msg(10, "b10")]}, {"a": 1, "b": None})
    session, out = _session(rooms)
    await session.start_feed()
    await session.open("a")
    rooms.feed_hold = asyncio.Event()
    waiting = asyncio.create_task(session.follow(wait=5))
    await asyncio.sleep(0)  # the request is now waiting

    rooms.deliver("b", _msg(11, "b11"))  # stored before B's history is read
    await session.open("b")
    rooms.feed_hold.set()
    assert await waiting == 0  # b11 already came with B's history
    assert sum("b11" in line for line in out) == 1
    rooms.feed_hold = None
    assert await session.follow(wait=0) == 0  # the cursor moved past it


@pytest.mark.asyncio
async def test_a_feed_answer_during_the_history_load_is_kept_for_the_new_room() -> None:
    """The review's probe: B's history is slow; a B message stored after B's
    history snapshot arrives in a feed answer that completes while B is still
    loading. It must show in B once B is open, not be dropped."""
    rooms = FakeRooms({"a": [_msg(1, "a1")], "b": [_msg(10, "b10")]}, {"a": 1, "b": None})
    session, out = _session(rooms)
    await session.start_feed()
    await session.open("a")

    history_read = asyncio.Event()
    release_history = asyncio.Event()
    original_get = rooms.get

    async def slow_get(target: str, **kwargs: Any) -> dict[str, Any]:
        view = await original_get(target, **kwargs)  # B's snapshot: b10 only
        if target == "b":
            history_read.set()
            await release_history.wait()
        return view

    rooms.get = slow_get  # type: ignore[method-assign]
    opening = asyncio.create_task(session.open("b"))
    await history_read.wait()
    rooms.deliver("b", _msg(11, "b11"))  # stored after the snapshot
    following = asyncio.create_task(session.follow(wait=0))  # answered while B loads
    await asyncio.sleep(0.01)
    assert not following.done()  # held until the switch finishes

    release_history.set()
    await opening
    assert await following == 1
    assert sum("b11" in line for line in out) == 1
    assert await session.follow(wait=0) == 0


@pytest.mark.asyncio
async def test_activity_elsewhere_refreshes_the_room_list() -> None:
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    session, out = _session(rooms)
    await session.start_feed()
    await session.refresh_rooms()
    await session.open("a")
    assert session.others_with_activity() == 0

    rooms.deliver("b", _msg(5, "help!"))
    assert await session.follow(wait=0) == 0  # not the open room: not shown
    assert "help!" not in "\n".join(out)
    assert session.others_with_activity() == 1  # the toolbar's count, from a fresh list


@pytest.mark.asyncio
async def test_an_invalid_feed_position_starts_again_at_the_end() -> None:
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    session, _ = _session(rooms)
    session.feed_cursor = "bad"
    assert await session.follow(wait=0) == 0
    assert session.feed_cursor == "0"  # a fresh position, no backlog


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


@pytest.mark.asyncio
async def test_the_watcher_keeps_following_after_a_transport_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from unitysvc.chat import terminal
    from unitysvc.chat.terminal import _watch

    monkeypatch.setattr(terminal, "RETRY_SECONDS", 0.001)
    polls = 0

    class Flaky:
        async def follow(self, wait: float) -> int:
            nonlocal polls
            polls += 1
            if polls == 1:
                raise httpx.ReadTimeout("slow")
            await asyncio.sleep(0.001)
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
        await run_chat(rooms, "a", wait=0.01, console=Console(file=buffer, width=120))

    text = buffer.getvalue()
    assert "Unknown command" not in text
    assert "alice  m1\n" in text and "10 earlier message(s)" in text
    assert "start of the stored conversation" in text


def test_room_rows_show_the_last_sender_and_read_only_rooms() -> None:
    from unitysvc.chat.session import room_line

    row = room_line(1, {**A, "last_sender_name": "alice", "can_post": True}).plain
    assert "· alice" in row and "read-only" not in row
    row = room_line(2, {**B, "sent_latest_message": True, "last_sender_name": "x", "can_post": False}).plain
    assert "· you" in row and "(read-only)" in row


def test_attachments_link_only_http_urls() -> None:
    line = format_message(
        {
            "sender_name": "alice",
            "body": "see attached",
            "sent_at": "2026-11-03T10:00:00+00:00",
            "attachments": [
                {"filename": "shot.png", "mime_type": "image/png", "size": 2048, "url": "https://s3.example/shot"},
                {"filename": "evil.html", "url": "data:text/html;base64,PHNjcmlwdD4="},
                {"filename": "old.pdf", "url": "https://s3.example/old", "expired": True},
                {"base64": "aGk=", "note": "not kept: too large"},
            ],
        }
    ).plain
    assert "[attachment] shot.png (image/png, 2 KB) https://s3.example/shot" in line
    assert "data:" not in line and "aGk=" not in line
    assert "[attachment] evil.html" in line
    assert "old.pdf" in line and "expired" in line and "https://s3.example/old" not in line
    assert "[attachment] file (not kept: too large)" in line


@pytest.mark.asyncio
async def test_the_header_says_when_you_cannot_post() -> None:
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    rooms.can_post["a"] = False
    session, out = _session(rooms)
    await session.refresh_rooms()
    await session.open("a")
    assert "You can't post in this room." in out


@pytest.mark.asyncio
async def test_attached_files_go_with_the_next_post_then_clear(tmp_path: Any) -> None:
    (tmp_path / "shot.png").write_bytes(b"\x89PNG")
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    session, out = _session(rooms)
    await session.open("a")
    session.attach_path(str(tmp_path / "shot.png"))
    assert any("[attached] shot.png" in line for line in out)

    await session.send("")  # files alone are a message
    [files] = rooms.posted_files
    assert [f["filename"] for f in files] == ["shot.png"]
    assert session.pending == []
    assert any("you  " in line and "[attachment] shot.png" in line for line in out)

    await session.send("")  # nothing left: nothing posted
    assert len(rooms.posted_files) == 1


@pytest.mark.asyncio
async def test_a_refused_file_stays_attached_until_dropped(tmp_path: Any) -> None:
    (tmp_path / "x.exe").write_bytes(b"MZ")
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    rooms.refuse_files = True
    session, out = _session(rooms)
    await session.open("a")
    session.attach_path(str(tmp_path / "x.exe"))
    with pytest.raises(ChatError, match="isn't accepted.*/drop"):
        await session.send("here")
    assert len(session.pending) == 1
    session.drop()
    assert session.pending == [] and "Removed 1 attached file(s)" in out


@pytest.mark.asyncio
async def test_attaching_past_the_limits_is_refused_before_upload(monkeypatch: pytest.MonkeyPatch) -> None:
    from unitysvc import attachments

    monkeypatch.setattr(attachments, "MAX_MESSAGE_BYTES", 5)
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    session, _ = _session(rooms)
    session.attach(attachments.from_bytes(b"1234", "a"))
    with pytest.raises(ChatError, match="total"):
        session.attach(attachments.from_bytes(b"1234", "b"))
    assert [entry["filename"] for entry in session.pending] == ["a"]


@pytest.mark.asyncio
async def test_save_numbers_attachments_and_refreshes_an_expired_link(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    from unitysvc import attachments

    file = {"filename": "shot.png", "mime_type": "image/png", "size": 3, "url": "https://s3.example/old"}
    message = {**_msg(5, "see this"), "attachments": [file]}
    rooms = FakeRooms({"a": [message], "b": []}, {"a": 5, "b": None})
    session, out = _session(rooms)
    await session.open("a")
    assert any("[attachment 1] shot.png" in line for line in out)

    fetched: list[str] = []

    async def fake_save(entry: dict[str, Any], directory: Any) -> Any:
        fetched.append(entry["url"])
        if entry["url"].endswith("/old"):  # signed for minutes: this one lapsed
            raise httpx.HTTPStatusError(
                "expired", request=httpx.Request("GET", entry["url"]), response=httpx.Response(403)
            )
        return tmp_path / "shot.png"

    monkeypatch.setattr(attachments, "save", fake_save)
    rooms.messages["a"][0] = {**message, "attachments": [{**file, "url": "https://s3.example/new"}]}
    await session.save(1, str(tmp_path))
    assert fetched == ["https://s3.example/old", "https://s3.example/new"]
    assert ("get", "a", 4, None) in rooms.calls  # reread just that message
    assert out[-1] == f"Saved {tmp_path / 'shot.png'}"
    with pytest.raises(ChatError, match="No attachment 2"):
        await session.save(2)


def test_ctrl_v_attaches_an_image_or_copied_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    from unitysvc.chat import clipboard
    from unitysvc.chat.terminal import paste_into

    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    session, out = _session(rooms)

    monkeypatch.setattr(clipboard, "read", lambda: clipboard.PNG_SIGNATURE + b"img")
    paste_into(session)
    assert [entry["filename"] for entry in session.pending] == ["pasted-image.png"]

    (tmp_path / "report.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(clipboard, "read", lambda: [str(tmp_path / "report.pdf")])
    paste_into(session)
    assert [entry["filename"] for entry in session.pending] == ["pasted-image.png", "report.pdf"]

    monkeypatch.setattr(clipboard, "read", lambda: None)
    paste_into(session)
    assert "No image or file in the clipboard" in out[-1]

    def unavailable() -> None:
        raise clipboard.ClipboardUnavailable("Pasting images needs wl-paste (Wayland) or xclip (X11)")

    monkeypatch.setattr(clipboard, "read", unavailable)
    paste_into(session)
    assert "xclip" in out[-1] and len(session.pending) == 2


@pytest.mark.asyncio
async def test_attached_files_stay_with_their_room() -> None:
    """The review's probe: a file attached in A must not go out with a message
    in B (/open or /next); it waits in A and is announced when A is back."""
    from unitysvc import attachments

    rooms = FakeRooms({"a": [], "b": [_msg(4, "help!")]}, {"a": None, "b": 2})
    session, out = _session(rooms)
    await session.refresh_rooms()
    await session.open("a")
    session.attach(attachments.from_bytes(b"private", "contract.pdf"))

    await session.open("b")
    assert any("1 attached file(s) stay with Acme support" in line for line in out)
    assert session.pending == []
    await session.send("on it")
    assert rooms.posted_files[-1] is None  # B's post carries no files

    rooms.activity = {"a"}
    out.clear()
    assert await session.next_with_activity() is True  # back to A through /next
    assert any("Attached here from before: contract.pdf" in line for line in out)
    await session.send("as promised")
    assert [f["filename"] for f in rooms.posted_files[-1]] == ["contract.pdf"]
    assert session.pending == []


@pytest.mark.asyncio
async def test_displayed_reply_acknowledges_personal_reading_and_retries_marker_lag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(chat_session, "MARK_RETRY_SECONDS", 0)
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    session, out = _session(rooms)
    await session.open("a")
    rooms.capped = 1
    await session.send("on it")
    assert any("on it" in line for line in out)
    await asyncio.sleep(0.01)
    assert [call for call in rooms.calls if call[0] == "active"] == [
        ("active", "a", 99), ("active", "a", 99),
    ]
    assert session.marked == 99
    await session.close()


@pytest.mark.asyncio
async def test_failed_reply_does_not_acknowledge_reading() -> None:
    rooms = FakeRooms({"a": [], "b": []}, {"a": None, "b": None})
    rooms.readonly.add("a")
    session, _ = _session(rooms)
    await session.open("a")
    with pytest.raises(ChatError):
        await session.send("on it")
    assert not [call for call in rooms.calls if call[0] == "active"]
