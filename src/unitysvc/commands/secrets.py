"""``usvc secrets`` — remote customer-secret operations.

- ``usvc secrets list``        — list the customer's secrets
- ``usvc secrets set NAME``    — upsert a secret by name (``--description`` too)
- ``usvc secrets upload FILE`` — bulk-set from a ``.env.example`` manifest
  (environment- and description-aware)
- ``usvc secrets delete NAME`` — delete a secret by name

All commands read credentials from ``UNITYSVC_API_KEY`` /
``UNITYSVC_API_URL`` by default and accept ``--api-key`` / ``--base-url``
overrides.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

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
    help="Customer secret management (list, set, upload, delete).",
)

# Valid env-var / secret name: leading letter or underscore, then word chars.
_VALID_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# ``${NAME}`` / ``${NAME:-default}`` / ``${NAME-default}`` — the one expansion
# form the manifest resolves against the process environment. Anything else is
# taken verbatim (opaque secret material: tokens, URLs, ids).
_EXPANSION_RE = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)(?::?-(.*))?\}$")


def _resolve_rhs(rhs: str, environ: Mapping[str, str]) -> str:
    """Resolve one assignment's right-hand side.

    ``${NAME:-default}`` (or ``${NAME-default}`` / ``${NAME}``) uses the process
    env value for ``NAME`` when set and non-empty, else the default — the
    ``source``-compatible semantics that let one file seed local test values and,
    in CI, pick up externally-provided ones. Any other RHS is verbatim (one layer
    of surrounding quotes stripped).
    """
    rhs = rhs.strip()
    if len(rhs) >= 2 and rhs[0] == rhs[-1] and rhs[0] in ("'", '"'):
        return rhs[1:-1]
    m = _EXPANSION_RE.match(rhs)
    if not m:
        return rhs
    name, default = m.group(1), m.group(2)
    env_val = environ.get(name)
    if env_val:
        return env_val
    return default if default is not None else ""


def _parse_secrets_text(text: str, environ: Mapping[str, str] | None = None) -> list[tuple[str, str, str | None]]:
    """Parse a ``.env``-style manifest into ``(name, value, description)`` triples.

    ``NAME=value`` / ``export NAME=value`` lines; the contiguous ``#`` comment
    lines directly above a definition become its **description** (a blank line
    separates blocks, so a file header attaches to no secret); the value is
    resolved by :func:`_resolve_rhs`. Last assignment wins.
    """
    environ = os.environ if environ is None else environ
    values: dict[str, tuple[str, str | None]] = {}
    order: list[str] = []
    comments: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            comments = []
            continue
        if line.startswith("#"):
            comments.append(line.lstrip("#").strip())
            continue
        if line.startswith(("export ", "export\t")):
            line = line[len("export") :].lstrip()
        name, sep, rhs = line.partition("=")
        name = name.strip()
        if not sep or not _VALID_NAME_RE.match(name):
            comments = []
            continue
        description = "\n".join(comments).strip() or None
        if name not in values:
            order.append(name)
        values[name] = (_resolve_rhs(rhs, environ), description)
        comments = []
    return [(n, values[n][0], values[n][1]) for n in order]


def _read_secrets_source(file: str | None) -> str:
    """Read manifest text from a file path or stdin — no implicit default."""
    if file == "-":
        return sys.stdin.read()
    if file is None:
        if sys.stdin.isatty():
            console.print(
                "[red]No input.[/red] Pass a file or pipe one in:\n"
                "  usvc secrets upload FILE\n"
                "  <decrypt> | usvc secrets upload"
            )
            raise typer.Exit(code=2)
        return sys.stdin.read()
    path = Path(file)
    if not path.is_file():
        console.print(f"[red]Secrets file not found:[/red] {file}")
        raise typer.Exit(code=1)
    return path.read_text()


def _print_upload_summary(rows: list[tuple[str, str]], output_format: str, *, dry_run: bool) -> None:
    """Render the per-secret outcome table (or JSON) plus a one-line tally."""
    if output_format == "json":
        console.print(json.dumps([{"name": n, "status": s} for n, s in rows], indent=2))
        return
    table = Table(title="Secrets (dry run)" if dry_run else "Secrets uploaded")
    table.add_column("Name", style="bold")
    table.add_column("Status", style="dim")
    for name, status in rows:
        table.add_row(name, status)
    console.print(table)
    n_desc = sum(1 for _, s in rows if "(+desc)" in s)
    verb = "would upload" if dry_run else "uploaded"
    summary = f"[green]✓[/green] {verb} {len(rows)} secret(s)"
    if n_desc:
        summary += f", {n_desc} with a description"
    console.print(summary)


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

    table = Table(title="Secrets & variables")
    table.add_column("Name", style="bold")
    table.add_column("Kind")
    table.add_column("Value")
    table.add_column("Owner type")
    for s in secrets:
        is_secret = s.get("sensitive", True)
        # Variables (sensitive=false) return their value; secrets are masked.
        value = "[dim]•••[/dim]" if is_secret else str(s.get("value") or "")
        table.add_row(
            str(s.get("name", "")),
            "secret" if is_secret else "[cyan]variable[/cyan]",
            value,
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
        help=(
            "Secret value. If omitted: reads from stdin when piped, prompts with hidden input when run interactively."
        ),
    ),
    variable: bool = typer.Option(
        False,
        "--variable",
        help=(
            "Store as a viewable variable (value is returned by list/get) "
            "rather than a write-only secret. Honored only when creating."
        ),
    ),
    description: str | None = typer.Option(
        None,
        "--description",
        "-d",
        help=(
            "Author guidance stored on the row (what this secret is / how to "
            "obtain one). Omit to leave any existing description untouched. For "
            "many secrets at once, use a .env.example manifest with 'secrets upload'."
        ),
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set a secret or variable by name (idempotent — creates or rotates).

    Maps to ``PUT /v1/customer/secrets/{name}``. The value is encrypted
    server-side. A **secret** (default) is write-only and cannot be retrieved;
    pass ``--variable`` to store a viewable **variable** instead (its value is
    returned by ``list``/``get`` — useful for non-sensitive config like a
    notification email). ``--variable`` is honored only when the row is created.
    Resolution order for the value, in order of precedence:

      1. ``--value VALUE``                     — explicit literal (or
                                                 ``--value "$ENV_NAME"``
                                                 via shell expansion).
      2. piped stdin                           — ``echo v | usvc secrets set X``
                                                 (trailing newline stripped).
      3. interactive prompt                    — TTY only; hidden input.

    Mirrors the convention used by ``gh secret set``, ``vault kv put``,
    and similar tools.
    """
    if value is None:
        if not sys.stdin.isatty():
            # Piped stdin (or closed stdin): read it. Strip a single
            # trailing newline so ``echo "$X" | ...`` works as expected.
            value = sys.stdin.read().rstrip("\n")
        else:
            # Terminal: prompt with hidden input + confirmation.
            value = typer.prompt(
                f"Value for secret '{name}'",
                hide_input=True,
                confirmation_prompt=True,
            )

    # ``--variable`` => sensitive=False (viewable); otherwise leave unset so the
    # server default (a secret) applies and existing rows keep their kind.
    sensitive = False if variable else None

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.secrets.set(name, value, sensitive=sensitive, description=description))

    result = run_async(_impl(), error_prefix="Failed to set secret")
    kind = "variable" if result.get("sensitive") is False else "secret"
    console.print(f"[green]✓[/green] set {kind} [bold]{result.get('name', name)}[/bold] ({result.get('id', '')})")


