"""``usvc resolve`` — dry-run gateway route resolution.

Wraps ``client.resolve(...)`` (``POST /v1/customer/resolve``). Answers
"what would the gateway do for this path + routing key?" without
executing the upstream call — useful for debugging routing or
inspecting candidate selection.
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
    parse_json_option,
    run_async,
)

console = Console()


def resolve_cmd(
    path: str = typer.Option(..., "--path", help="Gateway request path, e.g. 'v1/chat/completions'."),
    routing_key: str | None = typer.Option(
        None,
        "--routing-key",
        help="Optional routing key as inline JSON, e.g. '{\"model\": \"gpt-4\"}'.",
    ),
    gateway: str = typer.Option(
        "api", "--gateway", help="Gateway prefix the path belongs to: api | s3 | smtp."
    ),
    strategy: str | None = typer.Option(
        None,
        "--strategy",
        help="Override the group's configured routing strategy (e.g. 'by_price').",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Dry-run resolve a gateway path + routing key. Prints the response as JSON."""
    routing_key_dict = parse_json_option(routing_key, flag="--routing-key")
    if routing_key_dict is not None and not isinstance(routing_key_dict, dict):
        raise typer.BadParameter("--routing-key must be a JSON object")

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            response = await client.resolve(
                path=path,
                routing_key=routing_key_dict,
                gateway=gateway,
                strategy=strategy,
            )
            return model_to_dict(response)

    result = run_async(_impl(), error_prefix="Failed to resolve")
    console.print(json.dumps(result, indent=2, default=str))
