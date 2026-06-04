"""Unit tests for :class:`unitysvc.chains.Chains` and the :class:`Chain` wrapper.

Exercises the customer request-chain surface against a mocked ``httpx``
transport: the ``{data, count}`` envelope ``list`` shape, a ``create``
round-trip that serializes steps, and ``Chain.dispatch`` hitting the
gateway ``/c/<name>`` path. Mirrors the harness in ``test_groups.py``.
"""

from __future__ import annotations

import json
import uuid

import httpx
import pytest

from unitysvc import AsyncClient, Client


def _chain_public(name: str, *, steps: list[dict] | None = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "customer_id": str(uuid.uuid4()),
        "name": name,
        "default_timeout_ms": 10000,
        "enabled": True,
        "created_at": "2026-01-01T00:00:00+00:00",
        "steps": steps or [],
    }


def _envelope_transport(payload: list[dict], captured: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"data": payload, "count": len(payload)})

    return httpx.MockTransport(handler)


def test_list_returns_envelope_wrapped_in_page() -> None:
    payload = [_chain_public("llm-failover"), _chain_public("rag-flow")]
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _envelope_transport(payload, captured)
        page = client.chains.list()

    assert page.count == 2
    assert {c.name for c in page.data} == {"llm-failover", "rag-flow"}
    assert captured[0].url.path.rstrip("/").endswith("/chains")


def test_create_serializes_steps() -> None:
    created = _chain_public("llm-failover")
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(201, json=created)

    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = httpx.MockTransport(handler)
        chain = client.chains.create(
            name="llm-failover",
            steps=[
                {"name": "primary", "target_path": "anthropic", "on_failure": "continue"},
                {"name": "backup", "target_path": "openai", "on_success": "stop"},
            ],
        )

    assert chain.name == "llm-failover"
    assert chain.path == "c/llm-failover"
    assert captured[0].method == "POST"
    assert captured[0].url.path.rstrip("/").endswith("/chains")
    body = json.loads(captured[0].content)
    assert body["name"] == "llm-failover"
    assert [s["name"] for s in body["steps"]] == ["primary", "backup"]
    # sort_order is auto-assigned from list position when omitted.
    assert [s["sort_order"] for s in body["steps"]] == [0, 1]
    assert body["steps"][0]["on_failure"] == "continue"


def test_dispatch_posts_to_chain_path() -> None:
    chain = _chain_public("llm-failover")
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        if request.url.path.endswith(f"/chains/{chain['id']}"):
            return httpx.Response(200, json=chain)
        return httpx.Response(200, json={"ok": True})

    with Client(api_key="svcpass_test", api_base_url="https://gw.test") as client:
        client._client.get_httpx_client()._transport = httpx.MockTransport(handler)
        ch = client.chains.get(chain["id"])
        resp = ch.dispatch(json={"messages": []})

    assert resp.status_code == 200
    dispatch_req = captured[-1]
    assert dispatch_req.method == "POST"
    assert str(dispatch_req.url) == "https://gw.test/c/llm-failover"


@pytest.mark.asyncio
async def test_async_list_returns_envelope() -> None:
    payload = [_chain_public("llm-failover")]
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _envelope_transport(payload, captured)
        page = await client.chains.list()

    assert page.count == 1
    assert page.data[0].name == "llm-failover"
    assert page.data[0].path == "c/llm-failover"
