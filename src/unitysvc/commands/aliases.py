"""``usvc aliases`` — remote customer service-alias operations."""

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
    model_list,
    model_to_dict,
    run_async,
)

console = Console()

app = typer.Typer(
    help="Remote service-alias operations (list, show, delete).",
)


@app.command("list")
def list_aliases(
    skip: int = typer.Option(0, "--skip", help="Offset for pagination."),
    limit: int = typer.Option(100, "--limit", help="Max records to return."),
    name: str | None = typer.Option(None, "--name", "-n", help="Filter by alias name."),
    include_deactivated: bool = typer.Option(False, "--include-deactivated", help="Include deactivated aliases."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List aliases owned by the authenticated customer."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            return model_list(
                await client.aliases.list(
                    skip=skip,
                    limit=limit,
                    name=name,
                    include_deactivated=include_deactivated,
                )
            )

    aliases = run_async(_impl(), error_prefix="Failed to list aliases")

    if not aliases:
        console.print("[dim]No aliases found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(aliases, indent=2, default=str))
        return

    table = Table(title="Service Aliases")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Status")
    for a in aliases:
        table.add_row(
            str(a.get("id", ""))[:8] + "…",
            str(a.get("name", "")),
            str(a.get("status", "")),
        )
    console.print(table)


@app.command("show")
def show_alias(
    alias_id: str = typer.Argument(..., help="Alias ID."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show a single alias as JSON."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.aliases.get(alias_id))

    alias = run_async(_impl(), error_prefix="Failed to show alias")
    console.print(json.dumps(alias, indent=2, default=str))


@app.command("delete")
def delete_alias(
    alias_id: str = typer.Argument(..., help="Alias ID."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Delete an alias by id."""
    if not yes and not typer.confirm(f"Delete alias '{alias_id}'?"):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=0)

    async def _impl() -> Any:
        async with async_client(api_key, base_url) as client:
            return await client.aliases.delete(alias_id)

    run_async(_impl(), error_prefix="Failed to delete alias")
    console.print(f"[green]✓[/green] Deleted alias {alias_id}")
