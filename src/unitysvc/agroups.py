"""Async mirror of :mod:`unitysvc.groups`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    import httpx

    from ._generated.client import AuthenticatedClient
    from ._generated.models.customer_service_group_detail import (
        CustomerServiceGroupDetail,
    )
    from ._generated.models.customer_service_groups_response import (
        CustomerServiceGroupsResponse,
    )
    from ._generated.models.customer_services_response import (
        CustomerServicesResponse,
    )


class AsyncGroups:
    """Async operations on customer-visible service groups."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        name: str | None = None,
    ) -> CustomerServiceGroupsResponse:
        from ._generated.api.customer_groups import customer_groups_list_groups
        from ._generated.types import UNSET

        return unwrap(
            await customer_groups_list_groups.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                name=name if name is not None else UNSET,
            )
        )

    async def get(self, group_id: str | UUID) -> CustomerServiceGroupDetail:
        from ._generated.api.customer_groups import customer_groups_get_group

        return unwrap(
            await customer_groups_get_group.asyncio_detailed(
                group_id=UUID(str(group_id)) if not isinstance(group_id, UUID) else group_id,
                client=self._client,
            )
        )

    async def get_by_name(self, name: str) -> CustomerServiceGroupDetail:
        from .exceptions import NotFoundError

        resp = await self.list(name=name, limit=2)
        for g in resp.data:
            if g.name == name:
                return await self.get(g.id)
        raise NotFoundError(f"No service group named {name!r}", status_code=404)

    async def services(
        self,
        group_id: str | UUID,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> CustomerServicesResponse:
        from ._generated.api.customer_groups import (
            customer_groups_list_group_services,
        )
        from ._generated.types import UNSET

        return unwrap(
            await customer_groups_list_group_services.asyncio_detailed(
                group_id=UUID(str(group_id)) if not isinstance(group_id, UUID) else group_id,
                client=self._client,
                skip=skip,
                limit=limit,
                search=search if search is not None else UNSET,
            )
        )

    async def dispatch(
        self,
        group_id: str | UUID,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Async group-level dispatch. See :meth:`unitysvc.groups.Groups.dispatch`."""
        from ._generated.models.customer_access_interface import (
            CustomerAccessInterface,
        )

        group = await self.get(group_id)
        iface = group.interface
        if not isinstance(iface, CustomerAccessInterface):
            raise ValueError(
                f"Group {group_id!r} has no user-facing interface configured — "
                f"call service.dispatch() on a member service instead."
            )
        base_url = iface.base_url if isinstance(iface.base_url, str) else None
        return await _http_dispatch_async(
            self._client,
            base_url=base_url,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )


async def _http_dispatch_async(
    low_level_client: AuthenticatedClient,
    *,
    base_url: str | None,
    path: str,
    method: str,
    json: Any,
    data: Any,
    headers: dict[str, str] | None,
    timeout: float | None,
) -> httpx.Response:
    """Async dispatch over the low-level client's async httpx session."""
    if not base_url:
        raise ValueError(
            "Interface has no resolved base_url; cannot dispatch. Check that the gateway is configured upstream."
        )
    url = base_url.rstrip("/")
    if path:
        url = f"{url}/{path.lstrip('/')}"

    merged_headers = dict(headers) if headers else {}
    token = getattr(low_level_client, "token", None)
    if token:
        merged_headers.setdefault("Authorization", f"Bearer {token}")

    httpx_client = low_level_client.get_async_httpx_client()
    request_kwargs: dict[str, Any] = {"headers": merged_headers}
    if json is not None:
        request_kwargs["json"] = json
    elif data is not None:
        request_kwargs["content"] = data
    if timeout is not None:
        request_kwargs["timeout"] = timeout

    return await httpx_client.request(method, url, **request_kwargs)
