"""Async mirror of :mod:`unitysvc.groups`.

Same active-record contract: :class:`AsyncGroup` wraps the generated
record and exposes ``services()`` / ``dispatch()`` that delegate back
to the parent :class:`AsyncClient`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ._http import unwrap

if TYPE_CHECKING:
    import httpx

    from ._generated.client import AuthenticatedClient
    from ._generated.models.service_group_detail import ServiceGroupDetail
    from ._generated.models.service_group_summary import ServiceGroupSummary
    from .aclient import AsyncClient
    from .aservices import AsyncService


class AsyncGroup:
    """Active-record wrapper. See :class:`unitysvc.groups.Group` for the contract."""

    __slots__ = ("_raw", "_parent")

    def __init__(
        self, raw: ServiceGroupDetail | ServiceGroupSummary, parent: AsyncClient
    ) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<AsyncGroup name={raw.name!r}>"

    async def services(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        search: str | None = None,
    ) -> AsyncServiceListPage:
        return await self._parent.groups.services(
            self._raw.name,
            cursor=cursor,
            limit=limit,
            search=search,
        )

    async def dispatch(
        self,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        return await self._parent.groups.dispatch(
            self._raw.name,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )


@dataclass
class AsyncGroupListPage:
    data: list[AsyncGroup] = field(default_factory=list)
    count: int = 0


@dataclass
class AsyncServiceListPage:
    data: list[AsyncService] = field(default_factory=list)
    next_cursor: str | None = None
    has_more: bool = False


class AsyncGroups:
    """Async operations on customer-visible service groups."""

    def __init__(self, client: AuthenticatedClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(
        self,
        *,
        name: str | None = None,
    ) -> AsyncGroupListPage:
        from ._generated.api.customer_groups import customer_groups_list_groups
        from ._generated.types import UNSET

        raw = unwrap(
            await customer_groups_list_groups.asyncio_detailed(
                client=self._client,
                name=name if name is not None else UNSET,
            )
        )
        return AsyncGroupListPage(
            data=[AsyncGroup(item, parent=self._parent) for item in raw.data],
            count=raw.count,
        )

    async def get(self, name: str) -> AsyncGroup:
        from ._generated.api.customer_groups import customer_groups_get_group

        raw = unwrap(
            await customer_groups_get_group.asyncio_detailed(
                name=name,
                client=self._client,
            )
        )
        return AsyncGroup(raw, parent=self._parent)

    # Legacy alias — same rationale as the sync :class:`Groups` facade.
    get_by_name = get

    async def services(
        self,
        name: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
        search: str | None = None,
    ) -> AsyncServiceListPage:
        from ._generated.api.customer_groups import (
            customer_groups_list_group_services,
        )
        from ._generated.types import UNSET
        from .aservices import AsyncService

        raw = unwrap(
            await customer_groups_list_group_services.asyncio_detailed(
                name=name,
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                search=search if search is not None else UNSET,
            )
        )
        return AsyncServiceListPage(
            data=[AsyncService(item, parent=self._parent) for item in raw.data],
            next_cursor=raw.next_cursor if isinstance(raw.next_cursor, str) else None,
            has_more=bool(raw.has_more),
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
