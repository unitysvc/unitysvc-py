"""``usvc services`` — per-service operations.

Mirrors :class:`unitysvc.services.Services` operations
(the ``/v1/customer/services/*`` endpoints):

- ``usvc services show SERVICE_ID``                — show service detail
- ``usvc services interfaces SERVICE_ID``          — list access interfaces
- ``usvc services dispatch SERVICE_ID``            — one-shot HTTP dispatch
- ``usvc services schedule SERVICE_ID``            — register recurring dispatch
- ``usvc services enroll SERVICE_ID``              — enroll in this service
- ``usvc services required-secrets SERVICE_ID``    — list required customer secrets
- ``usvc services optional-secrets SERVICE_ID``    — list optional customer secrets

Note: there is no flat ``usvc services list`` — the customer API has no
flat services endpoint by design. Discovery flows through
``usvc groups services NAME``.
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
    build_recurrence,
    model_to_dict,
    parse_data_option,
    parse_headers,
    parse_json_option,
    parse_parameters,
    run_async,
    write_response,
)

console = Console()

app = typer.Typer(
    help="Per-service operations (show, interfaces, dispatch, schedule, enroll, required-secrets, optional-secrets).",
)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------
@app.command("show")
def show_service(
    service_id: str = typer.Argument(..., help="Service UUID."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show full service detail as JSON."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            svc = await client.services.get(service_id)
            return model_to_dict(svc._raw)

    service = run_async(_impl(), error_prefix="Failed to show service")
    console.print(json.dumps(service, indent=2, default=str))


# ---------------------------------------------------------------------------
# interfaces
# ---------------------------------------------------------------------------
@app.command("interfaces")
def list_interfaces(
    service_id: str = typer.Argument(..., help="Service UUID."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List access interfaces dispatchable by this customer."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            ifaces = await client.services.interfaces(service_id)
            return [model_to_dict(i) for i in ifaces]

    ifaces = run_async(_impl(), error_prefix="Failed to list interfaces")

    if not ifaces:
        console.print("[dim]No interfaces[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(ifaces, indent=2, default=str))
        return

    table = Table(title=f"Interfaces for service {service_id}")
    table.add_column("Name", style="bold")
    table.add_column("Kind")
    table.add_column("Enrollment", style="dim")
    table.add_column("Base URL")
    for i in ifaces:
        table.add_row(
            str(i.get("name", "")),
            str(i.get("kind", "")),
            str(i.get("enrollment_id", "") or "-"),
            str(i.get("base_url", "")),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------
@app.command("dispatch")
def dispatch_service(
    service_id: str = typer.Argument(..., help="Service UUID."),
    interface: str | None = typer.Option(
        None, "--interface", help="Pick an interface by name (required when ambiguous)."
    ),
    enrollment: str | None = typer.Option(
        None, "--enrollment", help="Pick the interface bound to this enrollment UUID."
    ),
    path: str = typer.Option("", "--path", help="Sub-path appended to the interface base URL."),
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
    """One-shot HTTP through the service's gateway interface.

    Body is written raw to stdout; HTTP status line goes to stderr.
    """
    json_body = parse_json_option(body_json)
    data_body = parse_data_option(body_data)
    if json_body is not None and data_body is not None:
        raise typer.BadParameter("--json and --data are mutually exclusive")
    header_dict = parse_headers(headers)

    async def _impl() -> Any:
        async with async_client(api_key, base_url) as client:
            return await client.services.dispatch(
                service_id,
                interface=interface,
                enrollment=enrollment,
                path=path,
                method=method,
                json=json_body,
                data=data_body,
                headers=header_dict,
                timeout=timeout,
            )

    response = run_async(_impl(), error_prefix="Failed to dispatch to service")
    write_response(response)


# ---------------------------------------------------------------------------
# schedule
# ---------------------------------------------------------------------------
@app.command("schedule")
def schedule_service(
    service_id: str = typer.Argument(..., help="Service UUID."),
    recurrence: str | None = typer.Option(
        None, "--recurrence", help="Schedule as inline JSON (advanced — see SDK docs)."
    ),
    interval: int | None = typer.Option(
        None, "--interval", help="Sugar: fixed-interval schedule, in seconds."
    ),
    cron: str | None = typer.Option(
        None, "--cron", help="Sugar: cron expression, e.g. '*/5 * * * *'."
    ),
    timezone: str = typer.Option(
        "UTC",
        "--timezone",
        help="Timezone for --cron (ignored for --interval / --recurrence).",
    ),
    interface: str | None = typer.Option(None, "--interface", help="Pick interface by name."),
    enrollment: str | None = typer.Option(None, "--enrollment", help="Pick interface by enrollment UUID."),
    path: str = typer.Option("", "--path", help="Sub-path appended to interface base URL."),
    method: str = typer.Option("POST", "--method", "-X", help="HTTP method."),
    body_json: str | None = typer.Option(None, "--json", help="Request body template as inline JSON."),
    headers: list[str] | None = typer.Option(
        None, "--header", "-H", help="Extra header 'Key: Value'. Repeatable."
    ),
    name: str | None = typer.Option(None, "--name", help="Optional human-friendly label."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Schedule a recurring dispatch. Prints the new recurrent-request as JSON.

    Pick exactly one of ``--recurrence``, ``--interval``, or ``--cron``.
    """
    recurrence_dict = build_recurrence(recurrence, interval, cron, timezone)
    json_body = parse_json_option(body_json)
    if json_body is not None and not isinstance(json_body, dict):
        raise typer.BadParameter("--json must be a JSON object for scheduled dispatches")
    header_dict = parse_headers(headers)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            created = await client.services.schedule(
                service_id,
                recurrence=recurrence_dict,
                interface=interface,
                enrollment=enrollment,
                path=path,
                method=method,
                json=json_body,
                headers=header_dict,
                name=name,
            )
            return model_to_dict(created)

    result = run_async(_impl(), error_prefix="Failed to schedule recurrent request")
    console.print(json.dumps(result, indent=2, default=str))


