"""The terminal chat state machine, independent of any terminal library.

``ChatSession`` drives an ``AsyncRooms``-shaped client (customer or seller,
see :class:`RoomsClient`) and hands rendered lines to an ``emit`` callback,
so it can be tested without a terminal and reused by every CLI that has a
rooms client.

Messages are user content from other accounts: everything shown is built as
literal :class:`rich.text.Text` after control characters (including ANSI
escape sequences) are stripped, never as markup.
"""

from __future__ import annotations

import re
import uuid
from collections import deque
from collections.abc import Callable
from datetime import datetime
from typing import Any, Protocol

import httpx
from rich.text import Text

from ..exceptions import UnitysvcSDKError

# Everything a terminal could act on except newline and tab.
_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
# History is oldest-first, so opening a room reads forward to its end.
PAGE = 200


class RoomsClient(Protocol):
    """The part of ``AsyncRooms`` the chat uses (customer and seller both match)."""

    async def list(self, *, kind: str | None = ..., enrollment: Any = ..., service: Any = ...) -> Any: ...
    async def get(self, target: str, *, after: int | None = ..., limit: int = ...) -> Any: ...
    async def post(self, target: str | None = ..., *, body: str, **message: Any) -> Any: ...
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
        self.seen: int | None = None  # highest offset shown in this room
        self.marked: int | None = None  # last offset the server accepted as seen
        self.shown_ids: set[str] = set()

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
        view = as_dict(await self.rooms.get(target, limit=PAGE))
        page = view.get("messages") or {}
        messages: deque[dict[str, Any]] = deque(page.get("data") or [], maxlen=self.history)
        cursor = page.get("next")
        while len(page.get("data") or []) >= PAGE:
            page = as_dict(await self.rooms.get(target, after=cursor, limit=PAGE)).get("messages") or {}
            messages.extend(page.get("data") or [])
            cursor = _next(page, cursor)

        self.room = {key: value for key, value in view.items() if key != "messages"}
        self.cursor, self.seen, self.marked, self.shown_ids = cursor, None, view.get("last_active_offset"), set()
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
        await self.mark_seen()

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
        """Show messages stored since the last read; return how many were new."""
        if self.room is None:
            return 0
        shown = 0
        while True:
            page = as_dict(await self.rooms.get(self.room["id"], after=self.cursor, limit=PAGE)).get("messages") or {}
            data = page.get("data") or []
            for message in data:
                if str(message.get("id")) not in self.shown_ids:
                    shown += 1
                self._show(message)
            self.cursor = _next(page, self.cursor)
            if len(data) < PAGE:
                break
        if shown:
            await self.mark_seen()
        return shown

    async def mark_seen(self) -> None:
        """Tell the server how far this person has seen the open room; a
        ``capped`` answer (storage behind) is retried on the next call."""
        if self.room is None or self.seen is None or (self.marked is not None and self.seen <= self.marked):
            return
        try:
            marked = as_dict(await self.rooms.mark_active(self.room["id"], self.seen))
        except UnitysvcSDKError:
            return  # best effort: the next poll or switch tries again
        self.marked = marked.get("last_active_offset")

    async def send(self, text: str) -> None:
        """Post to the open room, never anywhere else."""
        if self.room is None:
            raise ChatError("No room is open; use /rooms and /open")
        body = text.strip()
        if not body:
            return
        client_message_id = str(uuid.uuid4())
        try:
            posted = as_dict(await self.rooms.post(self.room["id"], body=body, client_message_id=client_message_id))
        except httpx.TransportError:  # a dropped connection: the same id posts at most once
            posted = as_dict(await self.rooms.post(self.room["id"], body=body, client_message_id=client_message_id))
        if str(posted.get("room_id")) != str(self.room["id"]):
            # The API falls back to the account's ``me`` room when it can't post here.
            reason = clean(posted.get("reason")) or "you can't post in this room"
            raise ChatError(f"Not posted here ({reason}); the server put it in your me room instead")
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
        await self.mark_seen()
