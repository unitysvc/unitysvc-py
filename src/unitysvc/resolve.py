"""``client.resolve`` — dry-run gateway route resolution.

Wraps ``POST /v1/customer/resolve`` from the generated low-level
client. Answers "what would the gateway do for this path + routing
key?" without executing the upstream call — useful for debugging,
simulating selection, or picking an interface when the caller only
knows gateway semantics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.resolve_response import ResolveResponse


def resolve(
    client: AuthenticatedClient,
    *,
    path: str,
    routing_key: dict[str, Any] | None = None,
    gateway: str = "api",
    strategy: str | None = None,
) -> ResolveResponse:
    """Dry-run resolve a gateway path + routing key to its candidates.

    Args:
        client: Low-level authenticated client (injected by
            :class:`~unitysvc.Client`).
        path: Gateway request path (same shape as
            ``service.dispatch(path=...)``), e.g. ``v1/chat/completions``.
        routing_key: Optional routing key the gateway would match
            against interface rules (e.g. ``{"model": "gpt-4"}``).
        gateway: ``"api"`` (default), ``"s3"``, or ``"smtp"``. Picks
            which gateway prefix the path belongs to.
        strategy: Override the group's configured routing strategy
            (e.g. ``"by_price"``, ``"lowest_latency"``).

    Returns:
        A :class:`~unitysvc._generated.models.resolve_response.ResolveResponse`
        with the candidate list, the effective strategy, and an
        optional pre-selected candidate.
    """
    from ._generated.api.customer_resolve import customer_resolve_resolve_route
    from ._generated.models.gateway_kind import check_gateway_kind
    from ._generated.models.resolve_request import ResolveRequest
    from ._generated.models.resolve_request_routing_key_type_0 import (
        ResolveRequestRoutingKeyType0,
    )
    from ._generated.types import UNSET

    routing_key_obj = ResolveRequestRoutingKeyType0.from_dict(routing_key) if routing_key else UNSET
    return unwrap(
        customer_resolve_resolve_route.sync_detailed(
            client=client,
            body=ResolveRequest(
                path=path,
                routing_key=routing_key_obj,  # type: ignore[arg-type]
                gateway=check_gateway_kind(gateway),
                strategy=strategy if strategy is not None else UNSET,
            ),
        )
    )
