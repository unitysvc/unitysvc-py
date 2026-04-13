"""Async mirror of :mod:`unitysvc.resources.aliases`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.service_alias_create import ServiceAliasCreate
    from .._generated.models.service_alias_update import ServiceAliasUpdate


class AsyncAliasesResource:
    """Async operations on the customer's service aliases."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        name: str | None = None,
        include_deactivated: bool = False,
    ) -> Any:
        from .._generated.api.customer_aliases import customer_aliases_list_aliases
        from .._generated.types import UNSET

        return unwrap(
            await customer_aliases_list_aliases.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                name=name if name is not None else UNSET,
                include_deactivated=include_deactivated,
            )
        )

    async def get(self, alias_id: str | UUID) -> Any:
        from .._generated.api.customer_aliases import customer_aliases_get_alias

        return unwrap(
            await customer_aliases_get_alias.asyncio_detailed(
                alias_id=UUID(str(alias_id)) if not isinstance(alias_id, UUID) else alias_id,
                client=self._client,
            )
        )

    async def create(self, body: ServiceAliasCreate | dict[str, Any]) -> Any:
        from .._generated.api.customer_aliases import customer_aliases_create_alias
        from .._generated.models.service_alias_create import ServiceAliasCreate

        if isinstance(body, dict):
            body = ServiceAliasCreate.from_dict(body)

        return unwrap(
            await customer_aliases_create_alias.asyncio_detailed(
                client=self._client,
                body=body,
            )
        )

    async def update(
        self,
        alias_id: str | UUID,
        body: ServiceAliasUpdate | dict[str, Any],
    ) -> Any:
        from .._generated.api.customer_aliases import customer_aliases_update_alias
        from .._generated.models.service_alias_update import ServiceAliasUpdate

        if isinstance(body, dict):
            body = ServiceAliasUpdate.from_dict(body)

        return unwrap(
            await customer_aliases_update_alias.asyncio_detailed(
                alias_id=UUID(str(alias_id)) if not isinstance(alias_id, UUID) else alias_id,
                client=self._client,
                body=body,
            )
        )

    async def switch_routing(self, alias_id: str | UUID, *, on: bool = True) -> Any:
        from .._generated.api.customer_aliases import customer_aliases_switch_alias_routing

        return unwrap(
            await customer_aliases_switch_alias_routing.asyncio_detailed(
                alias_id=UUID(str(alias_id)) if not isinstance(alias_id, UUID) else alias_id,
                client=self._client,
                on=on,
            )
        )

    async def delete(self, alias_id: str | UUID) -> Any:
        from .._generated.api.customer_aliases import customer_aliases_delete_alias

        return unwrap(
            await customer_aliases_delete_alias.asyncio_detailed(
                alias_id=UUID(str(alias_id)) if not isinstance(alias_id, UUID) else alias_id,
                client=self._client,
            )
        )
