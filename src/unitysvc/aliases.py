"""``client.aliases`` — customer service alias management.

Wraps the customer-tagged ``/v1/customer/aliases/*`` operations from
the generated low-level client.

Note: The current ``customer_api.json`` spec has a duplicate-schema
issue with ``RequestRoutingKey`` that prevents openapi-python-client
from producing a typed ``ServiceAliasPublic`` response model. Until
the backend spec is fixed, these methods return the raw response
bodies (parsed by the underlying httpx client) rather than a typed
alias model. Create/update/get/delete operations still work; only the
response type is loose.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import LowLevelClient, unwrap

if TYPE_CHECKING:
    from ._generated.models.service_alias_create import ServiceAliasCreate
    from ._generated.models.service_alias_update import ServiceAliasUpdate


class Aliases:
    """Operations on the customer's service aliases (``/v1/customer/aliases``)."""

    def __init__(self, client: LowLevelClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        name: str | None = None,
        include_deactivated: bool = False,
    ) -> Any:
        """List aliases owned by the authenticated customer."""
        from ._generated.api.customer_aliases import customer_aliases_list_aliases
        from ._generated.types import UNSET

        return unwrap(
            customer_aliases_list_aliases.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                name=name if name is not None else UNSET,
                include_deactivated=include_deactivated,
            )
        )

    def get(self, alias_id: str | UUID) -> Any:
        """Get a single alias by id."""
        from ._generated.api.customer_aliases import customer_aliases_get_alias

        return unwrap(
            customer_aliases_get_alias.sync_detailed(
                alias_id=UUID(str(alias_id)) if not isinstance(alias_id, UUID) else alias_id,
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def create(self, body: ServiceAliasCreate | dict[str, Any]) -> Any:
        """Create a new alias."""
        from ._generated.api.customer_aliases import customer_aliases_create_alias
        from ._generated.models.service_alias_create import ServiceAliasCreate

        if isinstance(body, dict):
            body = ServiceAliasCreate.from_dict(body)

        return unwrap(
            customer_aliases_create_alias.sync_detailed(
                client=self._client,
                body=body,
            )
        )

    def update(
        self,
        alias_id: str | UUID,
        body: ServiceAliasUpdate | dict[str, Any],
    ) -> Any:
        """Update an existing alias."""
        from ._generated.api.customer_aliases import customer_aliases_update_alias
        from ._generated.models.service_alias_update import ServiceAliasUpdate

        if isinstance(body, dict):
            body = ServiceAliasUpdate.from_dict(body)

        return unwrap(
            customer_aliases_update_alias.sync_detailed(
                alias_id=UUID(str(alias_id)) if not isinstance(alias_id, UUID) else alias_id,
                client=self._client,
                body=body,
            )
        )

    def switch(
        self,
        identifier: str | UUID,
        *,
        target: str | None = None,
        routing_key: str | None = None,
        on: bool = True,
    ) -> Any:
        """Switch which target routes for an alias — the one-call provider switch.

        ``identifier`` is an alias name, a full UUID, or a partial UUID. For a
        name, ``target`` (target-path substring) and ``routing_key`` (routing-key-
        value substring) select a specific target; omit both to cycle to the next.
        ``on=False`` turns the current target off.
        """
        from ._generated.api.customer_aliases import customer_aliases_switch_alias_routing
        from ._generated.types import UNSET

        return unwrap(
            customer_aliases_switch_alias_routing.sync_detailed(
                identifier=str(identifier),
                client=self._client,
                on=on,
                target=target if target is not None else UNSET,
                routing_key=routing_key if routing_key is not None else UNSET,
            )
        )

    def delete(self, alias_id: str | UUID) -> Any:
        """Delete an alias by id."""
        from ._generated.api.customer_aliases import customer_aliases_delete_alias

        return unwrap(
            customer_aliases_delete_alias.sync_detailed(
                alias_id=UUID(str(alias_id)) if not isinstance(alias_id, UUID) else alias_id,
                client=self._client,
            )
        )
