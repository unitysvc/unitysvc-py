"""The interactive terminal around :class:`ChatSession` (prompt_toolkit line mode).

Messages scroll above a single input line, so the terminal's own scrollback,
search and copy keep working. A background task polls the open room and,
less often, the room list for activity elsewhere.
"""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any

from rich.console import Console
from rich.text import Text

from ..exceptions import UnitysvcSDKError
from .session import ChatError, ChatSession, RoomsClient, as_dict, clean

HELP = """\
Type a message and press Enter to post it to the open room (Esc then Enter adds a new line).
  /rooms             list rooms (● new activity, ⚑ follow-up)
  /open ROOM         switch room: number from /rooms, @handle, id or name prefix
  /next  (Ctrl-N)    open the next room with new activity
  /members           who is in this room
  /follow [off]      flag this room to revisit, or clear the flag
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


async def run_chat(
    rooms: RoomsClient,
    target: str | None = None,
    *,
    filters: dict[str, Any] | None = None,
    join_code: str | None = None,
    interval: float = 3.0,
    rooms_interval: float = 30.0,
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
    await session.open(target)
    console.print(Text("Type /help for commands.", style="dim"))

    bindings = KeyBindings()

    @bindings.add("c-n")
    def _(event: Any) -> None:
        event.app.exit(result="/next")

    @bindings.add("escape", "enter")
    def _(event: Any) -> None:
        event.current_buffer.insert_text("\n")

    def toolbar() -> str:
        room = session.room or {}
        others = session.others_with_activity()
        busy = f"  ·  {others} other room(s) with new activity (Ctrl-N)" if others else ""
        return f" {clean(room.get('name'))} @{clean(room.get('handle'))}{busy}"

    async def watch() -> None:
        elapsed = 0.0
        while True:
            await asyncio.sleep(interval)
            elapsed += interval
            with contextlib.suppress(UnitysvcSDKError, OSError):
                await session.poll()
                if elapsed >= rooms_interval:
                    elapsed = 0.0
                    await session.refresh_rooms()

    prompt: PromptSession[str] = PromptSession(
        key_bindings=bindings,
        bottom_toolbar=toolbar,
        refresh_interval=1.0,
        erase_when_done=True,
    )
    with patch_stdout(raw=True):
        poller = asyncio.create_task(watch())
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
        finally:
            poller.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await poller
            await session.close()
