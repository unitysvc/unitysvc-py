"""The interactive terminal around :class:`ChatSession` (prompt_toolkit line mode).

Messages scroll above a single input line, so the terminal's own scrollback,
search and copy keep working. A background task long-polls the account's
feed (every room over one request) and, now and then, refreshes the room list.
"""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any

import httpx
from rich.console import Console
from rich.text import Text

from ..exceptions import UnitysvcSDKError
from .session import FEED_WAIT_SECONDS, ChatError, ChatSession, RoomsClient, as_dict, clean

HELP = """\
Type a message and press Enter to post it to the open room (Esc then Enter adds a new line).
  /attach PATH       attach a file to your next message (Ctrl-V attaches a copied image or file)
  /drop              remove the attached files
  /save N [DIR]      download attachment N (as numbered) into DIR, default the current one
  /rooms             list rooms (● new activity, ⚑ follow-up)
  /open ROOM         switch room: number from /rooms, @handle, id or name prefix
  /next  (Ctrl-N)    open the next room with new activity
  /members           who is in this room
  /follow [off]      flag this room to revisit, or clear the flag
  /older  (/more)    show the messages before the earliest one shown
  /refresh           reload this room
  /help              this help
  /quit  (Ctrl-D)    leave the chat"""


async def _command(session: ChatSession, line: str) -> bool:
    """Run a slash command; False ends the chat."""
    name, _, arg = line[1:].partition(" ")
    arg = arg.strip()
    if name in ("quit", "exit", "q"):
        return False
    if name == "help":
        session.emit(Text(HELP))
    elif name == "rooms":
        await session.refresh_rooms()
        session.show_rooms()
    elif name in ("open", "switch"):
        if not arg:
            raise ChatError(f"Usage: /{name} ROOM")
        if not session.room_list:
            await session.refresh_rooms()
        await session.open(arg)
    elif name == "next":
        if not await session.next_with_activity():
            session.emit(Text("No other room has new activity", style="dim"))
    elif name == "attach":
        if not arg:
            raise ChatError("Usage: /attach PATH")
        session.attach_path(arg)
    elif name == "drop":
        session.drop()
    elif name == "save":
        number, _, directory = arg.partition(" ")
        if not number.isdigit():
            raise ChatError("Usage: /save N [DIR]")
        await session.save(int(number), directory.strip() or ".")
    elif name in ("older", "more"):
        await session.older()
    elif name == "refresh":
        if session.room:
            await session.open(str(session.room["id"]))
    elif name == "members":
        if session.room:
            for member in (await session.rooms.members(session.room["id"])).data:
                m = as_dict(member)
                role = f"{clean(m.get('account_type'))}, {clean(m.get('role'))}"
                session.emit(Text(f"  {clean(m.get('name'))}  ({role})"))
    elif name == "follow":
        if session.room:
            flag = arg.lower() not in ("off", "no", "clear")
            await session.rooms.set_follow_up(session.room["id"], flag)
            session.emit(Text("Flagged to follow up" if flag else "Follow-up cleared", style="dim"))
    else:
        raise ChatError(f"Unknown command /{clean(name)} (try /help)")
    return True


# A feed request that fails for any of these is retried after a pause: a
# timeout or a dropped connection must not stop the room from updating.
TRANSIENT = (UnitysvcSDKError, httpx.TransportError, OSError)
RETRY_SECONDS = 3.0


async def _watch(session: ChatSession, wait: float, rooms_interval: float) -> None:
    """Follow the feed, and now and then refresh the room list, until cancelled."""
    loop = asyncio.get_running_loop()
    refreshed = loop.time()
    while True:
        try:
            await session.follow(wait)
        except TRANSIENT:
            await asyncio.sleep(RETRY_SECONDS)
        if loop.time() - refreshed >= rooms_interval:
            refreshed = loop.time()
            with contextlib.suppress(*TRANSIENT):
                await session.refresh_rooms()


def paste_into(session: ChatSession) -> None:
    """Ctrl-V: attach the clipboard's image, or the files copied in a file
    manager, to the next message. Text is pasted with the terminal's own paste."""
    from .. import attachments
    from . import clipboard

    try:
        content = clipboard.read()
    except clipboard.ClipboardUnavailable as exc:
        session.emit(Text(str(exc), style="yellow"))
        return
    try:
        if content is None:
            session.emit(Text("No image or file in the clipboard (paste text with your terminal's paste)", style="dim"))
        elif isinstance(content, list):
            for path in content:
                session.attach_path(path)
        else:
            session.attach(attachments.from_bytes(content, "pasted-image.png"))
    except (ChatError, ValueError) as exc:
        session.emit(Text(str(exc), style="yellow"))


async def run_chat(
    rooms: RoomsClient,
    target: str | None = None,
    *,
    filters: dict[str, Any] | None = None,
    join_code: str | None = None,
    wait: float = FEED_WAIT_SECONDS,
    rooms_interval: float = 60.0,
    console: Console | None = None,
) -> None:
    """Open ``target`` (or the most recently active room) and chat until /quit."""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.patch_stdout import patch_stdout

    console = console or Console()
    session = ChatSession(rooms, emit=console.print)

    if join_code:
        joined = as_dict(await rooms.join(join_code))
        target = str(joined["id"])
    listed = await session.refresh_rooms(**(filters or {}))
    if target is None:
        if not listed:
            console.print("[yellow]No rooms found[/yellow]")
            return
        target = str(listed[0]["id"])
    if filters:
        await session.refresh_rooms()  # switching sees every room, not just the filtered ones
    await session.start_feed()  # before opening: nothing stored after the open is missed
    await session.open(target)
    console.print(Text("Type /help for commands.", style="dim"))

    bindings = KeyBindings()

    @bindings.add("c-n")
    def _(event: Any) -> None:
        event.app.exit(result="/next")

    @bindings.add("c-v")
    def _(event: Any) -> None:
        paste_into(session)

    @bindings.add("escape", "enter")
    def _(event: Any) -> None:
        event.current_buffer.insert_text("\n")

    def toolbar() -> str:
        room = session.room or {}
        others = session.others_with_activity()
        busy = f"  ·  {others} other room(s) with new activity (Ctrl-N)" if others else ""
        return f" {clean(room.get('name'))} @{clean(room.get('handle'))}{busy}"

    prompt: PromptSession[str] = PromptSession(
        key_bindings=bindings,
        bottom_toolbar=toolbar,
        refresh_interval=1.0,
        erase_when_done=True,
    )
    with patch_stdout(raw=True):
        poller = asyncio.create_task(_watch(session, wait, rooms_interval))
        try:
            while True:
                try:
                    line = await prompt.prompt_async("> ")
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    break
                try:
                    if line.startswith("/"):
                        if not await _command(session, line.strip()):
                            break
                    else:
                        await session.send(line)
                except ChatError as exc:
                    console.print(Text(str(exc), style="yellow"))
                except UnitysvcSDKError as exc:
                    console.print(Text(f"✗ {clean(exc)}", style="red"))
                except httpx.TransportError as exc:
                    console.print(Text(f"✗ Connection problem, try again: {clean(exc)}", style="red"))
        finally:
            poller.cancel()
            try:
                with contextlib.suppress(asyncio.CancelledError):
                    await poller
            finally:
                await session.close()  # recording what was seen, whatever the poller did
