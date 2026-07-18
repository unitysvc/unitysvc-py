"""Anonymous (unauthenticated) browsing of the public UnitySVC catalog.

The rest of this SDK targets the customer API, where every route requires
an API key. The public marketplace catalog is a different surface: it is
served by the ``frontend`` BFF deployment, reached through the site
host's ingress (which peels ``/v1/*`` off to that deployment), and it
answers without credentials.

That is why this is a separate client rather than a mode of
:class:`unitysvc.Client`. It is a different host *and* a different route
set — ``api.unitysvc.com`` answers 404 for ``/services/`` and 401 for
``/groups`` when unauthenticated.

Example::

    from unitysvc import PublicClient

    with PublicClient() as client:
        page = client.services.list(limit=10)
        for service in page.data:
            print(service.name, service.display_name)

These routes are not part of the generated customer OpenAPI spec, so this
module talks to them over ``httpx`` directly. Errors are still routed
through :mod:`unitysvc.exceptions` so callers handle failures the same
way as with the authenticated clients.
"""

from __future__ import annotations

import builtins
import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx

from ._http import reraise_httpx
from .exceptions import error_for_status

DEFAULT_PUBLIC_API_URL = "https://unitysvc.com/v1"
"""Site host. Its ingress routes ``/v1/*`` to the public BFF deployment."""

ENV_PUBLIC_API_URL = "UNITYSVC_PUBLIC_API_URL"


@dataclass
class PublicService:
    """A service as exposed to anonymous callers.

    Deliberately narrower than the authenticated service models: the
    public catalog omits routing, pricing, and seller details.
    """

    id: str
    name: str
    display_name: str | None = None
    status: str | None = None
    currency: str | None = None
    tags: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
    parameters_schema: dict[str, Any] | None = None
    parameters_ui_schema: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> PublicService:
        tags = payload.get("tags")
        return cls(
            id=str(payload.get("id") or ""),
            name=str(payload.get("name") or ""),
            display_name=_opt_str(payload.get("display_name")),
            status=_opt_str(payload.get("status")),
            currency=_opt_str(payload.get("currency")),
            tags=[str(tag) for tag in tags] if isinstance(tags, list) else [],
            created_at=_opt_str(payload.get("created_at")),
            updated_at=_opt_str(payload.get("updated_at")),
            parameters_schema=_opt_dict(payload.get("parameters_schema")),
            parameters_ui_schema=_opt_dict(payload.get("parameters_ui_schema")),
        )


@dataclass
class PublicGroup:
    """A marketplace group (the catalog's tree view)."""

    id: str
    name: str
    display_name: str | None = None
    ancestor_path: str | None = None
    group_type: str | None = None
    sort_order: int | None = None
    service_count: int | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> PublicGroup:
        return cls(
            id=str(payload.get("id") or ""),
            name=str(payload.get("name") or ""),
            display_name=_opt_str(payload.get("display_name")),
            ancestor_path=_opt_str(payload.get("ancestor_path")),
            group_type=_opt_str(payload.get("group_type")),
            sort_order=_opt_int(payload.get("sort_order")),
            service_count=_opt_int(payload.get("service_count")),
        )


@dataclass
class PublicServicePage:
    """One page of services, plus the total matching count.

    These routes paginate by offset (``skip``/``limit``), not by cursor
    like the authenticated listings. :attr:`next_skip` is ``None`` on the
    last page.
    """

    data: list[PublicService]
    count: int
    skip: int = 0

    @property
    def next_skip(self) -> int | None:
        nxt = self.skip + len(self.data)
        return nxt if self.data and nxt < self.count else None


@dataclass
class PublicGroupPage:
    """One page of marketplace groups, plus the total matching count."""

    data: list[PublicGroup]
    count: int
    skip: int = 0

    @property
    def next_skip(self) -> int | None:
        nxt = self.skip + len(self.data)
        return nxt if self.data and nxt < self.count else None


def _opt_str(value: Any) -> str | None:
    return None if value is None else str(value)


