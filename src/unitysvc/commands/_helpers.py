"""Internal helpers shared by the ``usvc`` async command groups."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Coroutine
from contextlib import asynccontextmanager
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
