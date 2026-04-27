"""Internal helpers shared by the ``usvc`` async command groups."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from collections.abc import Coroutine
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, TypeVar

import typer
from rich.console import Console

from ..aclient import AsyncClient
from ..client import DEFAULT_API_URL, ENV_API_KEY, ENV_API_URL
from ..exceptions import UnitysvcSDKError

T = TypeVar("T")

console = Console()


def run_async(coro: Coroutine[Any, Any, T], *, error_prefix: str = "Failed") -> T:
    """Run a coroutine and translate SDK errors into ``typer.Exit(1)``."""
    try:
        return asyncio.run(coro)
    except UnitysvcSDKError as exc:
        console.print(f"[red]✗[/red] {error_prefix}: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc
    except typer.Exit:
        raise
    except Exception as exc:  # noqa: BLE001 — surface to user, not crash
        console.print(f"[red]✗[/red] {error_prefix}: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc


@asynccontextmanager
async def async_client(
    api_key: str | None = None,
    base_url: str | None = None,
):
    """Yield an :class:`AsyncClient` configured from args or environment.

    Raises:
        typer.Exit: If no API key is available.
    """
    resolved_key = api_key or os.environ.get(ENV_API_KEY)
    if not resolved_key:
        console.print(
            f"[red]✗[/red] Missing customer API key. Set ${ENV_API_KEY} or pass --api-key.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    resolved_url = base_url or os.environ.get(ENV_API_URL) or DEFAULT_API_URL
    async with AsyncClient(api_key=resolved_key, base_url=resolved_url) as client:
        yield client


def model_to_dict(obj: Any) -> dict[str, Any]:
    """Coerce a generated attrs model (or anything dict-like) into a dict."""
    if isinstance(obj, dict):
        return dict(obj)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    raise TypeError(f"Cannot coerce {type(obj).__name__} to dict")


def model_list(obj: Any) -> list[dict[str, Any]]:
    """Coerce a list-shaped response (``{data: [...], count: N}``) into ``list[dict]``."""
    if isinstance(obj, list):
        return [model_to_dict(item) for item in obj]
    if hasattr(obj, "data"):
        data = obj.data
        return [model_to_dict(item) for item in data]
    if isinstance(obj, dict) and "data" in obj:
        return [model_to_dict(item) for item in obj["data"]]
    return [model_to_dict(obj)]


# ---------------------------------------------------------------------------
# Common Typer option factories
# ---------------------------------------------------------------------------
def api_key_option():
    """Reusable ``--api-key`` option (env-fallback)."""
    return typer.Option(
        None,
        "--api-key",
        envvar=ENV_API_KEY,
        help=f"Customer API key (svcpass_...). Defaults to ${ENV_API_KEY}.",
        show_default=False,
    )


def base_url_option():
    """Reusable ``--base-url`` option (env-fallback)."""
    return typer.Option(
        DEFAULT_API_URL,
        "--base-url",
        envvar=ENV_API_URL,
        help="Backend base URL.",
    )


# ---------------------------------------------------------------------------
# Dispatch / payload parsing helpers
# ---------------------------------------------------------------------------
def parse_json_option(raw: str | None, *, flag: str = "--json") -> Any:
    """Parse a JSON string from a CLI option.

    Returns ``None`` if ``raw`` is None. Raises ``typer.BadParameter``
    on malformed JSON so the user sees a clean error rather than a
    traceback.
    """
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"{flag} is not valid JSON: {exc}") from exc


def parse_data_option(raw: str | None) -> bytes | str | None:
    """Parse a ``--data`` option.

    Supports ``@path`` to read raw bytes from a file (mirrors curl).
    A bare value is passed through as-is.
    """
    if raw is None:
        return None
    if raw.startswith("@"):
        path = Path(raw[1:])
        if not path.exists():
            raise typer.BadParameter(f"--data file not found: {path}")
        return path.read_bytes()
    return raw


def parse_headers(items: list[str] | None) -> dict[str, str] | None:
    """Parse repeated ``--header K:V`` options into a dict."""
    if not items:
        return None
    out: dict[str, str] = {}
    for raw in items:
        if ":" not in raw:
            raise typer.BadParameter(f"--header must be 'Key: Value', got {raw!r}")
        key, _, value = raw.partition(":")
        out[key.strip()] = value.strip()
    return out


def parse_parameters(
    raw_json: str | None,
    items: list[str] | None,
    *,
    json_flag: str = "--parameters",
    item_flag: str = "--parameter",
) -> dict[str, Any] | None:
    """Combine ``--parameters '<json>'`` and repeated ``--parameter K=V``.

    Both are optional; if both are given, ``--parameter`` items override
    keys from ``--parameters``. Returns ``None`` if neither is set.
    Values from ``--parameter`` are kept as strings — JSON must use the
    JSON form for non-string values.
    """
    if raw_json is None and not items:
        return None
    out: dict[str, Any] = {}
    if raw_json is not None:
        parsed = parse_json_option(raw_json, flag=json_flag)
        if not isinstance(parsed, dict):
            raise typer.BadParameter(f"{json_flag} must be a JSON object, got {type(parsed).__name__}")
        out.update(parsed)
    for raw in items or []:
        if "=" not in raw:
            raise typer.BadParameter(f"{item_flag} must be 'key=value', got {raw!r}")
        key, _, value = raw.partition("=")
        out[key.strip()] = value
    return out


def build_recurrence(
    recurrence_json: str | None,
    interval: int | None,
    cron: str | None,
    timezone: str,
) -> dict[str, Any]:
    """Resolve the ``recurrence`` dict for ``services schedule``.

    Exactly one of ``--recurrence`` / ``--interval`` / ``--cron`` must be
    given. ``--timezone`` only applies when ``--cron`` is used.
    """
    forms = [
        ("--recurrence", recurrence_json),
        ("--interval", interval),
        ("--cron", cron),
    ]
    chosen = [name for name, val in forms if val is not None]
    if len(chosen) == 0:
        raise typer.BadParameter("one of --recurrence, --interval, or --cron is required")
    if len(chosen) > 1:
        raise typer.BadParameter(f"only one of --recurrence/--interval/--cron may be given (got {', '.join(chosen)})")

    if recurrence_json is not None:
        parsed = parse_json_option(recurrence_json, flag="--recurrence")
        if not isinstance(parsed, dict):
            raise typer.BadParameter("--recurrence must be a JSON object")
        return parsed
    if interval is not None:
        if interval <= 0:
            raise typer.BadParameter("--interval must be a positive integer (seconds)")
        return {"schedule_type": "interval", "interval_seconds": interval}
    return {"schedule_type": "cron", "cron_expression": cron, "timezone": timezone}


def write_response(response: Any) -> None:
    """Write an httpx-style response: status to stderr, body raw to stdout.

    The body is written as raw bytes so the caller can pipe binary
    payloads losslessly. The status line goes to stderr so it can be
    inspected without polluting the piped body.
    """
    status = getattr(response, "status_code", None)
    reason = getattr(response, "reason_phrase", "") or ""
    if status is not None:
        sys.stderr.write(f"HTTP {status} {reason}\n".rstrip() + "\n")
        sys.stderr.flush()

    content = getattr(response, "content", None)
    if content is None:
        text = getattr(response, "text", "")
        sys.stdout.write(text)
        sys.stdout.flush()
        return
    try:
        sys.stdout.buffer.write(content)
        sys.stdout.flush()
    except (AttributeError, ValueError):
        # Fallback when stdout has no underlying buffer (e.g. captured).
        sys.stdout.write(content.decode("utf-8", errors="replace"))
        sys.stdout.flush()
