"""Console script for ``unitysvc`` — the ``usvc`` CLI."""

from __future__ import annotations

import importlib.metadata
import os

import typer
from rich.console import Console

from .client import (
    DEFAULT_API_URL,
    ENV_API_BASE_URL,
    ENV_API_KEY,
    ENV_API_URL,
    ENV_S3_BASE_URL,
    ENV_SMTP_BASE_URL,
)
from .commands import aliases as aliases_cmd
from .commands import recurrent_requests as recurrent_cmd
from .commands import secrets as secrets_cmd

console = Console()


def version_callback(value: bool) -> None:
    if value:
        try:
            version = importlib.metadata.version("unitysvc-py")
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"
        typer.echo(f"unitysvc-py {version}")
        raise typer.Exit()


app = typer.Typer(
    help=(
        "UnitySVC customer CLI — remote operations against the UnitySVC "
        "customer backend via the unitysvc-py HTTP SDK."
    ),
)


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """UnitySVC customer CLI."""


@app.command("env")
def show_env() -> None:
    """Show the environment variables the SDK and CLI will use."""
    rows = [
        (ENV_API_KEY, _redact(os.environ.get(ENV_API_KEY))),
        (ENV_API_URL, os.environ.get(ENV_API_URL) or f"(unset, default: {DEFAULT_API_URL})"),
        (ENV_API_BASE_URL, os.environ.get(ENV_API_BASE_URL) or "(unset)"),
        (ENV_S3_BASE_URL, os.environ.get(ENV_S3_BASE_URL) or "(unset)"),
        (ENV_SMTP_BASE_URL, os.environ.get(ENV_SMTP_BASE_URL) or "(unset)"),
    ]
    for name, value in rows:
        console.print(f"  [cyan]{name}[/cyan] = {value}")


def _redact(value: str | None) -> str:
    if not value:
        return "(unset)"
    if len(value) <= 12:
        return "***"
    return f"{value[:8]}…{value[-4:]}"


# Remote API command groups
app.add_typer(secrets_cmd.app, name="secrets")
app.add_typer(aliases_cmd.app, name="aliases")
app.add_typer(recurrent_cmd.app, name="recurrent-requests")


if __name__ == "__main__":
    app()
