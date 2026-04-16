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

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.service_alias_create import ServiceAliasCreate
    from ._generated.models.service_alias_update import ServiceAliasUpdate


class Aliases:
    """Operations on the customer's service aliases (``/v1/customer/aliases``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
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

    def switch_routing(self, alias_id: str | UUID, *, on: bool = True) -> Any:
        """Switch routing on or off for an alias.

        When *on* is True, any sibling alias currently routing the same
        (name, routing_key) combo is atomically demoted.  When False the
        alias simply stops routing.
        """
        from ._generated.api.customer_aliases import customer_aliases_switch_alias_routing

        return unwrap(
            customer_aliases_switch_alias_routing.sync_detailed(
                alias_id=UUID(str(alias_id)) if not isinstance(alias_id, UUID) else alias_id,
                client=self._client,
                on=on,
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
