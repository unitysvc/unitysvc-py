"""``usvc enrollments`` — service enrollment lifecycle.

Mirrors :class:`unitysvc.enrollments.Enrollments` operations
(the ``/v1/customer/enrollments/*`` endpoints):

- ``usvc enrollments list``                  — list the customer's enrollments
- ``usvc enrollments show ENROLLMENT_ID``    — show one enrollment
- ``usvc enrollments cancel ENROLLMENT_ID``  — cancel (reversible — preserves params)
- ``usvc enrollments instance ...``          — start, stop, status, check, key of a
  container service's instance (see below)

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
    help="Enrollment management (list, show, cancel, instance).",
)

instance_app = typer.Typer(
    help="A container service's instance: start, stop, status, check, key.",
)
app.add_typer(instance_app, name="instance")

# ``instance check`` exit codes: 0 the instance is up, 1 it failed on the service's side
# (or something else went wrong), 75 (EX_TEMPFAIL) it failed on the platform's side, so
# retrying later may succeed.
EXIT_SERVICE_FAULT = 1
EXIT_PLATFORM_FAULT = 75


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
    shared: bool = typer.Option(
        True,
        "--shared/--personal",
        help="List shared team enrollments or personal enrollments.",
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
                shared=shared,
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
            enr = await client.enrollments.get(enrollment_id, include_service_details=not no_service_details)
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
    console.print(f"[green]✓[/green] {result.get('message', f'cancelled enrollment {enrollment_id}')}")


# ---------------------------------------------------------------------------
# instance
# ---------------------------------------------------------------------------
def _value(v: Any) -> Any:
    return getattr(v, "value", v)


def _print_instance(state: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        console.print(json.dumps(state, indent=2, default=str))
        return
    reason = f" ({state['reason']})" if state.get("reason") else ""
    fault = f", fault: {state['fault']}" if state.get("fault") else ""
    console.print(
        f"{state.get('requested_action')} #{state.get('generation')}: [bold]{state.get('status')}[/bold]{reason}{fault}"
    )
    for c in state.get("components") or []:
        mark = "[green]ready[/green]" if c.get("ready") else f"[yellow]{c.get('phase')}[/yellow]"
        console.print(f"  {c.get('service')}/{c.get('pod')}: {mark} {c.get('reason') or ''}")
    for e in state.get("entries") or []:
        console.print(f"  {e.get('name')}: {e.get('url')}")


def _exit_for(state: dict[str, Any]) -> int:
    if state.get("status") == "succeeded":
        return 0
    return EXIT_PLATFORM_FAULT if state.get("fault") == "platform" else EXIT_SERVICE_FAULT


def _state(raw: Any) -> dict[str, Any]:
    out = model_to_dict(raw)
    for k in ("status", "fault", "requested_action"):
        if k in out:
            out[k] = _value(out[k])
    return out


@instance_app.command("status")
def instance_status(
    enrollment_id: str = typer.Argument(..., help="Enrollment UUID."),
    wait: int = typer.Option(0, "--wait", min=0, max=60, help="Hold up to N seconds for the request to finish."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show the instance's request, status and pods. Exit 0 when succeeded, else 1 (75 on a platform fault);
    a request still in progress also exits 1."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return _state(await client.enrollments.instance(enrollment_id, wait=wait))

    state = run_async(_impl(), error_prefix="Failed to read the instance")
    _print_instance(state, output_format)
    raise typer.Exit(code=_exit_for(state))


@instance_app.command("start")
def instance_start(
    enrollment_id: str = typer.Argument(..., help="Enrollment UUID."),
    wait: bool = typer.Option(False, "--wait", help="Wait until the instance is up or has failed."),
    timeout: float = typer.Option(300.0, "--timeout", help="Seconds to wait with --wait."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Start the instance (idempotent). With --wait, exit like ``instance check``."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            state = await client.enrollments.start_instance(enrollment_id)
            if wait:
                state = await client.enrollments.wait_for_instance(enrollment_id, timeout=timeout)
            return _state(state)

    state = run_async(_impl(), error_prefix="Failed to start the instance")
    _print_instance(state, output_format)
    if wait:
        raise typer.Exit(code=_exit_for(state))


@instance_app.command("stop")
def instance_stop(
    enrollment_id: str = typer.Argument(..., help="Enrollment UUID."),
    wait: bool = typer.Option(False, "--wait", help="Wait until the instance is stopped."),
    timeout: float = typer.Option(120.0, "--timeout", help="Seconds to wait with --wait."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Stop the instance (idempotent)."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            state = await client.enrollments.stop_instance(enrollment_id)
            if wait:
                state = await client.enrollments.wait_for_instance(enrollment_id, timeout=timeout)
            return _state(state)

    state = run_async(_impl(), error_prefix="Failed to stop the instance")
    _print_instance(state, output_format)
    if wait:
        raise typer.Exit(code=_exit_for(state))


@instance_app.command("check")
def instance_check(
    enrollment_id: str = typer.Argument(..., help="Enrollment UUID."),
    timeout: float = typer.Option(300.0, "--timeout", help="Seconds to wait for the instance to come up."),
    keep: bool = typer.Option(False, "--keep", help="Leave the instance running afterwards."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Start the instance, wait for it to come up, then stop it (unless --keep).

    Exit codes: 0 up; 1 failed on the service's side (bad manifest, image, never ready);
    75 failed on the platform's side (retry later).
    """

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            enrollments = client.enrollments
            await enrollments.start_instance(enrollment_id)
            try:
                state = _state(await enrollments.wait_for_instance(enrollment_id, timeout=timeout))
            finally:
                if not keep:
                    try:
                        await enrollments.stop_instance(enrollment_id)
                    except Exception as exc:  # noqa: BLE001 — the check's own outcome matters more
                        console.print(f"[yellow]could not stop the instance: {exc}[/yellow]")
            return state

    state = run_async(_impl(), error_prefix="Instance check failed")
    _print_instance(state, output_format)
    raise typer.Exit(code=_exit_for(state))


@instance_app.command("key")
def instance_key(
    enrollment_id: str = typer.Argument(..., help="Enrollment UUID."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Print the instance's application key (a secret) on its own line."""

    async def _impl() -> str:
        async with async_client(api_key, base_url) as client:
            return (await client.enrollments.instance_credentials(enrollment_id)).key

    typer.echo(run_async(_impl(), error_prefix="Failed to read the instance key"))
