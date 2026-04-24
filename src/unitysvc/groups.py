"""``client.groups`` — customer service group browsing.

Wraps the customer-tagged ``/v1/customer/groups/*`` operations from
the generated low-level client. Service groups are the entry point
for service discovery: customers drill from a group into its member
services.

Group-level dispatch uses the embedded ``CustomerServiceGroupDetail.interface``
— a single ``CustomerAccessInterface`` whose ``base_url`` is already
resolved against the active gateway. Calling ``group.dispatch(...)``
HTTP-POSTs to that URL; the gateway then picks a member service via
the group's ``routing_policy`` (weighted / content-dependent /
price-based).
"""

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


class Groups:
    """Operations on customer-visible service groups (``/v1/customer/groups``).

    Example::

        llm = client.groups.get_by_name("llm")           # by name
        services = client.groups.services(llm.id)        # list members
        resp = client.groups.dispatch(llm.id, json={...})  # call group-level interface
    """

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
    ) -> CustomerServiceGroupsResponse:
        """List active platform service groups visible to the customer."""
        from ._generated.api.customer_groups import customer_groups_list_groups
        from ._generated.types import UNSET

        return unwrap(
            customer_groups_list_groups.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                name=name if name is not None else UNSET,
            )
        )

    def get(self, group_id: str | UUID) -> CustomerServiceGroupDetail:
        """Get a single group by UUID (or partial UUID prefix)."""
        from ._generated.api.customer_groups import customer_groups_get_group

        return unwrap(
            customer_groups_get_group.sync_detailed(
                group_id=UUID(str(group_id)) if not isinstance(group_id, UUID) else group_id,
                client=self._client,
            )
        )

    def get_by_name(self, name: str) -> CustomerServiceGroupDetail:
        """Get a group by its (unique per platform) name.

        Convenience over :meth:`list` + :meth:`get` — raises
        :class:`~unitysvc.NotFoundError` if no group matches.
        """
        from .exceptions import NotFoundError

        resp = self.list(name=name, limit=2)
        for g in resp.data:
            if g.name == name:
                return self.get(g.id)
        raise NotFoundError(f"No service group named {name!r}", status_code=404)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def services(
        self,
        group_id: str | UUID,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> CustomerServicesResponse:
        """List services that belong to a group.

        This is the canonical service-discovery path — there is no
        flat ``/customer/services`` list endpoint.
        """
        from ._generated.api.customer_groups import (
            customer_groups_list_group_services,
        )
        from ._generated.types import UNSET

        return unwrap(
            customer_groups_list_group_services.sync_detailed(
                group_id=UUID(str(group_id)) if not isinstance(group_id, UUID) else group_id,
                client=self._client,
                skip=skip,
                limit=limit,
                search=search if search is not None else UNSET,
            )
        )

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------
    def dispatch(
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
        """Send an HTTP request through the group's gateway interface.

        Resolves ``group.interface.base_url`` (the one group-level
        interface declared on the group's ``user_access_interfaces``)
        and makes a single HTTP request. The gateway's
        ``routing_policy`` picks a member service via weighted /
        content-dependent / price-based selection. No ``interface=``
        parameter is needed because groups have at most one
        user-facing interface.

        Args:
            group_id: Group UUID.
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
        from ._generated.models.customer_access_interface import (
            CustomerAccessInterface,
        )

        group = self.get(group_id)
        iface = group.interface
        if not isinstance(iface, CustomerAccessInterface):
            raise ValueError(
                f"Group {group_id!r} has no user-facing interface configured — "
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
