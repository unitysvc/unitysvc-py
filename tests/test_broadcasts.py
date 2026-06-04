"""Unit tests for :class:`unitysvc.broadcasts.Broadcasts` and the :class:`Broadcast` wrapper.

Exercises the customer broadcast surface against a mocked ``httpx``
transport: the ``{data, count}`` envelope ``list`` shape, a ``create``
round-trip that serializes targets, and ``Broadcast.dispatch`` hitting
the gateway ``/b/<name>`` path. Mirrors the harness in ``test_groups.py``.
"""

from __future__ import annotations

import json
import uuid

import httpx
import pytest

from unitysvc import AsyncClient, Client


def _broadcast_public(name: str, *, mode: str = "sync", targets: list[dict] | None = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "customer_id": str(uuid.uuid4()),
        "name": name,
        "mode": mode,
        "target_timeout_ms": 30000,
        "enabled": True,
        "created_at": "2026-01-01T00:00:00+00:00",
        "targets": targets or [],
    }


def _envelope_transport(payload: list[dict], captured: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"data": payload, "count": len(payload)})

    return httpx.MockTransport(handler)


def test_list_returns_envelope_wrapped_in_page() -> None:
    payload = [_broadcast_public("eval-fanout"), _broadcast_public("mirror", mode="async")]
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _envelope_transport(payload, captured)
        page = client.broadcasts.list()

    assert page.count == 2
    assert {b.name for b in page.data} == {"eval-fanout", "mirror"}
    assert captured[0].url.path.rstrip("/").endswith("/broadcasts")


def test_create_serializes_targets() -> None:
    created = _broadcast_public("eval-fanout")
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(201, json=created)

    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = httpx.MockTransport(handler)
        bc = client.broadcasts.create(
            name="eval-fanout",
            mode="sync",
            targets=[
                {"name": "anthropic", "target_path": "anthropic"},
                {"name": "openai", "target_path": "openai"},
            ],
        )

    assert bc.name == "eval-fanout"
    assert bc.path == "b/eval-fanout"
    assert captured[0].method == "POST"
    assert captured[0].url.path.rstrip("/").endswith("/broadcasts")
    body = json.loads(captured[0].content)
    assert body["name"] == "eval-fanout"
    assert body["mode"] == "sync"
    assert [t["name"] for t in body["targets"]] == ["anthropic", "openai"]
    assert [t["sort_order"] for t in body["targets"]] == [0, 1]


def test_dispatch_posts_to_broadcast_path() -> None:
    bc = _broadcast_public("eval-fanout")
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        if request.url.path.endswith(f"/broadcasts/{bc['id']}"):
            return httpx.Response(200, json=bc)
        return httpx.Response(200, json={"ok": True})

    with Client(api_key="svcpass_test", api_base_url="https://gw.test") as client:
        client._client.get_httpx_client()._transport = httpx.MockTransport(handler)
        obj = client.broadcasts.get(bc["id"])
        resp = obj.dispatch(json={"messages": []})

    assert resp.status_code == 200
    dispatch_req = captured[-1]
    assert dispatch_req.method == "POST"
    assert str(dispatch_req.url) == "https://gw.test/b/eval-fanout"


@pytest.mark.asyncio
async def test_async_list_returns_envelope() -> None:
    payload = [_broadcast_public("eval-fanout")]
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _envelope_transport(payload, captured)
        page = await client.broadcasts.list()

    assert page.count == 1
    assert page.data[0].name == "eval-fanout"
    assert page.data[0].path == "b/eval-fanout"
