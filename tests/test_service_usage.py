"""Tests for the derived usage guide and document wrappers (unitysvc#1622/#1617).

Both are anonymous-readable customer-API reads. The wrappers thread the query
params through to the generated client and unwrap the typed response — usage
returns the markdown string; documents returns the ``{interface,
available_interfaces, documents}`` envelope.
"""

from __future__ import annotations

import httpx
import pytest

from unitysvc import AsyncClient, Client

SVC = "32374227-ffe0-5f69-98d5-e6ce97710b67"

USAGE = {"markdown": "## How to use this service\n\nUse it directly."}

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


def test_usage_returns_markdown_and_defaults_to_plain_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == f"/v1/services/{SVC}/usage"
        # Default flavor: links off.
        assert request.url.params.get("links") == "false"
        return httpx.Response(200, json=USAGE)

    with Client(base_url="https://example.test/v1") as client:
        _mount_sync(client, handler)
        md = client.services.usage(SVC)

    assert md.startswith("## How to use this service")


def test_usage_links_flag_is_forwarded() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("links") == "true"
        return httpx.Response(200, json=USAGE)

    with Client(base_url="https://example.test/v1") as client:
        _mount_sync(client, handler)
        client.services.usage(SVC, links=True)


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
async def test_async_usage_returns_markdown() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == f"/v1/services/{SVC}/usage"
        return httpx.Response(200, json=USAGE)

    async with AsyncClient(base_url="https://example.test/v1") as client:
        _mount_async(client, handler)
        md = await client.services.usage(SVC)

    assert "How to use this service" in md
