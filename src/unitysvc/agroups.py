"""Async mirror of :mod:`unitysvc.groups`.

Same active-record contract: :class:`AsyncGroup` wraps the generated
record and exposes ``services()`` / ``dispatch()`` that delegate back
to the parent :class:`AsyncClient`.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET as _UNSET
from ._http import LowLevelClient, unwrap
from ._streaming import AsyncStreamingResponse, build_stream_kwargs

if TYPE_CHECKING:
    import httpx

    from ._generated.models.customer_group_detail import CustomerGroupDetail
    from ._generated.models.customer_group_view import CustomerGroupView
    from ._generated.models.service_collection_member_public import (
        ServiceCollectionMemberPublic,
    )
    from .aclient import AsyncClient
    from .aservices import AsyncService


class AsyncGroup:
    """Active-record wrapper. See :class:`unitysvc.groups.Group` for the contract."""

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: CustomerGroupDetail | CustomerGroupView, parent: AsyncClient) -> None:
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

    async def stream(
        self,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> AsyncStreamingResponse:
        """See :meth:`AsyncGroups.stream`."""
        return await self._parent.groups.stream(
            self._raw.name,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Collection management (pre-bind this group's id)
    # ------------------------------------------------------------------
    async def refresh(self) -> AsyncGroup:
        """Re-fetch this group by name (latest metadata / members)."""
        return await self._parent.groups.get(self._raw.name)

    async def update(
        self,
        *,
        display_name: Any = _UNSET,
        description: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> AsyncGroup:
        """Update this collection's metadata. See :meth:`AsyncGroups.update`."""
        return await self._parent.groups.update(
            self._raw.id,
            display_name=display_name,
            description=description,
            enabled=enabled,
        )

    async def delete(self) -> None:
        """Delete this customer-owned collection. See :meth:`AsyncGroups.delete`."""
        await self._parent.groups.delete(self._raw.id)

    async def add_member(
        self,
        *,
        service_id: str | UUID,
        routing_key: Any = None,
        sort_order: int = 0,
    ) -> ServiceCollectionMemberPublic:
        """Add a member service to this collection. See :meth:`AsyncGroups.add_member`."""
        return await self._parent.groups.add_member(
            self._raw.id,
            service_id=service_id,
            routing_key=routing_key,
            sort_order=sort_order,
        )

    async def members(self) -> builtins.list[ServiceCollectionMemberPublic]:
        """List this collection's member services. See :meth:`AsyncGroups.members`."""
        return await self._parent.groups.members(self._raw.id)

    async def remove_member(self, service_id: str | UUID) -> None:
        """Remove a member service from this collection. See :meth:`AsyncGroups.remove_member`."""
        await self._parent.groups.remove_member(self._raw.id, service_id)


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

    def __init__(self, client: LowLevelClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(
        self,
        *,
        owner: str = "all",
        name: str | None = None,
    ) -> AsyncGroupListPage:
        """See :meth:`unitysvc.groups.Groups.list`."""
        from ._generated.api.customer_groups import customer_groups_list_groups

        raw = unwrap(
            await customer_groups_list_groups.asyncio_detailed(
                client=self._client,
                owner=owner,
            )
        )
        data = [AsyncGroup(item, parent=self._parent) for item in raw.data]
        count = raw.count
        if name is not None:
            data = [g for g in data if name in g.name]
            count = len(data)
        return AsyncGroupListPage(data=data, count=count)

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

    # ------------------------------------------------------------------
    # Collection management (customer-owned editable groups)
    # ------------------------------------------------------------------
    async def create(
        self,
        *,
        name: str,
        display_name: str | None = None,
        description: str | None = None,
    ) -> AsyncGroup:
        """See :meth:`unitysvc.groups.Groups.create`."""
        from ._generated.api.customer_groups import (
            customer_groups_create_customer_group,
        )
        from ._generated.models.service_collection_create import ServiceCollectionCreate
        from ._generated.types import UNSET

        body = ServiceCollectionCreate(
            name=name,
            display_name=display_name if display_name is not None else UNSET,
            description=description if description is not None else UNSET,
        )
        raw = unwrap(
            await customer_groups_create_customer_group.asyncio_detailed(
                client=self._client,
                body=body,
            )
        )
        return AsyncGroup(raw, parent=self._parent)

    async def update(
        self,
        group_id: str | UUID,
        *,
        display_name: Any = _UNSET,
        description: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> AsyncGroup:
        """See :meth:`unitysvc.groups.Groups.update`."""
        from ._generated.api.customer_groups import (
            customer_groups_update_customer_group,
        )
        from ._generated.models.service_collection_update import ServiceCollectionUpdate

        body = ServiceCollectionUpdate(
            display_name=display_name,
            description=description,
            enabled=enabled,
        )
        raw = unwrap(
            await customer_groups_update_customer_group.asyncio_detailed(
                UUID(str(group_id)),
                client=self._client,
                body=body,
            )
        )
        return AsyncGroup(raw, parent=self._parent)

    async def delete(self, group_id: str | UUID) -> None:
        """See :meth:`unitysvc.groups.Groups.delete`."""
        from ._generated.api.customer_groups import (
            customer_groups_delete_customer_group,
        )

        unwrap(
            await customer_groups_delete_customer_group.asyncio_detailed(
                UUID(str(group_id)),
                client=self._client,
            )
        )

    async def add_member(
        self,
        group_id: str | UUID,
        *,
        service_id: str | UUID,
        routing_key: Any = None,
        sort_order: int = 0,
    ) -> ServiceCollectionMemberPublic:
        """See :meth:`unitysvc.groups.Groups.add_member`."""
        from ._generated.api.customer_groups import customer_groups_add_member
        from ._generated.models.service_collection_member_create import (
            ServiceCollectionMemberCreate,
        )
        from ._generated.types import UNSET

        body = ServiceCollectionMemberCreate(
            service_id=UUID(str(service_id)),
            routing_key=routing_key if routing_key is not None else UNSET,
            sort_order=sort_order,
        )
        return unwrap(
            await customer_groups_add_member.asyncio_detailed(
                UUID(str(group_id)),
                client=self._client,
                body=body,
            )
        )

    async def members(self, group_id: str | UUID) -> builtins.list[ServiceCollectionMemberPublic]:
        """See :meth:`unitysvc.groups.Groups.members`."""
        from ._generated.api.customer_groups import customer_groups_list_members

        return unwrap(
            await customer_groups_list_members.asyncio_detailed(
                UUID(str(group_id)),
                client=self._client,
            )
        )

    async def remove_member(self, group_id: str | UUID, service_id: str | UUID) -> None:
        """See :meth:`unitysvc.groups.Groups.remove_member`."""
        from ._generated.api.customer_groups import customer_groups_remove_member

        unwrap(
            await customer_groups_remove_member.asyncio_detailed(
                UUID(str(group_id)),
                UUID(str(service_id)),
                client=self._client,
            )
        )

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

    async def stream(
        self,
        name: str,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> AsyncStreamingResponse:
        """Async sibling of :meth:`unitysvc.groups.Groups.stream`.

        ``stream()`` is async only because it must resolve the group
        first; the returned object is an ``async with``-able streaming
        response::

            async with await aclient.groups.stream(name, json={...}) as r:
                async for event in r.iter_events():
                    ...
        """
        from ._generated.models.access_interface import AccessInterface

        group = await self.get(name)
        iface = group.interface
        if not isinstance(iface, AccessInterface):
            raise ValueError(
                f"Group {name!r} has no user-facing interface configured — "
                f"call service.stream() on a member service instead."
            )
        base_url = iface.base_url if isinstance(iface.base_url, str) else None
        url, kwargs = build_stream_kwargs(
            token=getattr(self._client, "token", None),
            base_url=base_url,
            path=path,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )
        return AsyncStreamingResponse(self._client.get_async_httpx_client(), method, url, kwargs)


async def _http_dispatch_async(
    low_level_client: LowLevelClient,
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
