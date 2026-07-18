"""Async mirror of :mod:`unitysvc.public`.

Same anonymous catalog surface as the sync client, using ``httpx``'s
async transport. See :mod:`unitysvc.public` for why this is a separate
client rather than a mode of :class:`unitysvc.AsyncClient`.

Example::

    import asyncio
    from unitysvc import AsyncPublicClient

    async def main():
        async with AsyncPublicClient() as client:
            page = await client.services.list(limit=10)
            for service in page.data:
                print(service.name)

    asyncio.run(main())
"""

from __future__ import annotations

import builtins
from collections.abc import AsyncIterator

import httpx

from ._http import reraise_httpx
from .public import (
    PublicGroupPage,
    PublicService,
    PublicServicePage,
    groups_page,
    parse_response,
    resolve_public_base_url,
    services_page,
)


class AsyncPublicServices:
    """Anonymous operations on catalog services (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def list(self, *, skip: int = 0, limit: int = 100) -> PublicServicePage:
        """See :meth:`unitysvc.public.PublicServices.list`."""
        try:
            response = await self._client.get("/services/", params={"skip": skip, "limit": limit})
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
        return services_page(parse_response(response), skip=skip)

    async def iter_all(self, *, limit: int = 100) -> AsyncIterator[PublicService]:
        """Async-iterate every public service, following offset pages."""
        skip = 0
        while True:
            page = await self.list(skip=skip, limit=limit)
            for service in page.data:
                yield service
            if page.next_skip is None:
                return
            skip = page.next_skip

    async def get(self, service_id: str) -> PublicService:
        """See :meth:`unitysvc.public.PublicServices.get`."""
        try:
            response = await self._client.get(f"/services/{service_id}")
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
        return PublicService.from_dict(parse_response(response))

    async def ids(self) -> builtins.list[str]:
        """See :meth:`unitysvc.public.PublicServices.ids`."""
        try:
            response = await self._client.get("/services/ids")
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
        payload = parse_response(response)
        return [str(item) for item in payload] if isinstance(payload, list) else []


class AsyncPublicGroups:
    """Anonymous operations on marketplace groups (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def list(self, *, skip: int = 0, limit: int = 100) -> PublicGroupPage:
        """See :meth:`unitysvc.public.PublicGroups.list`."""
        try:
            response = await self._client.get("/groups", params={"skip": skip, "limit": limit})
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
        return groups_page(parse_response(response), skip=skip)


class AsyncPublicClient:
    """Unauthenticated async client for the public UnitySVC catalog.

    Args:
        base_url: Override the public base URL. Falls back to
            ``UNITYSVC_PUBLIC_API_URL``, then to
            :data:`unitysvc.public.DEFAULT_PUBLIC_API_URL`.
        timeout: Per-request timeout in seconds. Default 30s.
        verify_ssl: Whether to verify TLS certificates. Default ``True``.
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
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout_obj,
            verify=verify_ssl,
            follow_redirects=True,
        )
        self._services: AsyncPublicServices | None = None
        self._groups: AsyncPublicGroups | None = None

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def services(self) -> AsyncPublicServices:
        if self._services is None:
            self._services = AsyncPublicServices(self._client)
        return self._services

    @property
    def groups(self) -> AsyncPublicGroups:
        if self._groups is None:
            self._groups = AsyncPublicGroups(self._client)
        return self._groups

    async def aclose(self) -> None:
        """Close the underlying async httpx client."""
        try:
            await self._client.aclose()
        except Exception:
            pass

    async def __aenter__(self) -> AsyncPublicClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
