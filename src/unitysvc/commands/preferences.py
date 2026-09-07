"""``usvc preferences`` — generic per-user preference management (unitysvc#2063).

- ``usvc preferences set NAME [--value VALUE] [--json]``
  — set (or, with no ``--value``, clear) any preference by name. The
  generic escape hatch: works for preferences this CLI has no dedicated
  command for yet.
- ``usvc preferences notification-destination [SERVICE]``
  — typed convenience: where personal notifications are delivered. Omit
  ``SERVICE`` to clear it.
- ``usvc preferences request-log [MODE]``
  — typed convenience: request-logging mode (``truncated`` | ``complete``).
  Omit ``MODE`` to disable logging.

Preferences here are account-level: they apply across every role the
caller has, not just the one that happened to authenticate this
particular request — any of your API keys (customer, seller, admin) may
set them, same as your own login can.
"""

from __future__ import annotations

from typing import Any

import typer
from rich.console import Console

from ._helpers import api_key_option, async_client, base_url_option, model_to_dict, parse_json_option, run_async

console = Console()

app = typer.Typer(
    help="Per-user preference management (set/clear).",
)

_LOG_MODES = ("truncated", "complete")


def _print_result(result: dict[str, Any], name: str) -> None:
    preference = result.get("preference") or {}
    console.print(f"[green]✓[/green] set preference [bold]{name}[/bold]")
    console.print(f"  current preference: {preference}")


# ---------------------------------------------------------------------------
# set (generic)
# ---------------------------------------------------------------------------
@app.command("set")
def set_preference(
    name: str = typer.Argument(..., help="Preference name, e.g. 'notification-destination' or 'request-log'."),
    value: str | None = typer.Option(
        None,
        "--value",
        help="New value. Omit to clear the preference (sends value: null).",
    ),
    json_value: bool = typer.Option(
        False,
        "--json",
        help="Parse --value as JSON instead of a literal string (for non-string values future preferences may need).",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set (or clear) one named preference. Maps to POST /v1/customer/preferences/set.

    ``--value`` is taken as a literal string by default; pass ``--json`` to
    parse it as JSON instead (so ``--value true --json`` sends the boolean
    ``true``, not the string ``"true"``). Omitting ``--value`` entirely
    clears the preference.
    """
    parsed_value: Any = parse_json_option(value, flag="--value") if json_value else value

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.preferences.set(name, parsed_value))

    result = run_async(_impl(), error_prefix=f"Failed to set preference '{name}'")
    _print_result(result, name)


# ---------------------------------------------------------------------------
# notification-destination (typed convenience)
# ---------------------------------------------------------------------------
@app.command("notification-destination")
def set_notification_destination(
    service: str | None = typer.Argument(
        None,
        help=(
            "Where personal notifications are delivered — a service path "
            "(e.g. 'labs/discord-relay'), or a 'b/<name>' broadcast / "
            "'e/<CODE>' enrollment you own. Omit to clear (falls back to "
            "in-app delivery only)."
        ),
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set (or clear) where your personal notifications are delivered."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.preferences.set_notification_destination(service))

    result = run_async(_impl(), error_prefix="Failed to set notification-destination")
    _print_result(result, "notification-destination")


# ---------------------------------------------------------------------------
# request-log (typed convenience)
# ---------------------------------------------------------------------------
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

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.preferences.set_request_log_mode(mode))

    result = run_async(_impl(), error_prefix="Failed to set request-log mode")
    _print_result(result, "request-log")
