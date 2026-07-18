"""Tests for anonymous catalog browsing.

Exercises :class:`unitysvc.PublicClient` and
:class:`unitysvc.AsyncPublicClient` against a mocked transport, using the
``httpx.MockTransport`` harness the other resource tests use.
"""

from __future__ import annotations

import httpx
import pytest

from unitysvc import (
    DEFAULT_PUBLIC_API_URL,
    AsyncPublicClient,
    NotFoundError,
    PublicClient,
)

SERVICE_ROW = {
    "id": "32374227-ffe0-5f69-98d5-e6ce97710b67",
    "name": "resp400",
    "display_name": "Direct Response 400 (Bad Request)",
    "status": "ready",
    "currency": "USD",
    "tags": None,
    "created_at": "2026-06-07T14:19:52.971810+00:00",
    "parameters_schema": None,
}

GROUP_ROW = {
    "id": "77ed3e5b-2f1f-4ddd-a0b5-c590f5b7db57",
    "name": "all_services",
    "display_name": "All Services",
    "ancestor_path": "/",
    "group_type": "collection",
    "sort_order": 0,
    "service_count": 11,
}


def _mount(client: PublicClient | AsyncPublicClient, handler) -> None:
    client._client._transport = httpx.MockTransport(handler)


def test_defaults_to_the_site_host() -> None:
    with PublicClient() as client:
        assert client.base_url == DEFAULT_PUBLIC_API_URL


def test_base_url_override_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    with PublicClient(base_url="https://example.test/v1/") as client:
        # Trailing slash is stripped so paths join predictably.
        assert client.base_url == "https://example.test/v1"

    monkeypatch.setenv("UNITYSVC_PUBLIC_API_URL", "https://env.test/v1")
    with PublicClient() as client:
        assert client.base_url == "https://env.test/v1"


def test_services_list_sends_no_credentials() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": [SERVICE_ROW], "count": 1})

    with PublicClient(base_url="https://example.test/v1") as client:
        _mount(client, handler)
        page = client.services.list(limit=10)

    assert seen[0].url.path == "/v1/services/"
    assert "authorization" not in {k.lower() for k in seen[0].headers}
    assert page.count == 1
    assert page.data[0].name == "resp400"
    assert page.data[0].currency == "USD"
    # `tags: null` must normalise to an empty list, not None.
    assert page.data[0].tags == []


def test_service_page_next_skip_stops_at_the_end() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        skip = int(request.url.params.get("skip", 0))
        rows = [SERVICE_ROW] if skip < 3 else []
        return httpx.Response(200, json={"data": rows, "count": 3})

    with PublicClient(base_url="https://example.test/v1") as client:
        _mount(client, handler)
        assert client.services.list(limit=1).next_skip == 1
        assert client.services.list(skip=2, limit=1).next_skip is None
        # An empty trailing page terminates rather than looping forever.
        assert client.services.list(skip=3, limit=1).next_skip is None


def test_iter_all_follows_pages() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        skip = int(request.url.params.get("skip", 0))
        rows = [dict(SERVICE_ROW, name=f"svc-{skip}")] if skip < 3 else []
        return httpx.Response(200, json={"data": rows, "count": 3})

    with PublicClient(base_url="https://example.test/v1") as client:
        _mount(client, handler)
        names = [s.name for s in client.services.iter_all(limit=1)]

    assert names == ["svc-0", "svc-1", "svc-2"]


def test_service_get_and_ids() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/ids"):
            return httpx.Response(200, json=[SERVICE_ROW["id"]])
        return httpx.Response(200, json=SERVICE_ROW)

    with PublicClient(base_url="https://example.test/v1") as client:
        _mount(client, handler)
        assert client.services.get(str(SERVICE_ROW["id"])).name == "resp400"
        assert client.services.ids() == [SERVICE_ROW["id"]]


def test_groups_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/groups"
        return httpx.Response(200, json={"data": [GROUP_ROW], "count": 1})

    with PublicClient(base_url="https://example.test/v1") as client:
        _mount(client, handler)
        page = client.groups.list()

    assert page.data[0].name == "all_services"
    assert page.data[0].service_count == 11


def test_errors_map_to_sdk_exceptions() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Not found"})

    with PublicClient(base_url="https://example.test/v1") as client:
        _mount(client, handler)
        with pytest.raises(NotFoundError):
            client.services.get("missing")


@pytest.mark.asyncio
async def test_async_services_list() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": [SERVICE_ROW], "count": 1})

    async with AsyncPublicClient(base_url="https://example.test/v1") as client:
        _mount(client, handler)
        page = await client.services.list(limit=10)

    assert seen[0].url.path == "/v1/services/"
    assert "authorization" not in {k.lower() for k in seen[0].headers}
    assert page.data[0].name == "resp400"


@pytest.mark.asyncio
async def test_async_iter_all_follows_pages() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        skip = int(request.url.params.get("skip", 0))
        rows = [dict(SERVICE_ROW, name=f"svc-{skip}")] if skip < 2 else []
        return httpx.Response(200, json={"data": rows, "count": 2})

    async with AsyncPublicClient(base_url="https://example.test/v1") as client:
        _mount(client, handler)
        names = [s.name async for s in client.services.iter_all(limit=1)]

    assert names == ["svc-0", "svc-1"]
