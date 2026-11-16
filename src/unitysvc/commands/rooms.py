"""``usvc rooms`` — rooms the account can reach, their messages and settings.

Mirrors :class:`unitysvc.arooms.AsyncRooms`. ``ROOM`` is a room id or one of
the account's handles (``me``, ``helpdesk``, or a room's own handle):

- ``usvc rooms list [--kind K] [--enrollment ID] [--service ID] [--name PREFIX] [--new] [--closed]``
- ``usvc rooms show ROOM [--after N] [--limit N]``   — the room and its messages
- ``usvc rooms post ROOM [TEXT] [--attach PATH ...] [--mention MEMBER ...] [--title T] [--id KEY]``
- ``usvc rooms members ROOM``
- ``usvc rooms commands [ROOM]`` — the ``!`` commands, or which you may send in ROOM now
- ``usvc rooms set ROOM [--name] [--description] [--retention S] [--status S]``
- ``usvc rooms delivery ROOM`` — the room's connectors for your account
- ``usvc rooms connector add|set|remove ROOM NAME [--notify S] [--email S] [--post S]``
- ``usvc rooms live status ROOM`` / ``waiting`` / ``accept`` / ``stop`` / ``request ROOM MEMBER`` /
  ``cancel ROOM MEMBER`` / ``resolve ROOM`` — live help (traffic light)
- ``usvc rooms work next`` / ``claim ROOM TOKEN`` / ``return-later ROOM`` / ``done ROOM OFFSET`` — the
  rooms waiting for your account, one at a time
- ``usvc rooms invite ROOM [--role R] [--max-uses N] [--expires-in-days N] [--note T]``
- ``usvc rooms invitations ROOM [--all]`` / ``revoke ROOM CODE_ID``
- ``usvc rooms join CODE`` / ``leave ROOM``
- ``usvc rooms chat [ROOM] [--enrollment ID] [--service ID] [--join CODE]`` — interactive

What the account may do is decided by the server from its role in the room.

Room names, descriptions and messages are user content: they are printed as
literal text, never as Rich markup, and ``--format json`` writes plain JSON to
stdout.
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table
from rich.text import Text

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_to_dict,
    run_async,
)

console = Console()

app = typer.Typer(help="Rooms: list, read, post, settings, delivery, live help and invitations.")
connector_app = typer.Typer(help="How a room reaches you: its named connectors (notify, email and post services).")
live_app = typer.Typer(help="Live help: accept requests, ask a room's member for help, see who is accepting.")
work_app = typer.Typer(help="The rooms waiting for your account, one at a time: next, claim, return-later, done.")
app.add_typer(connector_app, name="connector")
app.add_typer(live_app, name="live")
app.add_typer(work_app, name="work")

OFF = "off"


def _print_json(value: Any) -> None:
    """Plain JSON on stdout: no wrapping, no markup, safe to pipe and parse."""
    typer.echo(json.dumps(value, indent=2, default=str))


def _literal(value: Any) -> Text:
    """User content as a table cell, never interpreted as markup."""
    return Text("" if value is None else str(value))


def _rooms_table(rooms: list[dict[str, Any]]) -> None:
    table = Table(title="Rooms")
    for column, style in (("ID", "dim"), ("Kind", ""), ("Name", "bold"), ("Handle", ""), ("Role", ""), ("Status", "")):
        table.add_column(column, style=style or None)
    for room in rooms:
        table.add_row(*(_literal(room.get(key)) for key in ("id", "kind", "name", "handle", "role", "status")))
    console.print(table)


@app.command("list")
def list_rooms(
    kind: str | None = typer.Option(None, "--kind", help="Only rooms of this kind (chat, me, helpdesk)."),
    enrollment: str | None = typer.Option(None, "--enrollment", help="Only rooms of this enrollment."),
    service: str | None = typer.Option(None, "--service", help="Only rooms of this service (not its enrollments')."),
    name: str | None = typer.Option(None, "--name", help="Only rooms whose name starts with this (any case)."),
    new: bool = typer.Option(False, "--new", help="Only rooms with activity you haven't acknowledged."),
    closed: bool = typer.Option(
        False, "--closed", help="Also rooms you can't reach now (a paused enrollment), with their closed_reason."
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the rooms the account can reach, most recently active first."""
    narrow: dict[str, Any] = {}
    if name is not None:
        narrow["q"] = name
    if new:
        narrow["new_activity"] = True
    if closed:
        narrow["include_closed"] = True

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            listed = await client.rooms.list(kind=kind, enrollment=enrollment, service=service, **narrow)
            return [model_to_dict(room) for room in listed.data]

    rooms = run_async(_impl(), error_prefix="Failed to list rooms")
    if output_format == "json":
        _print_json(rooms)
    elif not rooms:
        console.print("[dim]No rooms found[/dim]")
    else:
        _rooms_table(rooms)


