"""Tests for anonymous (no-api_key) catalog browsing.

The customer API serves three catalog reads without credentials
(unitysvc#1610), so ``Client``/``AsyncClient`` can be constructed with no
``api_key``. Such a client uses the generated *unauthenticated* low-level
client, which sends no ``Authorization`` header at all — the customer API
reads an absent header as anonymous, while a malformed ``Bearer `` header
would earn a 401.
"""

from __future__ import annotations

import httpx
import pytest

from unitysvc import (
    AsyncClient,
    AuthenticationError,
    Client,
)

GROUPS_PAGE = {
    "data": [
        {
            "id": "77ed3e5b-2f1f-4ddd-a0b5-c590f5b7db57",
            "name": "all_services",
            "display_name": "All Services",
            "owner_type": "platform",
            "editable": False,
            "member_count": 11,
        }
    ],
    "count": 1,
}

SERVICES_PAGE = {
    "data": [
        {
            "id": "32374227-ffe0-5f69-98d5-e6ce97710b67",
            "name": "resp200",
            "display_name": "Direct Response 200 (OK)",
            "service_type": "http",
        }
    ],
    "next_cursor": None,
    "has_more": False,
}


def _mount_sync(client: Client, handler) -> None:
    client._client.get_httpx_client()._transport = httpx.MockTransport(handler)


def _mount_async(client: AsyncClient, handler) -> None:
    client._client.get_async_httpx_client()._transport = httpx.MockTransport(handler)


def test_client_no_longer_requires_an_api_key() -> None:
    with Client() as client:
        assert client._api_key is None


def test_empty_api_key_is_still_an_error() -> None:
    """Omitting the key means "anonymous"; an empty string means a missing
    env var got passed through. Treating the latter as anonymous would turn
    a misconfiguration into a silently narrower catalog."""
    with pytest.raises(ValueError, match="api_key is required"):
        Client(api_key="")


def test_authenticated_client_still_sends_the_key() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=GROUPS_PAGE)

    with Client(api_key="svcpass_test", base_url="https://example.test/v1") as client:
        _mount_sync(client, handler)
        client.groups.list()

    assert seen[0].headers["authorization"] == "Bearer svcpass_test"


def test_anonymous_client_sends_no_authorization_header() -> None:
    """The header must be absent, not empty.

    An empty-token AuthenticatedClient would send ``Bearer `` — which the
    customer API treats as a malformed credential (401), not as anonymous.
    """
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=GROUPS_PAGE)

    with Client(base_url="https://example.test/v1") as client:
        _mount_sync(client, handler)
        page = client.groups.list()

    assert "authorization" not in {k.lower() for k in seen[0].headers}
    assert [g.name for g in page.data] == ["all_services"]


def test_anonymous_group_services_listing() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/groups/all_services/services"
        assert "authorization" not in {k.lower() for k in request.headers}
        return httpx.Response(200, json=SERVICES_PAGE)

    with Client(base_url="https://example.test/v1") as client:
        _mount_sync(client, handler)
        page = client.groups.services("all_services", limit=10)

    assert [s.name for s in page.data] == ["resp200"]


def test_anonymous_authenticated_only_resource_fails_fast() -> None:
    """Account files require credentials, so say so up front rather than
    letting the caller discover it as a 401 mid-upload."""
    with Client(base_url="https://example.test/v1") as client:
        with pytest.raises(AuthenticationError, match="requires an api_key"):
            _ = client.files


def test_anonymous_server_side_401_still_surfaces() -> None:
    """Resources mixing public reads and authenticated writes are left to
    the server, which must still produce a normal SDK error."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Authorization header required"})

    with Client(base_url="https://example.test/v1") as client:
        _mount_sync(client, handler)
        with pytest.raises(AuthenticationError):
            client.groups.list()


def test_from_env_still_demands_a_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """``from_env`` is explicitly the authenticated entry point. Silently
    handing back an anonymous client when the key is missing would turn a
    misconfiguration into confusing empty results."""
    monkeypatch.delenv("UNITYSVC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="UNITYSVC_API_KEY"):
        Client.from_env()


@pytest.mark.asyncio
async def test_async_anonymous_client_sends_no_authorization_header() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=GROUPS_PAGE)

    async with AsyncClient(base_url="https://example.test/v1") as client:
        _mount_async(client, handler)
        page = await client.groups.list()

    assert "authorization" not in {k.lower() for k in seen[0].headers}
    assert [g.name for g in page.data] == ["all_services"]


@pytest.mark.asyncio
async def test_async_anonymous_group_services() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "authorization" not in {k.lower() for k in request.headers}
        return httpx.Response(200, json=SERVICES_PAGE)

    async with AsyncClient(base_url="https://example.test/v1") as client:
        _mount_async(client, handler)
        page = await client.groups.services("all_services")

    assert [s.name for s in page.data] == ["resp200"]
