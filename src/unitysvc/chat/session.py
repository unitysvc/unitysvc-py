"""The terminal chat state machine, independent of any terminal library.

``ChatSession`` drives an ``AsyncRooms``-shaped client (customer or seller,
see :class:`RoomsClient`) and hands rendered lines to an ``emit`` callback,
so it can be tested without a terminal and reused by every CLI that has a
rooms client.

What the person has seen is recorded the way the web inbox does it (#2877):
when a room opens, through the newest message loaded, and when it stops
being shown (a switch or quitting), through the newest message shown. Polls
never record anything, so a terminal left open doesn't clear new activity.

Messages are user content from other accounts: everything shown is built as
literal :class:`rich.text.Text` after control characters (including ANSI
escape sequences) are stripped, never as markup.
"""

from __future__ import annotations

import asyncio
import re
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any, Protocol

import httpx
from rich.text import Text

from ..exceptions import NotFoundError, UnitysvcSDKError
from ..exceptions import PermissionError as ForbiddenError

# Everything a terminal could act on except newline and tab.
_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
PAGE = 200
# ``mark_active`` caps at what ``rooms-deliver`` has recorded so far; retry a
# capped mark once, as the web inbox does.
MARK_RETRY_SECONDS = 4.0


class RoomsClient(Protocol):
    """The part of ``AsyncRooms`` the chat uses (customer and seller both match)."""

    async def list(self, *, kind: str | None = ..., enrollment: Any = ..., service: Any = ...) -> Any: ...
    async def get(
        self,
        target: str,
        *,
        after: int | None = ...,
        limit: int = ...,
        tail: int | None = ...,
        before: int | None = ...,
    ) -> Any: ...
    async def post(self, target: str | None = ..., *, body: str, fallback: bool = ..., **message: Any) -> Any: ...
    async def mark_active(self, target: str, offset: int) -> Any: ...
    async def members(self, target: str) -> Any: ...
    async def set_follow_up(self, target: str, follow_up: bool = ...) -> Any: ...
    async def join(self, token: str) -> Any: ...


class ChatError(Exception):
    """A problem to show the person, not a crash (unknown room, misrouted post)."""


def as_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return dict(obj.__dict__)


def clean(value: Any) -> str:
    """Remote text made safe for a terminal."""
    return _CONTROL.sub("", "" if value is None else str(value))


def _next(page: dict[str, Any], cursor: int | None) -> int | None:
    """The page's resume offset, keeping the old one when the page has none."""
    return cursor if page.get("next") is None else page["next"]


def _clock(sent_at: Any, today: datetime | None = None) -> str:
    try:
        sent = datetime.fromisoformat(str(sent_at)).astimezone()
    except ValueError:
        return clean(sent_at)[:16]
    today = today or datetime.now().astimezone()
    return sent.strftime("%H:%M" if sent.date() == today.date() else "%b %d %H:%M")


def format_message(message: dict[str, Any], my_member_id: Any = None) -> Text:
    """One message as a literal line: ``[10:02] alice  body``."""
    mine = my_member_id is not None and str(message.get("sender_member_id")) == str(my_member_id)
    line = Text()
    line.append(f"[{_clock(message.get('sent_at'))}] ", style="dim")
    if message.get("is_system"):
        line.append(clean(message.get("body")), style="dim italic")
        return line
    line.append(f"{'you' if mine else clean(message.get('sender_name')) or '?'}  ", style="cyan" if mine else "bold")
    if message.get("title"):
        line.append(clean(message["title"]), style="bold")
        line.append("\n")
    line.append(clean(message.get("body")))
    for attachment in message.get("attachments") or []:
        size = attachment.get("size")
        line.append(f"\n  [attachment] {clean(attachment.get('filename'))}", style="magenta")
        if size:
            line.append(f" ({int(size) // 1024 or 1} KB)", style="dim")
    return line


def room_line(index: int, room: dict[str, Any], current: bool = False) -> Text:
    """A row of ``/rooms``: number, activity dot, follow-up flag, kind, name, handle."""
    line = Text()
    line.append(f"{index:>3} ", style="dim")
    line.append("● " if room.get("has_new_activity") else "  ", style="yellow")
    line.append("⚑ " if room.get("follow_up") else "  ", style="red")
    line.append(f"{clean(room.get('kind')):<9}", style="dim")
    line.append(clean(room.get("name")), style="bold reverse" if current else "bold")
    line.append(f"  @{clean(room.get('handle'))}", style="dim")
    return line


