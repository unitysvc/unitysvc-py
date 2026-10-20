"""``usvc preferences`` — named preferences on the account a key acts for (unitysvc#2659).

- ``usvc preferences list`` — every preference, as the current account sees it.
- ``usvc preferences get NAME`` — one preference.
- ``usvc preferences set NAME [--value VALUE] [--json]`` — set (or, with no
  ``--value``, clear) any preference by name. The generic escape hatch.
- ``usvc preferences clear NAME`` — clear one preference, back to its fallback.
- ``usvc preferences notification [SERVICE]`` — typed convenience: where
  notices are forwarded. Omit ``SERVICE`` to clear it.
- ``usvc preferences ai [SERVICE]`` — typed convenience: the AI behind
  ``/ai``. Omit ``SERVICE`` to clear it (the platform default applies).
- ``usvc preferences request-log [MODE]`` — typed convenience:
  request-logging mode (``truncated`` | ``complete``). Omit ``MODE`` to
  disable logging.

Preferences belong to the account the key acts for: a personal key changes
your own, a team key the team's, a seller key the seller's.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import typer
from rich.console import Console

from ._helpers import api_key_option, async_client, base_url_option, model_to_dict, parse_json_option, run_async

console = Console()

app = typer.Typer(
    help="Preferences of the account your key acts for (list/get/set/clear).",
)

_LOG_MODES = ("truncated", "complete")


def _describe(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, dict):
        return str(value.get("service", value))
    return str(value)


def _print_preference(result: dict[str, Any]) -> None:
    account = result.get("account") or {}
    console.print(f"[bold]{result.get('name')}[/bold]  ({account.get('type')}: {account.get('name')})")
    console.print(f"  value:     {_describe(result.get('value'))}")
    console.print(f"  effective: {_describe(result.get('effective'))}  (source: {result.get('source') or '-'})")


def _run(api_key: str | None, base_url: str, call: Callable[[Any], Awaitable[Any]], error_prefix: str) -> None:
    """Run one ``client.preferences`` call and print the preference it returns."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await call(client.preferences))

    _print_preference(run_async(_impl(), error_prefix=error_prefix))


@app.command("list")
def list_preferences(
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List every preference. Maps to GET /v1/preferences."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.preferences.list())

    result = run_async(_impl(), error_prefix="Failed to list preferences")
    for item in result.get("data") or []:
        _print_preference(model_to_dict(item))


@app.command("get")
def get_preference(
    name: str = typer.Argument(..., help="Preference name: 'notification', 'ai' or 'request-log'."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show one preference. Maps to GET /v1/preferences/{name}."""
    _run(api_key, base_url, lambda p: p.get(name), f"Failed to get preference '{name}'")


@app.command("set")
def set_preference(
    name: str = typer.Argument(..., help="Preference name: 'notification', 'ai' or 'request-log'."),
    value: str | None = typer.Option(
        None,
        "--value",
        help="New value. Omit to clear the preference.",
    ),
    json_value: bool = typer.Option(
        False,
        "--json",
        help='Parse --value as JSON instead of a literal string (e.g. \'{"service": "labs/llm-balanced"}\').',
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set (or clear) one named preference. Maps to PUT /v1/preferences/{name}.

    ``--value`` is taken as a literal string by default; pass ``--json`` to
    parse it as JSON instead. Omitting ``--value`` clears the preference
    (DELETE /v1/preferences/{name}).
    """
    parsed_value: Any = parse_json_option(value, flag="--value") if json_value else value
    _run(api_key, base_url, lambda p: p.set(name, parsed_value), f"Failed to set preference '{name}'")


@app.command("clear")
def clear_preference(
    name: str = typer.Argument(..., help="Preference name: 'notification', 'ai' or 'request-log'."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Clear one preference, back to its fallback. Maps to DELETE /v1/preferences/{name}."""
    _run(api_key, base_url, lambda p: p.clear(name), f"Failed to clear preference '{name}'")


@app.command("notification")
def set_notification(
    service: str | None = typer.Argument(
        None,
        help=(
            "Where notices are forwarded: a service path (e.g. "
            "'labs/discord-relay'), or a 'b/<name>' broadcast / 'e/<CODE>' "
            "enrollment you own. Omit to clear."
        ),
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set (or clear) where notices for this account are forwarded."""
    _run(api_key, base_url, lambda p: p.set_notification(service), "Failed to set notification")


@app.command("ai")
def set_ai(
    service: str | None = typer.Argument(
        None,
        help=(
            "The AI behind /ai: a service name (e.g. 'labs/llm-balanced') or an "
            "'a/<name>' alias. Services that require enrollment are refused. "
            "Omit to clear (the platform default applies)."
        ),
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set (or clear) the AI this account's /ai calls use."""
    _run(api_key, base_url, lambda p: p.set_ai(service), "Failed to set ai")


@app.command("request-log")
def set_request_log_mode(
    mode: str | None = typer.Argument(
        None,
        help=(
            "'truncated' (8 KB inline preview, no S3) or 'complete' (full "
            "body uploaded to S3). Omit to disable logging."
        ),
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set (or disable) the request-logging mode for the authenticated user."""
    if mode is not None and mode not in _LOG_MODES:
        raise typer.BadParameter(f"mode must be one of {_LOG_MODES}, or omitted to disable")
    _run(api_key, base_url, lambda p: p.set_request_log_mode(mode), "Failed to set request-log mode")
