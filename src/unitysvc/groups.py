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

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ._http import unwrap

if TYPE_CHECKING:
    import httpx

    from ._generated.client import AuthenticatedClient
    from ._generated.models.service_group_detail import ServiceGroupDetail
    from ._generated.models.service_group_summary import ServiceGroupSummary
    from .client import Client
    from .services import Service


class Group:
    """Active-record wrapper around a service group.

    Forwards field access (``grp.name``, ``grp.routing_policy``,
    ``grp.interface``, …) to the underlying generated record via
    ``__getattr__`` — every attribute exposed on
    :class:`ServiceGroupDetail` / :class:`ServiceGroupSummary` is
    available unchanged. Adds methods that delegate back to the
    parent :class:`Client`:

    - :meth:`services` — list member services of this group.
    - :meth:`dispatch` — HTTP-POST through the group-level interface.

    Cheap to construct: holds only references to the raw record and
    the parent client. Returned by :meth:`Groups.get`,
    :meth:`Groups.list`, and as items inside the page returned by
    :meth:`Groups.services`.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: ServiceGroupDetail | ServiceGroupSummary, parent: Client) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        # __getattr__ only fires when normal lookup fails, so
        # ``_raw`` / ``_parent`` are unaffected.
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<Group name={raw.name!r}>"

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

    def __init__(self, client: AuthenticatedClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(self, *, name: str | None = None) -> GroupListPage:
        """List active platform service groups visible to the customer.

        The visible set is small and bounded — the endpoint is not
        paginated. ``name`` filters by partial substring match.
        Items are returned as :class:`Group` wrappers with bound
        methods.
        """
        from ._generated.api.customer_groups import customer_groups_list_groups
        from ._generated.types import UNSET

        raw = unwrap(
            customer_groups_list_groups.sync_detailed(
                client=self._client,
                name=name if name is not None else UNSET,
            )
        )
        return GroupListPage(
            data=[Group(item, parent=self._parent) for item in raw.data],
            count=raw.count,
        )

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


def _http_dispatch(
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