class ChatSession:
    """One person in one room at a time, switching between the account's rooms."""

    def __init__(
        self,
        rooms: RoomsClient,
        *,
        emit: Callable[[Text | str], None],
        history: int = 50,
    ) -> None:
        self.rooms = rooms
        self.emit = emit
        self.history = history
        self.room_list: list[dict[str, Any]] = []
        self.room: dict[str, Any] | None = None
        self.cursor: int | None = None  # resume reading with after=cursor
        self.previous: int | None = None  # read older history with before=previous
        self.seen: int | None = None  # highest offset shown in this room
        self.marked: int | None = None  # last offset the server accepted as seen
        self.shown_ids: set[str] = set()
        self._retry: asyncio.Task[None] | None = None
        # Bumped whenever the open room changes: a read that was in flight
        # across a switch belongs to the room before it and is discarded.
        self._generation = 0

    # ---- rooms -------------------------------------------------------------

    async def refresh_rooms(self, **filters: Any) -> list[dict[str, Any]]:
        listed = await self.rooms.list(**filters)
        self.room_list = [as_dict(room) for room in listed.data]
        return self.room_list

    def others_with_activity(self) -> int:
        current = self.room and self.room["id"]
        return sum(1 for room in self.room_list if room.get("has_new_activity") and room.get("id") != current)

    def resolve(self, query: str) -> str:
        """A room id from a number in the last ``/rooms`` list, an id, a handle
        (with or without ``@``) or a unique name prefix. Unknown values are
        passed through so the server can resolve ids and handles it knows."""
        query = query.strip().removeprefix("@")
        if query.isdigit() and 1 <= int(query) <= len(self.room_list):
            return str(self.room_list[int(query) - 1]["id"])
        for room in self.room_list:
            if query in (str(room.get("id")), room.get("handle")):
                return str(room["id"])
        matches = [room for room in self.room_list if str(room.get("name", "")).lower().startswith(query.lower())]
        if len(matches) == 1:
            return str(matches[0]["id"])
        if len(matches) > 1:
            names = ", ".join(f"@{clean(room.get('handle'))}" for room in matches)
            raise ChatError(f"'{clean(query)}' matches several rooms: {names}")
        return query

    def show_rooms(self) -> None:
        if not self.room_list:
            self.emit(Text("No rooms", style="dim"))
        current = self.room and self.room["id"]
        for index, room in enumerate(self.room_list, 1):
            self.emit(room_line(index, room, room.get("id") == current))

    # ---- open / switch -----------------------------------------------------

    async def open(self, query: str) -> None:
        """Leave the current room (recording what was seen) and show the end of another."""
        target = self.resolve(query)
        await self.mark_seen()
        self._generation += 1  # a poll of the room being left is now stale
        # One request: the latest messages, whose ``next`` resumes with newer ones.
        view = as_dict(await self.rooms.get(target, tail=min(self.history, PAGE)))
        page = view.get("messages") or {}
        messages = page.get("data") or []

        self._generation += 1  # and so is one that started while this was loading
        self.room = {key: value for key, value in view.items() if key != "messages"}
        self.cursor, self.previous = page.get("next"), page.get("previous")
        self.seen, self.marked, self.shown_ids = None, view.get("last_active_offset"), set()
        self._header()
        last_seen = self.marked
        divided = last_seen is None
        for message in messages:
            if not divided and message.get("offset", -1) > last_seen:
                self.emit(Text("─ new since your last visit ─", style="yellow"))
                divided = True
            self._show(message)
        if not messages:
            self.emit(Text("No messages yet", style="dim"))
        await self.mark_seen(retry=True)

    def _header(self) -> None:
        room = self.room or {}
        head = Text()
        head.append(f"── {clean(room.get('name'))} ", style="bold")
        details = f"{clean(room.get('kind'))} · @{clean(room.get('handle'))} · {clean(room.get('role'))}"
        head.append(f"({details})", style="dim")
        self.emit(head)
        if room.get("status") == "readonly" and room.get("role") in ("member", "readonly"):
            self.emit(Text("This room is read-only for you.", style="yellow"))

    def _show(self, message: dict[str, Any]) -> None:
        message_id = str(message.get("id"))
        offset = message.get("offset")
        if isinstance(offset, int):
            self.seen = offset if self.seen is None else max(self.seen, offset)
        if message_id in self.shown_ids:
            return
        self.shown_ids.add(message_id)
        self.emit(format_message(message, (self.room or {}).get("member_id")))

    # ---- live --------------------------------------------------------------

    async def poll(self) -> int:
        """Show messages stored since the last read; return how many were new.
        Records nothing as seen (that happens on open, switch and quit)."""
        if self.room is None:
            return 0
        shown = 0
        while True:
            generation = self._generation
            page = as_dict(await self.rooms.get(self.room["id"], after=self.cursor, limit=PAGE)).get("messages") or {}
            if generation != self._generation:
                return shown  # the room changed while reading: not this room's messages
            data = page.get("data") or []
            for message in data:
                if str(message.get("id")) not in self.shown_ids:
                    shown += 1
                self._show(message)
            self.cursor = _next(page, self.cursor)
            if len(data) < PAGE:
                break
        return shown

    async def older(self) -> int:
        """Show the messages before the earliest one loaded; return how many.
        A scrolling terminal can't insert above, so they print below, framed."""
        if self.room is None:
            raise ChatError("No room is open; use /rooms and /open")
        if self.previous is None:
            self.emit(Text("No older messages", style="dim"))
            return 0
        generation, size = self._generation, min(self.history, PAGE)
        view = as_dict(await self.rooms.get(self.room["id"], tail=size, before=self.previous))
        if generation != self._generation:
            return 0
        page = view.get("messages") or {}
        messages = page.get("data") or []
        self.previous = page.get("previous")
        self.emit(Text(f"── {len(messages)} earlier message(s) ──", style="yellow"))
        shown = 0
        for message in messages:
            if str(message.get("id")) not in self.shown_ids:
                shown += 1
                self._show(message)
        end = "── start of the stored conversation ──" if self.previous is None else "── /older for more ──"
        self.emit(Text(end, style="yellow"))
        return shown

    async def mark_seen(self, *, retry: bool = False) -> None:
        """Record that the open room has been seen through the newest message
        shown. Called on open (``retry``: once more after a ``capped`` answer)
        and when the room stops being shown; best effort."""
        if self._retry is not None:
            self._retry.cancel()
            self._retry = None
        if self.room is None or self.seen is None or (self.marked is not None and self.seen <= self.marked):
            return
        room_id, offset = str(self.room["id"]), self.seen
        try:
            marked = as_dict(await self.rooms.mark_active(room_id, offset))
        except (UnitysvcSDKError, httpx.TransportError):  # best effort
            return
        self.marked = marked.get("last_active_offset")
        if retry and marked.get("capped"):
            self._retry = asyncio.create_task(self._mark_again(room_id, offset))

    async def _mark_again(self, room_id: str, offset: int) -> None:
        await asyncio.sleep(MARK_RETRY_SECONDS)
        if self.room is None or str(self.room["id"]) != room_id:
            return
        try:
            marked = as_dict(await self.rooms.mark_active(room_id, offset))
        except (UnitysvcSDKError, httpx.TransportError):  # best effort
            return
        self.marked = marked.get("last_active_offset")

    async def send(self, text: str) -> None:
        """Post to the open room, never anywhere else."""
        if self.room is None:
            raise ChatError("No room is open; use /rooms and /open")
        body = text.strip()
        if not body:
            return
        client_message_id = str(uuid.uuid4())
        # ``fallback=False``: a room that can't take the post is an error, never
        # a post to the account's ``me`` room.
        room_id = str(self.room["id"])

        async def post() -> dict[str, Any]:
            return as_dict(
                await self.rooms.post(room_id, body=body, client_message_id=client_message_id, fallback=False)
            )

        try:
            try:
                posted = await post()
            except httpx.TransportError:  # a dropped connection: the same id posts at most once
                posted = await post()
        except ForbiddenError as exc:
            raise ChatError("Not posted: you can't post in this room") from exc
        except NotFoundError as exc:
            raise ChatError("Not posted: this room is no longer reachable") from exc
        message_id = str(posted.get("message_id"))
        self.shown_ids.add(message_id)
        now = datetime.now().astimezone().isoformat()
        member_id = self.room.get("member_id")
        self.emit(format_message({"sender_member_id": member_id, "sent_at": now, "body": body}, member_id))

    async def next_with_activity(self) -> bool:
        """Open the next room with unseen activity (a helpdesk queue); False if none."""
        await self.refresh_rooms()
        current = self.room and self.room["id"]
        for room in self.room_list:
            if room.get("has_new_activity") and room.get("id") != current:
                await self.open(str(room["id"]))
                return True
        return False

    async def close(self) -> None:
        """Quitting stops showing the room: record what was seen."""
        await self.mark_seen()
