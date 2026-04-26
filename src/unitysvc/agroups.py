"""Async mirror of :mod:`unitysvc.groups`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._http import unwrap

if TYPE_CHECKING:
    import httpx

    from ._generated.client import AuthenticatedClient
    from ._generated.models.cursor_page_service_summary import (
        CursorPageServiceSummary,
    )
    from ._generated.models.service_group_detail import ServiceGroupDetail
    from ._generated.models.service_group_list_response import (
        ServiceGroupListResponse,
    )


class AsyncGroups:
    """Async operations on customer-visible service groups."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        name: str | None = None,
    ) -> ServiceGroupListResponse:
        from ._generated.api.customer_groups import customer_groups_list_groups
        from ._generated.types import UNSET

        return unwrap(
            await customer_groups_list_groups.asyncio_detailed(
                client=self._client,
                name=name if name is not None else UNSET,
            )
        )

    async def get(self, name: str) -> ServiceGroupDetail:
        from ._generated.api.customer_groups import customer_groups_get_group

        return unwrap(
            await customer_groups_get_group.asyncio_detailed(
                name=name,
                client=self._client,
            )
        )

    # Legacy alias — same rationale as the sync :class:`Groups` facade.
    get_by_name = get

    async def services(
        self,
        name: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
        search: str | None = None,
    ) -> CursorPageServiceSummary:
        from ._generated.api.customer_groups import (
            customer_groups_list_group_services,
        )
        from ._generated.types import UNSET

        return unwrap(
            await customer_groups_list_group_services.asyncio_detailed(
                name=name,
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                search=search if search is not None else UNSET,
            )
        )

    async def dispatch(
        self,
        name: str,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Async group-level dispatch. See :meth:`unitysvc.groups.Groups.dispatch`."""
        from ._generated.models.access_interface import AccessInterface

        group = await self.get(name)
        iface = group.interface
        if not isinstance(iface, AccessInterface):
            raise ValueError(
                f"Group {name!r} has no user-facing interface configured — "
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