# ---------------------------------------------------------------------------
# upload (bulk-set from a .env.example manifest)
# ---------------------------------------------------------------------------
@app.command("upload")
def upload_secrets(
    file: str | None = typer.Argument(
        None,
        help="Manifest file (.env.example) to read, or '-' for stdin. Omit when piping.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse and list; upload nothing."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Bulk-set secrets from an ``.env``-style manifest (idempotent).

    Reads a shell-sourceable ``.env.example`` and sets each via
    ``PUT /v1/customer/secrets/{name}``, with two conventions:

    - **Environment-aware**: ``NAME=${NAME:-default}`` resolves ``NAME`` from the
      process environment when set, else the default — so the file reuses values
      already exported in your shell, falling back to test defaults. Opaque
      literals (``NAME=sk-abc``) are verbatim.
    - **Description-aware**: the contiguous ``#`` comment lines directly above a
      definition become that secret's ``description``. A blank line ends a block,
      so a file header attaches to no secret.

    Every declared entry is set (source semantics; empties included, so the row
    that carries a description is created). Last assignment wins. Input is a file
    or a pipe: ``FILE`` argument, or ``-`` / piped stdin.
    """
    entries = _parse_secrets_text(_read_secrets_source(file))
    if not entries:
        console.print("[yellow]No secrets found in input.[/yellow]")
        raise typer.Exit(code=0)

    def _status(description: str | None, *, done: bool) -> str:
        return ("set" if done else "would set") + (" (+desc)" if description else "")

    if dry_run:
        rows = [(n, _status(d, done=False)) for n, _v, d in entries]
        _print_upload_summary(rows, output_format, dry_run=True)
        return

    async def _impl() -> list[tuple[str, str | None]]:
        done: list[tuple[str, str | None]] = []
        async with async_client(api_key, base_url) as client:
            for name, value, description in entries:
                await client.secrets.set(name, value, description=description)
                done.append((name, description))
        return done

    done = run_async(_impl(), error_prefix="Failed to upload secrets")
    rows = [(n, _status(d, done=True)) for n, d in done]
    _print_upload_summary(rows, output_format, dry_run=False)


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
