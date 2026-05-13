"""Unit tests for :class:`unitysvc.request_logs.RequestLogs`.

Focused on the ``start(truncate_long_message=...)`` query-parameter
behavior. Listing / detail go through the generated client and are
covered by the generated-client smoke tests.
"""

from __future__ import annotations

import httpx
import pytest

from unitysvc import AsyncClient, Client


def _capturing_transport(captured: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={"enabled": True},
        )

    return httpx.MockTransport(handler)


def test_start_default_passes_truncate_long_message_true() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        # Inject a mock transport into the low-level client's httpx session.
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        result = client.request_logs.start()

    assert result.enabled is True
    assert len(captured) == 1
    assert captured[0].url.path.endswith("/request-logs/start")
    assert captured[0].url.params.get("truncate_long_message") == "true"


def test_start_truncate_false_passes_false() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.request_logs.start(truncate_long_message=False)

    assert captured[0].url.params.get("truncate_long_message") == "false"


@pytest.mark.asyncio
async def test_async_start_passes_truncate_long_message() -> None:
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _capturing_transport(captured)
        await client.request_logs.start(truncate_long_message=False)

    assert captured[0].url.params.get("truncate_long_message") == "false"