# ---------------------------------------------------------------------------
# enroll
# ---------------------------------------------------------------------------
@app.command("enroll")
def enroll_service(
    service_id: str = typer.Argument(..., help="Service UUID."),
    parameters_json: str | None = typer.Option(
        None, "--parameters", help="Enrollment parameters as inline JSON object."
    ),
    parameter: list[str] | None = typer.Option(
        None,
        "--parameter",
        "-p",
        help="Single 'key=value' parameter (string-valued). Repeatable; merged with --parameters.",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Enroll in a service. Prints the new enrollment ID + status."""
    params = parse_parameters(parameters_json, parameter)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            enr = await client.enrollments.create(service_id=service_id, parameters=params)
            return model_to_dict(enr._raw)

    result = run_async(_impl(), error_prefix="Failed to enroll in service")
    console.print(
        f"[green]✓[/green] enrolled in service {service_id} "
        f"→ enrollment [bold]{result.get('id', '')}[/bold] (status={result.get('status', '')})"
    )


# ---------------------------------------------------------------------------
# required-secrets / optional-secrets
# ---------------------------------------------------------------------------
@app.command("required-secrets")
def required_secrets(
    service_id: str = typer.Argument(..., help="Service UUID."),
    interface: str | None = typer.Option(None, "--interface", help="Inspect a specific interface by name."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List customer secrets the picked interface requires.

    Prints one secret name per line (pipeable). Empty output means none
    are required.
    """

    async def _impl() -> list[str]:
        async with async_client(api_key, base_url) as client:
            svc = await client.services.get(service_id)
            return await svc.required_secrets(interface=interface)

    secrets = run_async(_impl(), error_prefix="Failed to fetch required secrets")
    for name in secrets:
        console.print(name, highlight=False)


@app.command("optional-secrets")
def optional_secrets(
    service_id: str = typer.Argument(..., help="Service UUID."),
    interface: str | None = typer.Option(None, "--interface", help="Inspect a specific interface by name."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List customer secrets the picked interface can use but doesn't require."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            svc = await client.services.get(service_id)
            entries = await svc.optional_secrets(interface=interface)
            return [model_to_dict(e) if not isinstance(e, dict) else e for e in entries]

    entries = run_async(_impl(), error_prefix="Failed to fetch optional secrets")

    if not entries:
        console.print("[dim]No optional secrets[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(entries, indent=2, default=str))
        return

    table = Table(title="Optional secrets")
    table.add_column("Name", style="bold")
    table.add_column("Default")
    for e in entries:
        table.add_row(str(e.get("name", "")), str(e.get("default", "")))
    console.print(table)
