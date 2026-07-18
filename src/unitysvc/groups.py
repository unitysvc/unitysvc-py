"""``client.groups`` — customer service group browsing.

Wraps the customer-tagged ``/v1/customer/groups/*`` operations from
the generated low-level client. Service groups are the entry point
for service discovery: customers drill from a group into its member
services.

Groups are addressed on the public API by ``name`` (a URL-friendly
slug), not UUID — group UUIDs change when admins recreate a group, so
SDK scripts that hardcode a name survive admin recreations while
UUID-keyed scripts would break.

This module exposes the :class:`Groups` resource manager (the
``client.groups`` namespace) plus a :class:`Group` active-record
wrapper. ``client.groups.get("llm")`` returns a :class:`Group` whose
methods (``services()``, ``dispatch()``) navigate without re-passing
the slug, and whose data fields are forwarded transparently from the
underlying generated record. List / pagination responses are similarly
wrapped so iteration yields :class:`Group` / :class:`Service` objects
with bound methods.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET as _UNSET
from ._http import LowLevelClient, unwrap
from ._streaming import StreamingResponse, build_stream_kwargs
from ._wrappers import _Wrappable

if TYPE_CHECKING:
    import httpx

    from ._generated.models.customer_group_detail import CustomerGroupDetail
    from ._generated.models.customer_group_view import CustomerGroupView
    from ._generated.models.service_collection_member_public import (
        ServiceCollectionMemberPublic,
    )
    from .client import Client
    from .services import Service


class Group(_Wrappable):
    """Active-record wrapper around a service group.

    Forwards field access (``grp.name``, ``grp.routing_policy``,
    ``grp.interface``, …) to the underlying generated record via
    ``__getattr__`` — every attribute exposed on
    :class:`ServiceGroupDetail` / :class:`ServiceGroupSummary` is
    available unchanged. Adds methods that delegate back to the
    parent :class:`Client`:

    - :meth:`services` — list member services of this group.
    - :meth:`dispatch` — HTTP-POST through the group-level interface.

    Inherits from :class:`~unitysvc._wrappers._Wrappable`, so the
    gateway-native wrapper primitives are available as chainable
    methods: ``grp.logged()``, ``grp.cached(ttl="1h")``,
    ``grp.with_failover(other_grp)``, etc. — see :class:`Service`
    for the full list.

    Cheap to construct: holds only references to the raw record and
    the parent client. Returned by :meth:`Groups.get`,
    :meth:`Groups.list`, and as items inside the page returned by
    :meth:`Groups.services`.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: CustomerGroupDetail | CustomerGroupView, parent: Client) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        # __getattr__ only fires when normal lookup fails, so
        # ``_raw`` / ``_parent`` are unaffected.
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<Group name={raw.name!r}>"

    # _Wrappable interface — provides the wrapper-primitive methods.
    @property
    def path(self) -> str:
        """Gateway-relative path for this group: ``g/<name>``."""
        return f"g/{object.__getattribute__(self, '_raw').name}"

    def _get_client(self) -> Client:
        return object.__getattribute__(self, "_parent")

    def services(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        search: str | None = None,
    ) -> ServiceListPage:
        """List member services of this group.

        Wrapper around :meth:`Groups.services` that forwards the
        group's slug. Returns a :class:`ServiceListPage` whose
        ``data`` items are :class:`~unitysvc.services.Service`
        wrappers ready for ``.dispatch()`` / ``.interfaces()``.
        """
        return self._parent.groups.services(
            self._raw.name,
            cursor=cursor,
            limit=limit,
            search=search,
        )

    def dispatch(
        self,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send an HTTP request through the group-level interface.

        See :meth:`Groups.dispatch` for the full contract — this is a
        convenience that fills in the group's slug.
        """
        return self._parent.groups.dispatch(
            self._raw.name,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    def stream(
        self,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StreamingResponse:
        """Open a streaming HTTP request. See :meth:`Groups.stream`."""
        return self._parent.groups.stream(
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
    #
    # Customer-owned collections only — these mirror the membership /
    # metadata ops on :class:`Groups`, filling in this group's id so
    # you don't re-pass it.
    # ------------------------------------------------------------------
    def refresh(self) -> Group:
        """Re-fetch this group by name (latest metadata / members)."""
        return self._parent.groups.get(self._raw.name)

    def update(
        self,
        *,
        display_name: Any = _UNSET,
        description: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> Group:
        """Update this collection's metadata. See :meth:`Groups.update`."""
        return self._parent.groups.update(
            self._raw.id,
            display_name=display_name,
            description=description,
            enabled=enabled,
        )

    def delete(self) -> None:
        """Delete this customer-owned collection. See :meth:`Groups.delete`."""
        self._parent.groups.delete(self._raw.id)

    def add_member(
        self,
        *,
        service_id: str | UUID,
        routing_key: Any = None,
        sort_order: int = 0,
    ) -> ServiceCollectionMemberPublic:
        """Add a member service to this collection. See :meth:`Groups.add_member`."""
        return self._parent.groups.add_member(
            self._raw.id,
            service_id=service_id,
            routing_key=routing_key,
            sort_order=sort_order,
        )

    def members(self) -> builtins.list[ServiceCollectionMemberPublic]:
        """List this collection's member services. See :meth:`Groups.members`."""
        return self._parent.groups.members(self._raw.id)

    def remove_member(self, service_id: str | UUID) -> None:
        """Remove a member service from this collection. See :meth:`Groups.remove_member`."""
        self._parent.groups.remove_member(self._raw.id, service_id)


@dataclass
class GroupListPage:
    """Result of :meth:`Groups.list` — wraps the raw list response.

    ``data`` items are :class:`Group` wrappers with bound methods.
    ``count`` mirrors the upstream response.
    """

    data: list[Group] = field(default_factory=list)
    count: int = 0


@dataclass
class ServiceListPage:
    """Result of :meth:`Groups.services` — cursor-paginated wrapper.

    ``data`` items are :class:`~unitysvc.services.Service` wrappers.
    Echo ``next_cursor`` back as ``cursor=`` to fetch the next page.
    """

    data: list[Service] = field(default_factory=list)
    next_cursor: str | None = None
    has_more: bool = False


class Groups:
    """Operations on customer-visible service groups (``/v1/customer/groups``).

    Example::

        llm = client.groups.get("llm")              # by name
        page = llm.services()                       # active-record nav
        resp = llm.dispatch(json={"messages": [...]})

    The same operations are also available on the manager directly
    (``client.groups.services("llm")``); :class:`Group` is just a
    convenience that pre-binds the slug.
    """

    def __init__(self, client: LowLevelClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(self, *, owner: str = "all", name: str | None = None) -> GroupListPage:
        """List service groups and collections visible to the customer.

        Returns platform groups plus the customer's own editable
        collections. The visible set is small and bounded — the
        endpoint is not paginated and returns a ``{data, count}``
        envelope.

        ``owner`` narrows the server-side result set: ``"all"``
        (platform + own, default), ``"system"`` (platform only), or
        ``"own"`` (the customer's own collections only).

        ``name`` is a client-side substring filter applied on top of
        the returned rows (kept for back-compat with scripts that
        passed ``name=``). Items are :class:`Group` wrappers with
        bound methods.
        """
        from ._generated.api.customer_groups import customer_groups_list_groups

        raw = unwrap(
            customer_groups_list_groups.sync_detailed(
                client=self._client,
                owner=owner,
            )
        )
        data = [Group(item, parent=self._parent) for item in raw.data]
        count = raw.count
        if name is not None:
            data = [g for g in data if name in g.name]
            count = len(data)
        return GroupListPage(data=data, count=count)

    def get(self, name: str) -> Group:
        """Get a single group by its slug name."""
        from ._generated.api.customer_groups import customer_groups_get_group

        raw = unwrap(
            customer_groups_get_group.sync_detailed(
                name=name,
                client=self._client,
            )
        )
        return Group(raw, parent=self._parent)

    # Legacy alias — kept so SDK scripts that called ``get_by_name`` keep
    # working. Lookup is name-native now, so it's just ``get``.
    get_by_name = get

    # ------------------------------------------------------------------
    # Collection management (customer-owned editable groups)
    # ------------------------------------------------------------------
    def create(
        self,
        *,
        name: str,
        display_name: str | None = None,
        description: str | None = None,
    ) -> Group:
        """Create a customer-owned service collection.

        Collections are editable, customer-curated catalogs addressable
        at ``/g/<name>``. Returns the created group as a :class:`Group`.
        """
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
            customer_groups_create_customer_group.sync_detailed(
                client=self._client,
                body=body,
            )
        )
        return Group(raw, parent=self._parent)

    def update(
        self,
        group_id: str | UUID,
        *,
        display_name: Any = _UNSET,
        description: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> Group:
        """Update a customer-owned collection's metadata.

        Only the fields you pass are changed; omitted fields are left
        untouched server-side. Returns the updated group.
        """
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
            customer_groups_update_customer_group.sync_detailed(
                UUID(str(group_id)),
                client=self._client,
                body=body,
            )
        )
        return Group(raw, parent=self._parent)

    def delete(self, group_id: str | UUID) -> None:
        """Delete a customer-owned collection."""
        from ._generated.api.customer_groups import (
            customer_groups_delete_customer_group,
        )

        unwrap(
            customer_groups_delete_customer_group.sync_detailed(
                UUID(str(group_id)),
                client=self._client,
            )
        )

    def add_member(
        self,
        group_id: str | UUID,
        *,
        service_id: str | UUID,
        routing_key: Any = None,
        sort_order: int = 0,
    ) -> ServiceCollectionMemberPublic:
        """Add a member service to a customer-owned collection.

        Returns the created member record (raw generated
        :class:`ServiceCollectionMemberPublic`).
        """
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
            customer_groups_add_member.sync_detailed(
                UUID(str(group_id)),
                client=self._client,
                body=body,
            )
        )

    def members(self, group_id: str | UUID) -> builtins.list[ServiceCollectionMemberPublic]:
        """List the member services of a collection (raw member records)."""
        from ._generated.api.customer_groups import customer_groups_list_members

        return unwrap(
            customer_groups_list_members.sync_detailed(
                UUID(str(group_id)),
                client=self._client,
            )
        )

    def remove_member(self, group_id: str | UUID, service_id: str | UUID) -> None:
        """Remove a member service from a customer-owned collection."""
        from ._generated.api.customer_groups import customer_groups_remove_member

        unwrap(
            customer_groups_remove_member.sync_detailed(
                UUID(str(group_id)),
                UUID(str(service_id)),
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def services(
        self,
        name: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
        search: str | None = None,
    ) -> ServiceListPage:
        """List services that belong to a group.

        Cursor-paginated newest-first. Pass the response's
        ``next_cursor`` back as ``cursor=`` to fetch the next page.

        This is the canonical service-discovery path — there is no
        flat ``/customer/services`` list endpoint. Items are
        :class:`~unitysvc.services.Service` wrappers.
        """
        from ._generated.api.customer_groups import (
            customer_groups_list_group_services,
        )
        from ._generated.types import UNSET
        from .services import Service

        raw = unwrap(
            customer_groups_list_group_services.sync_detailed(
                name=name,
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                search=search if search is not None else UNSET,
            )
        )
        return ServiceListPage(
            data=[Service(item, parent=self._parent) for item in raw.data],
            next_cursor=raw.next_cursor if isinstance(raw.next_cursor, str) else None,
            has_more=bool(raw.has_more),
        )

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------
    def dispatch(
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
        """Send an HTTP request through the group's gateway interface.

        Resolves ``group.interface.base_url`` (the one group-level
        interface declared on the group's ``user_access_interfaces``)
        and makes a single HTTP request. The gateway's
        ``routing_policy`` picks a member service via weighted /
        content-dependent / price-based selection. No ``interface=``
        parameter is needed because groups have at most one
        user-facing interface.

        For wrapper primitives, use the fluent API on the
        active-record :class:`Group`:
        ``grp.cached(ttl="1h").dispatch(json=body)``.

        Args:
            name: Group slug.
            path: Optional sub-path appended to ``interface.base_url``
                (e.g. ``"completions"`` for an LLM gateway that
                already has ``/v1`` in its base).
            method: HTTP method. Defaults to ``POST``.
            json: Request body as JSON-serializable dict.
            data: Raw request body (bytes / str / form).
            headers: Extra headers merged on top of the auth header.
            timeout: Per-request timeout in seconds.

        Returns:
            The raw ``httpx.Response`` from the gateway. Upstream
            errors (4xx/5xx) are not raised — the caller can inspect
            ``.status_code`` / ``.json()`` directly.

        Raises:
            ValueError: If the group has no group-level interface
                configured (``group.interface`` is ``None``).
        """
        from ._generated.models.access_interface import AccessInterface

        group = self.get(name)
        iface = group.interface
        if not isinstance(iface, AccessInterface):
            raise ValueError(
                f"Group {name!r} has no user-facing interface configured — "
                f"call service.dispatch() on a member service instead."
            )
        base_url = iface.base_url if isinstance(iface.base_url, str) else None
        if base_url is None:
            raise ValueError(f"Group {name!r} has no resolved base_url; cannot dispatch.")
        return _http_dispatch(
            self._client,
            base_url=base_url,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Stream
    # ------------------------------------------------------------------
    def stream(
        self,
        name: str,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StreamingResponse:
        """Open a streaming HTTP request through the group-level interface.

        Same interface-resolution and URL composition as :meth:`dispatch`,
        but returns a context-managed :class:`StreamingResponse` so the
        caller can iterate the body lazily (SSE / NDJSON / chunks) via
        ``iter_events()`` / ``iter_bytes()`` / ``iter_lines()``.

        Setting the upstream-protocol ``stream`` flag in the request
        body (e.g. ``json={"stream": True}`` for OpenAI-style APIs) is
        the caller's job — orthogonal to whether the SDK iterates lazily.

        Example::

            with client.groups.stream(name, json={..., "stream": True}) as r:
                for event in r.iter_events():
                    if event.kind == "done":
                        break
                    handle(event.parsed)
        """
        from ._generated.models.access_interface import AccessInterface

        group = self.get(name)
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
        return StreamingResponse(self._client.get_httpx_client(), method, url, kwargs)


def _http_dispatch(
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
    """Shared HTTP dispatch for both group and service interfaces.

    Reuses the low-level client's httpx session (token, SSL, user-agent)
    rather than constructing a fresh client — consistent retries, auth,
    and connection pooling with the rest of the SDK.
    """
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

    httpx_client = low_level_client.get_httpx_client()
    request_kwargs: dict[str, Any] = {"headers": merged_headers}
    if json is not None:
        request_kwargs["json"] = json
    elif data is not None:
        request_kwargs["content"] = data
    if timeout is not None:
        request_kwargs["timeout"] = timeout

    return httpx_client.request(method, url, **request_kwargs)
