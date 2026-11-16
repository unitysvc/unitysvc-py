"""``usvc instances`` — a container service's instance (unitysvc/unitysvc#3016).

Mirrors :class:`unitysvc.instances.Instance`; every command takes the enrollment's id (the
instance has the same id) and needs an API key with the ``api:*`` scope:

- ``usvc instances start ENROLLMENT_ID``   — ask for the instance to start (``--wait`` to follow it)
- ``usvc instances stop ENROLLMENT_ID``    — ask for it to stop
- ``usvc instances status ENROLLMENT_ID``  — the request, its status and the pods
- ``usvc instances check ENROLLMENT_ID``   — start, wait until up, then stop: a connectivity check
- ``usvc instances key ENROLLMENT_ID``     — the instance's application key (a secret)
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_to_dict,
    run_async,
)

console = Console()

app = typer.Typer(
    help="A container service's instance: start, stop, status, check, key.",
)

# ``check`` exit codes: 0 the instance is up, 1 it failed on the service's side (or something else
# went wrong), 75 (EX_TEMPFAIL) it failed on the platform's side, so retrying later may succeed.
EXIT_SERVICE_FAULT = 1
EXIT_PLATFORM_FAULT = 75


# ---------------------------------------------------------------------------
# commands
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


@app.command("status")
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
            return _state(await client.instance(enrollment_id).get(wait=wait))

    state = run_async(_impl(), error_prefix="Failed to read the instance")
    _print_instance(state, output_format)
    raise typer.Exit(code=_exit_for(state))


@app.command("start")
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
            state = await client.instance(enrollment_id).start()
            if wait:
                state = await client.instance(enrollment_id).wait(timeout=timeout)
            return _state(state)

    state = run_async(_impl(), error_prefix="Failed to start the instance")
    _print_instance(state, output_format)
    if wait:
        raise typer.Exit(code=_exit_for(state))


@app.command("stop")
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
            state = await client.instance(enrollment_id).stop()
            if wait:
                state = await client.instance(enrollment_id).wait(timeout=timeout)
            return _state(state)

    state = run_async(_impl(), error_prefix="Failed to stop the instance")
    _print_instance(state, output_format)
    if wait:
        raise typer.Exit(code=_exit_for(state))


@app.command("check")
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
            instance = client.instance(enrollment_id)
            await instance.start()
            try:
                state = _state(await instance.wait(timeout=timeout))
            finally:
                if not keep:
                    try:
                        await instance.stop()
                    except Exception as exc:  # noqa: BLE001 — the check's own outcome matters more
                        console.print(f"[yellow]could not stop the instance: {exc}[/yellow]")
            return state

    state = run_async(_impl(), error_prefix="Instance check failed")
    _print_instance(state, output_format)
    raise typer.Exit(code=_exit_for(state))


@app.command("key")
def instance_key(
    enrollment_id: str = typer.Argument(..., help="Enrollment UUID."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Print the instance's application key (a secret) on its own line."""

    async def _impl() -> str:
        async with async_client(api_key, base_url) as client:
            return (await client.instance(enrollment_id).credentials()).key

    typer.echo(run_async(_impl(), error_prefix="Failed to read the instance key"))