@app.command("show")
def show_room(
    room: str = typer.Argument(..., help="Room id or handle."),
    after: int | None = typer.Option(None, "--after", help="Resume after this offset (a previous page's next)."),
    limit: int = typer.Option(50, "--limit", help="Messages per page (at most 200)."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show a room and its messages, oldest first."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.get(room, after=after, limit=limit))

    view = run_async(_impl(), error_prefix="Failed to show room")
    if output_format == "json":
        _print_json(view)
        return
    console.print(
        f"[bold]{escape(str(view.get('name', '')))}[/bold]  "
        f"({escape(str(view.get('kind', '')))}, you are {escape(str(view.get('role', '')))})"
    )
    if view.get("description"):
        console.print(Text(str(view["description"])))
    messages = (view.get("messages") or {}).get("data") or []
    for message in messages:
        line = Text()
        line.append(f"{message.get('offset', '')} {message.get('sent_at', '')} ", style="dim")
        line.append(str(message.get("sender_name", "")), style="bold")
        line.append(f": {message.get('body', '')}")
        console.print(line)
    if not messages:
        console.print("[dim]No messages[/dim]")
    next_offset = (view.get("messages") or {}).get("next")
    if next_offset is not None:
        console.print(f"[dim]next: --after {next_offset}[/dim]")


@app.command("post")
def post_message(
    room: str = typer.Argument(..., help="Room id or handle."),
    text: str = typer.Argument("", help="Message body (optional with --attach)."),
    attach: list[str] | None = typer.Option(
        None, "--attach", "-a", help="A file to attach (stored 7 days) or an http(s) URL. Repeatable."
    ),
    mention: list[str] | None = typer.Option(
        None, "--mention", "-m", help="A member id the message calls for (the room then waits for them). Repeatable."
    ),
    title: str | None = typer.Option(None, "--title", help="Optional title."),
    client_message_id: str | None = typer.Option(
        None, "--id", help="Idempotency key: retrying with the same key posts once."
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Post a message to a room, with files if you like. A first line starting with ! runs a command."""
    if not text.strip() and not attach:
        console.print("[red]✗[/red] Give a message, --attach a file, or both")
        raise typer.Exit(code=1)
    message: dict[str, Any] = {}
    if attach:
        from ..attachments import check_content, prepare

        try:
            message["attachments"] = prepare(attach)
            check_content(text, message["attachments"])
        except ValueError as exc:
            console.print(f"[red]✗[/red] {escape(str(exc))}")
            raise typer.Exit(code=1) from exc
    if mention:
        message["mentions"] = mention
    if title is not None:
        message["title"] = title
    if client_message_id is not None:
        message["client_message_id"] = client_message_id

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.post(room, body=text, **message))

    posted = run_async(_impl(), error_prefix="Failed to post")
    console.print(
        f"[green]✓[/green] Posted to {escape(str(posted.get('room_id', room)))} at offset {posted.get('offset', '')}"
    )
    command = posted.get("command")
    if command:
        mark = "[green]✓[/green]" if command.get("status") == "executed" else "[yellow]![/yellow]"
        console.print(f"{mark} {escape(str(command.get('message', '')))}")


@app.command("members")
def list_members(
    room: str = typer.Argument(..., help="Room id or handle."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the room's members and their roles."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            return [model_to_dict(m) for m in (await client.rooms.members(room)).data]

    members = run_async(_impl(), error_prefix="Failed to list members")
    if output_format == "json":
        _print_json(members)
        return
    table = Table(title="Members")
    for column in ("Name", "Account", "Role", "Joined"):
        table.add_column(column)
    for m in members:
        table.add_row(*(_literal(m.get(key)) for key in ("name", "account_type", "role", "joined_at")))
    console.print(table)


@app.command("set")
def set_room(
    room: str = typer.Argument(..., help="Room id or handle."),
    name: str | None = typer.Option(None, "--name", help="New room name."),
    description: str | None = typer.Option(None, "--description", help="Markdown description; '' clears it."),
    retention: int | None = typer.Option(None, "--retention", help="Seconds to keep messages (0 = don't store)."),
    status: str | None = typer.Option(None, "--status", help="active | readonly (only owner and moderators post)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Change the room's settings (owner only)."""
    settings: dict[str, Any] = {
        key: value
        for key, value in (
            ("name", name),
            ("description", description),
            ("retention_seconds", retention),
            ("status", status),
        )
        if value is not None
    }
    if not settings:
        console.print("[yellow]Nothing to change[/yellow]")
        raise typer.Exit(code=1)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.update(room, **settings))

    updated = run_async(_impl(), error_prefix="Failed to change the room")
    console.print(f"[green]✓[/green] Updated {escape(str(updated.get('name', room)))}")


@app.command("commands")
def list_commands(
    room: str | None = typer.Argument(None, help="Room id or handle; without it, every command the platform knows."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """The ! commands: all of them, or which you may send in ROOM right now and why not."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            listed = await (client.rooms.commands() if room is None else client.rooms.available_commands(room))
            return [model_to_dict(c) for c in listed.data]

    commands = run_async(_impl(), error_prefix="Failed to list commands")
    if output_format == "json":
        _print_json(commands)
        return
    table = Table(title="Commands")
    columns = ["Syntax", "Summary", "Sender", "Effect"] + ([] if room is None else ["Available", "Why not"])
    for column in columns:
        table.add_column(column)
    for c in commands:
        row = [c.get("syntax"), c.get("summary"), c.get("sender"), c.get("effect")]
        if room is not None:
            row += ["yes" if c.get("available") else "no", c.get("reason")]
        table.add_row(*(_literal(cell) for cell in row))
    console.print(table)


@app.command("delivery")
def delivery(
    room: str = typer.Argument(..., help="Room id or handle."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show how this room reaches you: its connectors, and whether you may change them."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.delivery(room))

    _print_json(run_async(_impl(), error_prefix="Failed to read delivery"))


def _channels(notify: str | None, email: str | None, post: str | None) -> dict[str, str | None]:
    """The channels given on the command line; ``off`` turns one off (null)."""
    return {
        key: (None if value == OFF else value)
        for key, value in (("notify", notify), ("email", email), ("post", post))
        if value is not None
    }


@connector_app.command("add")
def connector_add(
    room: str = typer.Argument(..., help="Room id or handle."),
    name: str = typer.Argument(..., help="Connector name: lowercase letters, digits and hyphens."),
    notify: str | None = typer.Option(None, "--notify", help="A notify service (notify = your Me service) | off."),
    email: str | None = typer.Option(None, "--email", help="An email service (email = your Me service) | off."),
    post: str | None = typer.Option(None, "--post", help="The service keyless senders post through | off."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Add a named connector to the room (at most five); channels left out are off."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.add_connector(room, name, **_channels(notify, email, post)))

    _print_json(run_async(_impl(), error_prefix="Failed to add the connector"))


@connector_app.command("set")
def connector_set(
    room: str = typer.Argument(..., help="Room id or handle."),
    name: str = typer.Argument(..., help="Connector name."),
    notify: str | None = typer.Option(None, "--notify", help="A notify service | off."),
    email: str | None = typer.Option(None, "--email", help="An email service | off."),
    post: str | None = typer.Option(None, "--post", help="The service keyless senders post through | off."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Change a connector's channels; those left out keep their value."""
    channels = _channels(notify, email, post)
    if not channels:
        console.print("[yellow]Nothing to change[/yellow]")
        raise typer.Exit(code=1)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.update_connector(room, name, **channels))

    _print_json(run_async(_impl(), error_prefix="Failed to change the connector"))


@connector_app.command("remove")
def connector_remove(
    room: str = typer.Argument(..., help="Room id or handle."),
    name: str = typer.Argument(..., help="Connector name."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Remove a connector; its reply address and inbound URL stop routing."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.remove_connector(room, name))

    _print_json(run_async(_impl(), error_prefix="Failed to remove the connector"))


@live_app.command("status")
def live_status(
    room: str = typer.Argument(..., help="Room id or handle."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """For each other member: whether their party accepts live requests, and the room's request to them."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            return [model_to_dict(row) for row in (await client.rooms.live_status(room)).data]

    _print_json(run_async(_impl(), error_prefix="Failed to read the live status"))


@live_app.command("waiting")
def live_waiting(
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """The rooms whose live request waits for your account, oldest first."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            return [model_to_dict(row) for row in (await client.rooms.live_waiting()).data]

    _print_json(run_async(_impl(), error_prefix="Failed to list waiting rooms"))


@live_app.command("accept")
def live_accept(
    client_id: str | None = typer.Option(None, "--client-id", help="Renew this client's lease; omit to start one."),
    draining: bool = typer.Option(False, "--draining", help="Finish the queue: serve waiting requests, take none."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Accept live requests for your account until the lease lapses; renew it with --client-id."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            mode = "draining" if draining else "accepting"
            return model_to_dict(await client.rooms.accept_live_requests(client_id=client_id, mode=mode))

    _print_json(run_async(_impl(), error_prefix="Failed to accept live requests"))


@live_app.command("stop")
def live_stop(
    client_id: str | None = typer.Option(None, "--client-id", help="Only this client's lease; omit for every client."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Stop accepting live requests."""

    async def _impl() -> None:
        async with async_client(api_key, base_url) as client:
            await client.rooms.stop_accepting_live_requests(client_id=client_id)

    run_async(_impl(), error_prefix="Failed to stop accepting")
    console.print("[green]✓[/green] Stopped accepting live requests")


@live_app.command("request")
def live_request(
    room: str = typer.Argument(..., help="Room id or handle."),
    member: str = typer.Argument(..., help="The member id to ask (from `live status`)."),
    client_id: str | None = typer.Option(None, "--client-id", help="Renew this client's request; omit to start."),
    generation: str | None = typer.Option(None, "--generation", help="The request being renewed."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Ask a member of the room for live help, or renew the ask with --client-id and --generation."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            lease = await client.rooms.request_live_help(room, member, client_id=client_id, generation=generation)
            return model_to_dict(lease)

    _print_json(run_async(_impl(), error_prefix="Failed to request live help"))


@live_app.command("cancel")
def live_cancel(
    room: str = typer.Argument(..., help="Room id or handle."),
    member: str = typer.Argument(..., help="The member id the request was to."),
    client_id: str = typer.Option(..., "--client-id", help="The client id the request was made with."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """End your own part of a live request; other requesters keep theirs."""

    async def _impl() -> None:
        async with async_client(api_key, base_url) as client:
            await client.rooms.cancel_live_help(room, member, client_id=client_id)

    run_async(_impl(), error_prefix="Failed to cancel the request")
    console.print("[green]✓[/green] Cancelled your live request")


@live_app.command("resolve")
def live_resolve(
    room: str = typer.Argument(..., help="Room id or handle."),
    generation: str | None = typer.Option(None, "--generation", help="Only this request, never a newer one."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Resolve the room's live request to your account, for every requester."""

    async def _impl() -> None:
        async with async_client(api_key, base_url) as client:
            await client.rooms.resolve_live_help(room, generation=generation)

    run_async(_impl(), error_prefix="Failed to resolve the request")
    console.print("[green]✓[/green] Resolved the live request")


@work_app.command("next")
def work_next(
    current: str | None = typer.Option(None, "--current", help="The room id to complete first."),
    claim: str | None = typer.Option(None, "--claim", help="Your claim on --current, from a previous next or claim."),
    offset: int | None = typer.Option(None, "--offset", help="The highest message offset shown in --current."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Claim the room that has waited longest for your account (room_id null when none), completing --current."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.next_room(current, claim_token=claim, offset=offset))

    _print_json(run_async(_impl(), error_prefix="Failed to claim the next room"))


@work_app.command("claim")
def work_claim(
    room: str = typer.Argument(..., help="Room id or handle."),
    token: str = typer.Argument(..., help="The claim token next returned."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Keep holding a claimed room; fails once the claim has lapsed."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.renew_claim(room, token))

    _print_json(run_async(_impl(), error_prefix="Failed to renew the claim"))


@work_app.command("return-later")
def work_return_later(
    room: str = typer.Argument(..., help="Room id or handle."),
    claim: str | None = typer.Option(None, "--claim", help="Your claim on the room, released."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Step away without completing the room; your next `work next` skips it for a few minutes."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.return_later(room, claim_token=claim))

    _print_json(run_async(_impl(), error_prefix="Failed to return the room"))


@work_app.command("done")
def work_done(
    room: str = typer.Argument(..., help="Room id or handle."),
    offset: int = typer.Argument(..., help="The highest message offset you displayed."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Complete the room for your account through OFFSET; a newer mention keeps it waiting."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.mark_done(room, offset))

    _print_json(run_async(_impl(), error_prefix="Failed to complete the room"))


@app.command("invite")
def invite(
    room: str = typer.Argument(..., help="Room id or handle."),
    role: str = typer.Option("member", "--role", help="readonly | member | moderator."),
    max_uses: int | None = typer.Option(None, "--max-uses", help="Uses before the code stops working."),
    expires_in_days: int | None = typer.Option(None, "--expires-in-days", help="Defaults to 7 days."),
    note: str | None = typer.Option(None, "--note", help="A note for yourself."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Create an invitation code for the room."""
    options = {
        key: value
        for key, value in (("max_uses", max_uses), ("expires_in_days", expires_in_days), ("note", note))
        if value is not None
    }

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.create_invitation(room, role=role, **options))

    code = run_async(_impl(), error_prefix="Failed to create the invitation")
    console.print(
        f"[green]✓[/green] Invitation code [bold]{escape(str(code.get('token', '')))}[/bold] "
        f"({escape(str(code.get('role', '')))})"
    )


@app.command("invitations")
def invitations(
    room: str = typer.Argument(..., help="Room id or handle."),
    include_inactive: bool = typer.Option(False, "--all", help="Include used-up, expired and revoked codes."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the room's invitation codes."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            listed = await client.rooms.invitations(room, include_inactive=include_inactive)
            return [model_to_dict(c) for c in listed.data]

    _print_json(run_async(_impl(), error_prefix="Failed to list invitations"))


@app.command("revoke")
def revoke(
    room: str = typer.Argument(..., help="Room id or handle."),
    code_id: str = typer.Argument(..., help="Invitation code id (from invitations)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Revoke an invitation code."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.revoke_invitation(room, code_id))

    run_async(_impl(), error_prefix="Failed to revoke the invitation")
    console.print(f"[green]✓[/green] Revoked {escape(code_id)}")


@app.command("join")
def join(
    code: str = typer.Argument(..., help="Invitation code."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Join a room with an invitation code."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.join(code))

    joined = run_async(_impl(), error_prefix="Failed to join")
    console.print(
        f"[green]✓[/green] Joined {escape(str(joined.get('name', '')))} as @{escape(str(joined.get('handle', '')))}"
    )


@app.command("leave")
def leave(
    room: str = typer.Argument(..., help="Room id or handle."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Leave a room you joined (chat rooms; the owner can't leave)."""
    if not yes and not typer.confirm(f"Leave room '{room}'?"):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=0)

    async def _impl() -> None:
        async with async_client(api_key, base_url) as client:
            await client.rooms.leave(room)

    run_async(_impl(), error_prefix="Failed to leave")
    console.print(f"[green]✓[/green] Left {escape(room)}")


@app.command("chat")
def chat(
    room: str | None = typer.Argument(None, help="Room id, @handle or name prefix; default: most recently active."),
    enrollment: str | None = typer.Option(None, "--enrollment", help="Open this enrollment's room."),
    service: str | None = typer.Option(None, "--service", help="Open this service's room."),
    join_code: str | None = typer.Option(None, "--join", help="Redeem an invitation code, then open its room."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Chat in a room interactively: live messages, posting and switching rooms.

    Needs prompt_toolkit (the package's chat extra) and a key with
    api:rooms read and write. Type /help inside the chat for commands.
    """
    filters = {key: value for key, value in (("enrollment", enrollment), ("service", service)) if value}
    run_chat_command(lambda: async_client(api_key, base_url), room, filters=filters, join_code=join_code)


def run_chat_command(open_client: Any, room: str | None, **options: Any) -> None:
    """Run :func:`unitysvc.chat.run_chat` from a CLI command; shared with ``usvc_seller rooms chat``.

    ``open_client`` returns an async context manager yielding a client with ``.rooms``.
    """
    try:
        from ..chat import run_chat
    except ImportError as exc:
        console.print("[red]✗[/red] The chat needs prompt_toolkit: " + escape('pip install "unitysvc-py[chat]"'))
        raise typer.Exit(code=1) from exc

    async def _impl() -> None:
        async with open_client() as client:
            await run_chat(client.rooms, room, console=console, **options)

    run_async(_impl(), error_prefix="Chat failed")