def _opt_int(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def _opt_dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def resolve_public_base_url(base_url: str | None = None) -> str:
    """Resolve the public base URL from an argument, env, then the default."""
    resolved = base_url or os.environ.get(ENV_PUBLIC_API_URL) or DEFAULT_PUBLIC_API_URL
    return resolved.rstrip("/")


def parse_response(response: httpx.Response) -> Any:
    """Return the decoded body, or raise the matching SDK exception.

    Mirrors :func:`unitysvc._http.unwrap` for hand-written requests: the
    generated-client wrapper isn't involved on this surface.
    """
    if 200 <= response.status_code < 300:
        return response.json()

    try:
        detail = response.json()
    except ValueError:
        detail = response.text or None

    raise error_for_status(response.status_code, detail=detail, response_body=response.content)


def services_page(payload: Any, *, skip: int) -> PublicServicePage:
    rows = payload.get("data") if isinstance(payload, dict) else None
    data = [PublicService.from_dict(r) for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []
    count = payload.get("count") if isinstance(payload, dict) else None
    return PublicServicePage(data=data, count=count if isinstance(count, int) else len(data), skip=skip)


def groups_page(payload: Any, *, skip: int) -> PublicGroupPage:
    rows = payload.get("data") if isinstance(payload, dict) else None
    data = [PublicGroup.from_dict(r) for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []
    count = payload.get("count") if isinstance(payload, dict) else None
    return PublicGroupPage(data=data, count=count if isinstance(count, int) else len(data), skip=skip)


class PublicServices:
    """Anonymous operations on catalog services."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self, *, skip: int = 0, limit: int = 100) -> PublicServicePage:
        """List public catalog services.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return (server caps this).

        Returns:
            A page of :class:`PublicService`, with the total in ``count``.
        """
        try:
            response = self._client.get("/services/", params={"skip": skip, "limit": limit})
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
        return services_page(parse_response(response), skip=skip)

    def iter_all(self, *, limit: int = 100) -> Iterator[PublicService]:
        """Iterate every public service, following offset pages."""
        skip = 0
        while True:
            page = self.list(skip=skip, limit=limit)
            yield from page.data
            if page.next_skip is None:
                return
            skip = page.next_skip

    def get(self, service_id: str) -> PublicService:
        """Fetch one public service by id."""
        try:
            response = self._client.get(f"/services/{service_id}")
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
        return PublicService.from_dict(parse_response(response))

    def ids(self) -> builtins.list[str]:
        """List the ids of every public service."""
        try:
            response = self._client.get("/services/ids")
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
        payload = parse_response(response)
        return [str(item) for item in payload] if isinstance(payload, list) else []


class PublicGroups:
    """Anonymous operations on marketplace groups."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self, *, skip: int = 0, limit: int = 100) -> PublicGroupPage:
        """List marketplace groups (the catalog tree view)."""
        try:
            response = self._client.get("/groups", params={"skip": skip, "limit": limit})
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
        return groups_page(parse_response(response), skip=skip)


class PublicClient:
    """Unauthenticated client for the public UnitySVC catalog.

    Args:
        base_url: Override the public base URL. Falls back to
            ``UNITYSVC_PUBLIC_API_URL``, then to
            :data:`DEFAULT_PUBLIC_API_URL`.
        timeout: Per-request timeout in seconds. Default 30s.
        verify_ssl: Whether to verify TLS certificates. Default ``True``.

    Example::

        with PublicClient() as client:
            for service in client.services.iter_all():
                print(service.name)
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float | httpx.Timeout | None = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        self._base_url = resolve_public_base_url(base_url)
        timeout_obj = httpx.Timeout(float(timeout)) if isinstance(timeout, (int, float)) else timeout
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout_obj,
            verify=verify_ssl,
            follow_redirects=True,
        )
        self._services: PublicServices | None = None
        self._groups: PublicGroups | None = None

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def services(self) -> PublicServices:
        if self._services is None:
            self._services = PublicServices(self._client)
        return self._services

    @property
    def groups(self) -> PublicGroups:
        if self._groups is None:
            self._groups = PublicGroups(self._client)
        return self._groups

    def close(self) -> None:
        """Close the underlying httpx client."""
        try:
            self._client.close()
        except Exception:
            pass

    def __enter__(self) -> PublicClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
