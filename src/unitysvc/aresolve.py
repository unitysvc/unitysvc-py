"""Async mirror of :mod:`unitysvc.resolve`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.resolve_response import ResolveResponse


async def resolve(
    client: AuthenticatedClient,
    *,
    path: str,
    routing_key: dict[str, Any] | None = None,
    gateway: str = "api",
    strategy: str | None = None,
) -> ResolveResponse:
    """Async dry-run resolve. See :func:`unitysvc.resolve.resolve`."""
    from ._generated.api.customer_resolve import customer_resolve_resolve_route
    from ._generated.models.gateway_kind import check_gateway_kind
    from ._generated.models.resolve_request import ResolveRequest
    from ._generated.models.resolve_request_routing_key_type_0 import (
        ResolveRequestRoutingKeyType0,
    )
    from ._generated.types import UNSET

    routing_key_obj = ResolveRequestRoutingKeyType0.from_dict(routing_key) if routing_key else UNSET
    return unwrap(
        await customer_resolve_resolve_route.asyncio_detailed(
            client=client,
            body=ResolveRequest(
                path=path,
                routing_key=routing_key_obj,  # type: ignore[arg-type]
                gateway=check_gateway_kind(gateway),
                strategy=strategy if strategy is not None else UNSET,
            ),
        )
    )
