"""``usvc enrollments`` — service enrollment lifecycle.

Mirrors :class:`unitysvc.enrollments.Enrollments` operations
(the ``/v1/customer/enrollments/*`` endpoints):

- ``usvc enrollments list``                  — list the customer's enrollments
- ``usvc enrollments show ENROLLMENT_ID``    — show one enrollment
- ``usvc enrollments cancel ENROLLMENT_ID``  — cancel (reversible — preserves params)

To create a new enrollment, use ``usvc services enroll SERVICE_ID``.
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
    run_async,
)

console = Console()

app = typer.Typer(
    help="Enrollment management (list, show, cancel).",
)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
@app.command("list")
def list_enrollments(
    skip: int = typer.Option(0, "--skip", help="Offset for pagination."),
    limit: int = typer.Option(100, "--limit", help="Max records to return."),
    no_service_details: bool = typer.Option(
        False,
        "--no-service-details",
        help="Skip embedding the service detail payload (faster).",
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List enrollments owned by the authenticated customer."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            page = await client.enrollments.list(
                skip=skip,
                limit=limit,
                include_service_details=not no_service_details,
            )
            return [model_to_dict(e._raw) for e in page.data]

    enrollments = run_async(_impl(), error_prefix="Failed to list enrollments")

    if not enrollments:
        console.print("[dim]No enrollments found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(enrollments, indent=2, default=str))
        return

    table = Table(title="Enrollments")
    table.add_column("ID", style="dim")
    table.add_column("Service ID", style="dim")
    table.add_column("Status", style="bold")
    for e in enrollments:
        table.add_row(
            str(e.get("id", "")),
            str(e.get("service_id", "")),
            str(e.get("status", "")),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------
@app.command("show")
def show_enrollment(
    enrollment_id: str = typer.Argument(..., help="Enrollment UUID."),
    no_service_details: bool = typer.Option(
        False,
        "--no-service-details",
        help="Skip embedding the service detail payload (faster).",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show one enrollment as JSON."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            enr = await client.enrollments.get(
                enrollment_id, include_service_details=not no_service_details
            )
            return model_to_dict(enr._raw)

    enrollment = run_async(_impl(), error_prefix="Failed to show enrollment")
    console.print(json.dumps(enrollment, indent=2, default=str))


# ---------------------------------------------------------------------------
# cancel
# ---------------------------------------------------------------------------
@app.command("cancel")
def cancel_enrollment(
    enrollment_id: str = typer.Argument(..., help="Enrollment UUID."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Cancel an enrollment (sets status=cancelled; preserves parameters)."""
    if not yes and not typer.confirm(f"Cancel enrollment '{enrollment_id}'?"):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=0)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.enrollments.cancel(enrollment_id))

    result = run_async(_impl(), error_prefix="Failed to cancel enrollment")
    console.print(
        f"[green]✓[/green] {result.get('message', f'cancelled enrollment {enrollment_id}')}"
    )
