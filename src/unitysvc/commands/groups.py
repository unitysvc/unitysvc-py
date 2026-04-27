"""``usvc groups`` — service group browsing and dispatch.

Mirrors :class:`unitysvc.groups.Groups` operations (the
``/v1/customer/groups/*`` endpoints):

- ``usvc groups list``                  — list visible groups
- ``usvc groups show NAME``             — show one group
- ``usvc groups services NAME``         — list member services (paginated)
- ``usvc groups dispatch NAME``         — one-shot HTTP through the group gateway
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_to_dict,
    parse_data_option,
    parse_headers,
    parse_json_option,
    run_async,
    write_response,
)

console = Console()

app = typer.Typer(
    help="Service-group operations (list, show, services, dispatch).",
)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
@app.command("list")
def list_groups(
    name: str | None = typer.Option(None, "--name", "-n", help="Filter by partial-substring match on the slug."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List service groups visible to the customer."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            page = await client.groups.list(name=name)
            # Items wrap the underlying record; extract via _raw.
            return [model_to_dict(g._raw) for g in page.data]

    groups = run_async(_impl(), error_prefix="Failed to list groups")

    if not groups:
        console.print("[dim]No groups found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(groups, indent=2, default=str))
        return

    table = Table(title="Service Groups")
    table.add_column("Name", style="bold")
    table.add_column("Display name")
    table.add_column("Routing policy", style="dim")
    for g in groups:
        table.add_row(
            str(g.get("name", "")),
            str(g.get("display_name", "")),
            str(g.get("routing_policy", "")),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------
@app.command("show")
def show_group(
    name: str = typer.Argument(..., help="Group slug name."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show full detail for one group as JSON."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            grp = await client.groups.get(name)
            return model_to_dict(grp._raw)

    group = run_async(_impl(), error_prefix="Failed to show group")
    console.print(json.dumps(group, indent=2, default=str))


# ---------------------------------------------------------------------------
# services
# ---------------------------------------------------------------------------
@app.command("services")
def list_group_services(
    name: str = typer.Argument(..., help="Group slug name."),
    cursor: str | None = typer.Option(None, "--cursor", help="Pagination cursor from a previous page."),
    limit: int = typer.Option(50, "--limit", help="Page size (max records per page)."),
    search: str | None = typer.Option(None, "--search", help="Filter by partial service name."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List services that belong to a group (cursor-paginated)."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            page = await client.groups.services(name, cursor=cursor, limit=limit, search=search)
            return {
                "data": [model_to_dict(s._raw) for s in page.data],
                "next_cursor": page.next_cursor,
                "has_more": page.has_more,
            }

    page = run_async(_impl(), error_prefix="Failed to list group services")
    services = page["data"]

    if not services:
        console.print("[dim]No services in this group[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(page, indent=2, default=str))
        return

    table = Table(title=f"Services in group '{name}'")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Display name")
    table.add_column("Status")
    for s in services:
        table.add_row(
            str(s.get("id", "")),
            str(s.get("name", "")),
            str(s.get("display_name", "")),
            str(s.get("status", "")),
        )
    console.print(table)
    if page["has_more"]:
        console.print(f"[dim]more available — pass --cursor {page['next_cursor']}[/dim]")


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------
@app.command("dispatch")
def dispatch_group(
    name: str = typer.Argument(..., help="Group slug name."),
    path: str = typer.Option("", "--path", help="Sub-path appended to the group interface base URL."),
    method: str = typer.Option("POST", "--method", "-X", help="HTTP method."),
    body_json: str | None = typer.Option(None, "--json", help="Request body as inline JSON."),
    body_data: str | None = typer.Option(
        None, "--data", "-d", help="Raw request body. Prefix with '@' to read from a file."
    ),
    headers: list[str] | None = typer.Option(
        None, "--header", "-H", help="Extra header 'Key: Value'. Repeatable."
    ),
    timeout: float | None = typer.Option(None, "--timeout", help="Per-request timeout in seconds."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """One-shot HTTP through the group's gateway interface.

    Body is written raw to stdout; the HTTP status line goes to stderr,
    so ``usvc groups dispatch llm --json '{"messages": [...]}' > out.json``
    captures only the response body.
    """
    json_body = parse_json_option(body_json)
    data_body = parse_data_option(body_data)
    if json_body is not None and data_body is not None:
        raise typer.BadParameter("--json and --data are mutually exclusive")
    header_dict = parse_headers(headers)

    async def _impl() -> Any:
        async with async_client(api_key, base_url) as client:
            return await client.groups.dispatch(
                name,
                path=path,
                method=method,
                json=json_body,
                data=data_body,
                headers=header_dict,
                timeout=timeout,
            )

    response = run_async(_impl(), error_prefix="Failed to dispatch to group")
    write_response(response)
