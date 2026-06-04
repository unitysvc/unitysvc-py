"""Unit tests for :class:`unitysvc.groups.Groups`.

Exercises the customer service-collections surface against a mocked
``httpx`` transport: the ``{data, count}`` envelope ``list`` shape,
the client-side ``name`` filter, and a ``create`` round-trip. Mirrors
the ``httpx.MockTransport`` harness used by ``test_request_logs.py``.
"""

from __future__ import annotations

import json
import uuid

import httpx
import pytest

from unitysvc import AsyncClient, Client


def _group_view(name: str, *, owner_type: str = "platform", editable: bool = False) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "display_name": name.title(),
        "owner_type": owner_type,
        "editable": editable,
        "member_count": 0,
    }


def _list_transport(payload: list[dict], captured: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"data": payload, "count": len(payload)})

    return httpx.MockTransport(handler)


# ---------------------------------------------------------------------------
# list — {data, count} envelope + owner param + client-side name filter
# ---------------------------------------------------------------------------
def test_list_returns_envelope_wrapped_in_page() -> None:
    payload = [_group_view("llm"), _group_view("embeddings")]
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _list_transport(payload, captured)
        page = client.groups.list()

    # {data, count} envelope → wrapped as GroupListPage{data, count}.
    assert page.count == 2
    assert {g.name for g in page.data} == {"llm", "embeddings"}
    assert captured[0].url.path.endswith("/groups")
    # Default owner filter is sent.
    assert captured[0].url.params.get("owner") == "all"


def test_list_owner_param_forwarded() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _list_transport([], captured)
        client.groups.list(owner="own")

    assert captured[0].url.params.get("owner") == "own"


def test_list_name_is_client_side_substring_filter() -> None:
    payload = [_group_view("llm-fast"), _group_view("embeddings"), _group_view("llm-cheap")]
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _list_transport(payload, captured)
        page = client.groups.list(name="llm")

    assert page.count == 2
    assert all("llm" in g.name for g in page.data)
    # name is NOT sent as a query param — it's applied locally.
    assert "name" not in captured[0].url.params


# ---------------------------------------------------------------------------
# create — round-trip
# ---------------------------------------------------------------------------
def test_create_round_trip() -> None:
    created = _group_view("my-collection", owner_type="customer", editable=True)
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(201, json=created)

    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = httpx.MockTransport(handler)
        group = client.groups.create(
            name="my-collection",
            display_name="My Collection",
            description="a curated set",
        )

    assert group.name == "my-collection"
    assert group.editable is True
    assert captured[0].method == "POST"
    assert captured[0].url.path.endswith("/groups")
    body = json.loads(captured[0].content)
    assert body["name"] == "my-collection"
    assert body["display_name"] == "My Collection"
    assert body["description"] == "a curated set"


def test_group_wrapper_binds_membership_ops() -> None:
    """The Group active-record binds add_member/members/remove_member to its id."""
    grp = _group_view("my-collection", owner_type="customer", editable=True)
    service_id = str(uuid.uuid4())
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        if request.method == "POST" and request.url.path.rstrip("/").endswith(f"/{grp['id']}/members"):
            return httpx.Response(
                201,
                json={"id": str(uuid.uuid4()), "service_id": service_id, "routing_key": None, "sort_order": 0},
            )
        return httpx.Response(200, json=grp)

    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = httpx.MockTransport(handler)
        group = client.groups.get("my-collection")
        member = group.add_member(service_id=service_id)

    # add_member pre-binds this group's id into the request path.
    assert str(member.service_id) == service_id
    add_req = captured[-1]
    assert add_req.method == "POST"
    assert add_req.url.path.rstrip("/").endswith(f"/{grp['id']}/members")


@pytest.mark.asyncio
async def test_async_list_returns_envelope() -> None:
    payload = [_group_view("llm")]
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _list_transport(payload, captured)
        page = await client.groups.list()

    assert page.count == 1
    assert page.data[0].name == "llm"
    assert captured[0].url.params.get("owner") == "all"
