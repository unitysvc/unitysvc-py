"""Tests for the structured access plan and document wrappers (unitysvc#1638/#1617).

Both are anonymous-readable customer-API reads. The wrappers thread any query
params through to the generated client and unwrap the typed response —
``access_plan`` returns the structured :class:`AccessPlan` (#1638 made the
endpoint serve structure, not prose); ``documents`` returns the ``{interface,
available_interfaces, documents}`` envelope.
"""

from __future__ import annotations

import httpx
import pytest

from unitysvc import AccessPlan, AsyncClient, Client

SVC = "32374227-ffe0-5f69-98d5-e6ce97710b67"

ACCESS_PLAN = {
    "enrollment_mode": "optional",
    "parameters": [
        {"name": "region", "description": "Deployment region", "required": True}
    ],
    "interfaces": [
        {
            "name": "canonical",
            "base_url": "https://gw.test/a/svc",
            "routing_key": {"model": "gpt-4"},
            "description": None,
        }
    ],
    "channels": [
        {
            "name": "managed",
            "channel_type": "managed",
            "free": False,
            "price_description": "$0.01 / call",
            "price": None,
            "currency": None,
            "requires_enrollment": False,
            "required_secrets": [{"name": "OPENAI_API_KEY", "description": "your key"}],
            "optional_secrets": [
                {"name": "ORG", "description": "org id", "default": "default-org"}
            ],
        }
    ],
}

DOCUMENTS = {
    "interface": "canonical",
    "available_interfaces": ["canonical", "latest"],
    "documents": [
        {
            "id": "11111111-1111-4111-8111-111111111111",
            "title": "Python code example",
            "category": "code_example",
            "mime_type": "python",
            "content": "print('hi')",
        }
    ],
}


def _mount_sync(client: Client, handler) -> None:
    client._client.get_httpx_client()._transport = httpx.MockTransport(handler)


def _mount_async(client: AsyncClient, handler) -> None:
    client._client.get_async_httpx_client()._transport = httpx.MockTransport(handler)


def test_access_plan_returns_the_parsed_structured_plan() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == f"/v1/services/{SVC}/usage"
        # #1640 removed the `links` param (rendering moved to clients).
        assert "links" not in request.url.params
        return httpx.Response(200, json=ACCESS_PLAN)

    with Client(base_url="https://example.test/v1") as client:
        _mount_sync(client, handler)
        plan = client.services.access_plan(SVC)

    assert isinstance(plan, AccessPlan)  # also exercises the public re-export
    assert plan.enrollment_mode == "optional"
    assert plan.parameters[0].name == "region"
    assert plan.parameters[0].required is True
    assert plan.interfaces[0].base_url == "https://gw.test/a/svc"
    ch = plan.channels[0]
    assert ch.name == "managed"
    assert ch.price_description == "$0.01 / call"
    assert ch.required_secrets[0].name == "OPENAI_API_KEY"
    assert ch.optional_secrets[0].default == "default-org"


def test_documents_forwards_filters_and_returns_envelope() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == f"/v1/services/{SVC}/documents"
        assert request.url.params.get("category") == "code_example"
        assert request.url.params.get("mime_type") == "python"
        assert request.url.params.get("include_content") == "true"
        return httpx.Response(200, json=DOCUMENTS)

    with Client(base_url="https://example.test/v1") as client:
        _mount_sync(client, handler)
        resp = client.services.documents(
            SVC,
            category="code_example",
            mime_type="python",
            include_content=True,
        )

    assert resp.interface == "canonical"
    assert list(resp.available_interfaces) == ["canonical", "latest"]
    assert [d.title for d in resp.documents] == ["Python code example"]


@pytest.mark.asyncio
async def test_async_access_plan_returns_the_parsed_structured_plan() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == f"/v1/services/{SVC}/usage"
        return httpx.Response(200, json=ACCESS_PLAN)

    async with AsyncClient(base_url="https://example.test/v1") as client:
        _mount_async(client, handler)
        plan = await client.services.access_plan(SVC)

    assert isinstance(plan, AccessPlan)
    assert plan.enrollment_mode == "optional"
    assert plan.channels[0].price_description == "$0.01 / call"
