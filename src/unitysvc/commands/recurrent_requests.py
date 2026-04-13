"""``usvc recurrent-requests`` — remote recurrent-request operations."""

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
    help="Remote recurrent-request operations (list, show, trigger, delete).",
)


@app.command("list")
def list_requests(
    service_id: str | None = typer.Option(None, "--service-id", help="Filter by service id."),
    enrollment_id: str | None = typer.Option(None, "--enrollment-id", help="Filter by enrollment id."),
    status: str | None = typer.Option(None, "--status", help="Filter by status."),
    skip: int = typer.Option(0, "--skip", help="Offset for pagination."),
    limit: int = typer.Option(100, "--limit", help="Max records to return."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List recurrent requests owned by the authenticated customer."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            return model_list(
                await client.recurrent_requests.list(
                    service_id=service_id,
                    enrollment_id=enrollment_id,
                    status=status,
                    skip=skip,
                    limit=limit,
                )
            )

    requests = run_async(_impl(), error_prefix="Failed to list recurrent requests")

    if not requests:
        console.print("[dim]No recurrent requests found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(requests, indent=2, default=str))
        return

    table = Table(title="Recurrent Requests")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Status")
    table.add_column("Schedule")
    for r in requests:
        table.add_row(
            str(r.get("id", ""))[:8] + "…",
            str(r.get("name", "")),
            str(r.get("status", "")),
            str(r.get("schedule", "")),
        )
    console.print(table)


@app.command("show")
def show_request(
    request_id: str = typer.Argument(..., help="Recurrent request ID."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show a single recurrent request as JSON."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.recurrent_requests.get(request_id))

    request = run_async(_impl(), error_prefix="Failed to show recurrent request")
    console.print(json.dumps(request, indent=2, default=str))


@app.command("trigger")
def trigger_request(
    request_id: str = typer.Argument(..., help="Recurrent request ID."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Force an immediate run of a recurrent request."""

    async def _impl() -> Any:
        async with async_client(api_key, base_url) as client:
            return await client.recurrent_requests.trigger(request_id)

    run_async(_impl(), error_prefix="Failed to trigger recurrent request")
    console.print(f"[green]✓[/green] Triggered recurrent request {request_id}")


@app.command("delete")
def delete_request(
    request_id: str = typer.Argument(..., help="Recurrent request ID."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Delete a recurrent request by id."""
    if not yes and not typer.confirm(f"Delete recurrent request '{request_id}'?"):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=0)

    async def _impl() -> Any:
        async with async_client(api_key, base_url) as client:
            return await client.recurrent_requests.delete(request_id)

    run_async(_impl(), error_prefix="Failed to delete recurrent request")
    console.print(f"[green]✓[/green] Deleted recurrent request {request_id}")
