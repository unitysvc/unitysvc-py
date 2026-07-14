"""``usvc files`` — account file browser (unitysvc#1533).

Paths use a virtual-folder grammar: the first segment picks the scope,
the rest is the folder path inside it.

- ``usvc files ls``                        — show the scope roots
- ``usvc files ls personal/reports``       — list one folder level
- ``usvc files get shared/q2.pdf ./q2.pdf`` — download a file
- ``usvc files put ./q2.pdf personal/reports`` — upload into a folder
- ``usvc files url personal/q2.pdf``       — print a presigned URL

``personal/`` is the member's own folder; ``shared/`` is the team
folder (team/enterprise plans). Upload and download bytes go directly
between this machine and storage — never through the UnitySVC API.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
from rich.console import Console
from rich.table import Table

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    run_async,
)

if TYPE_CHECKING:
    from ..files import FileScope

console = Console()

app = typer.Typer(
    help="Account files (ls, get, put, url). Paths start with personal/ or shared/.",
)


def _split_vpath(vpath: str) -> tuple[FileScope, str]:
    """Split a virtual path into (scope, relative path)."""
    vpath = vpath.strip("/")
    first, _, rest = vpath.partition("/")
    if first not in ("personal", "shared"):
        raise typer.BadParameter(f"Path must start with 'personal/' or 'shared/', got {vpath!r}")
    return first, rest  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# ls
# ---------------------------------------------------------------------------
@app.command("ls")
def list_files(
    path: str = typer.Argument(
        "",
        help="Virtual folder path (personal/... or shared/...); empty shows the roots.",
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List one folder level of account files."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            if not path.strip("/"):
                # Root: synthesize the scope folders. shared_enabled rides
                # on every list response, so one personal call decides both.
                resp = await client.files.list("", scope="personal", max_keys=1)
                roots = ["personal/"] + (["shared/"] if resp.shared_enabled else [])
                return {"folders": roots, "files": []}
            scope, rel = _split_vpath(path)
            resp = await client.files.list(rel, scope=scope)
            return {
                "folders": [f"{scope}/{p}" for p in resp.common_prefixes],
                "files": [
                    {
                        "key": f"{scope}/{o.key}",
                        "size": o.size,
                        "last_modified": o.last_modified,
                    }
                    for o in resp.objects
                ],
                "truncated": resp.is_truncated,
            }

    listing = run_async(_impl(), error_prefix="Failed to list files")

    if output_format == "json":
        console.print(json.dumps(listing, indent=2, default=str))
        return

    if not listing["folders"] and not listing["files"]:
        console.print("[dim]Empty folder[/dim]")
        return

    table = Table(title=f"Account files — {path or 'roots'}")
    table.add_column("Name", style="bold")
    table.add_column("Size", justify="right")
    table.add_column("Modified")
    for folder in listing["folders"]:
        table.add_row(f"[cyan]{folder}[/cyan]", "—", "—")
    for f in listing["files"]:
        table.add_row(f["key"], str(f["size"]), str(f["last_modified"]))
    console.print(table)
    if listing.get("truncated"):
        console.print("[dim]Listing truncated — more files exist[/dim]")


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------
@app.command("get")
def get_file(
    path: str = typer.Argument(..., help="Virtual file path (personal/... or shared/...)."),
    dest: Path | None = typer.Argument(None, help="Destination file or directory (default: basename in cwd)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Download one file (bytes stream storage → disk directly)."""
    scope, key = _split_vpath(path)
    if not key:
        raise typer.BadParameter("Path must reference a file, not a scope root")

    async def _impl() -> Path:
        async with async_client(api_key, base_url) as client:
            return await client.files.download(key, dest, scope=scope)

    written = run_async(_impl(), error_prefix="Failed to download")
    console.print(f"[green]✓[/green] Downloaded [bold]{path}[/bold] → {written}")


# ---------------------------------------------------------------------------
# put
# ---------------------------------------------------------------------------
@app.command("put")
def put_file(
    src: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Local file to upload."),
    path: str = typer.Argument(
        "personal",
        help="Virtual folder to upload into, e.g. personal, personal/reports, shared.",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Upload one file into a folder (bytes go disk → storage directly).

    The size ceiling is enforced by the server-signed upload policy;
    uploading to an existing name overwrites it.
    """
    scope, folder = _split_vpath(path)

    async def _impl() -> str:
        async with async_client(api_key, base_url) as client:
            return await client.files.upload(src, folder, scope=scope)

    key = run_async(_impl(), error_prefix="Failed to upload")
    console.print(f"[green]✓[/green] Uploaded [bold]{src.name}[/bold] → {scope}/{key}")


# ---------------------------------------------------------------------------
# url
# ---------------------------------------------------------------------------
@app.command("url")
def presign_url(
    path: str = typer.Argument(..., help="Virtual file path (personal/... or shared/...)."),
    expires_in: int = typer.Option(900, "--expires", help="URL validity in seconds (60-3600)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Print a short-TTL presigned download URL (for scripts / sharing)."""
    scope, key = _split_vpath(path)
    if not key:
        raise typer.BadParameter("Path must reference a file, not a scope root")

    async def _impl() -> str:
        async with async_client(api_key, base_url) as client:
            resp = await client.files.download_url(key, scope=scope, expires_in=expires_in)
            return resp.url

    url = run_async(_impl(), error_prefix="Failed to presign")
    # Bare print: the URL is the output — keep it pipeable.
    print(url)
