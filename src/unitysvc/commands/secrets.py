"""``usvc secrets`` — remote customer-secret operations.

Minimal surface for now:

- ``usvc secrets list``       — list the customer's secrets
- ``usvc secrets set NAME``   — upsert a secret by name (create or update)
- ``usvc secrets delete NAME`` — delete a secret by name

All commands read credentials from ``UNITYSVC_API_KEY`` /
``UNITYSVC_API_URL`` by default and accept ``--api-key`` / ``--base-url``
overrides.
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ..exceptions import NotFoundError
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
    help="Customer secret management (list, set, delete).",
)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
@app.command("list")
def list_secrets(
    skip: int = typer.Option(0, "--skip", help="Offset for pagination."),
    limit: int = typer.Option(100, "--limit", help="Max records to return."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List secrets owned by the authenticated customer."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            return model_list(await client.secrets.list(skip=skip, limit=limit))

    secrets = run_async(_impl(), error_prefix="Failed to list secrets")

    if not secrets:
        console.print("[dim]No secrets found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(secrets, indent=2, default=str))
        return

    table = Table(title="Secrets")
    table.add_column("Name", style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Owner type")
    for s in secrets:
        table.add_row(
            str(s.get("name", "")),
            str(s.get("id", "")),
            str(s.get("owner_type", "")),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# set (upsert by name)
# ---------------------------------------------------------------------------
@app.command("set")
def set_secret(
    name: str = typer.Argument(..., help="Secret name (unique per customer)."),
    value: str | None = typer.Option(
        None,
        "--value",
        help="Secret value. If omitted, reads from stdin or prompts interactively.",
    ),
    from_file: str | None = typer.Option(
        None,
        "--from-file",
        help="Read the secret value from a file (overrides --value).",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Create or update a secret by name.

    Looks up the secret by name; if it exists, updates its value. If
    not, creates a new secret. Use ``--value`` or ``--from-file`` to
    supply the value non-interactively; otherwise the CLI prompts with
    hidden input.
    """
    if from_file:
        try:
            with open(from_file, encoding="utf-8") as f:
                value = f.read().rstrip("\n")
        except OSError as exc:
            console.print(f"[red]✗[/red] Failed to read {from_file}: {exc}")
            raise typer.Exit(code=1) from exc

    if value is None:
        value = typer.prompt(f"Value for secret '{name}'", hide_input=True, confirmation_prompt=True)

    async def _impl() -> tuple[str, dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            # Try to get existing secret by name; if it exists, update it.
            try:
                await client.secrets.get(name)
                updated = await client.secrets.update(name, {"value": value})
                return ("updated", model_to_dict(updated))
            except NotFoundError:
                created = await client.secrets.create({"name": name, "value": value})
                return ("created", model_to_dict(created))

    action, result = run_async(_impl(), error_prefix="Failed to set secret")
    console.print(f"[green]✓[/green] {action} secret [bold]{result.get('name', name)}[/bold] ({result.get('id', '')})")


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------
@app.command("delete")
def delete_secret(
    name: str = typer.Argument(..., help="Secret name."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Delete a secret by name."""
    if not yes and not typer.confirm(f"Delete secret '{name}'?"):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=0)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            result = await client.secrets.delete(name)
            return model_to_dict(result)

    result = run_async(_impl(), error_prefix="Failed to delete secret")
    console.print(f"[green]✓[/green] {result.get('message', f'deleted secret {name}')}")
