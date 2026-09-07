"""Unit tests for :class:`unitysvc.request_logs.RequestLogs`.

Focused on how ``start``/``stop`` translate into the generic
``POST /preferences/set`` call (unitysvc#2063) — the "request-log"
preference, with ``truncate_long_message`` mapped to a mode string and
``stop`` mapped to ``value: null``. Listing / detail go through the
generated client and are covered by the generated-client smoke tests.
"""

from __future__ import annotations

import json

import httpx
import pytest

from unitysvc import AsyncClient, Client


def _capturing_transport(captured: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"id": "00000000-0000-0000-0000-000000000000", "email": "u@example.com"})

    return httpx.MockTransport(handler)


def test_start_default_is_truncated() -> None:
    """Default ``truncate_long_message=True`` → mode "truncated"."""
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.request_logs.start()

    assert len(captured) == 1
    assert captured[0].url.path.endswith("/preferences/set")
    body = json.loads(captured[0].content)
    assert body == {"name": "request-log", "value": "truncated"}


def test_start_truncate_true_is_truncated_mode() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.request_logs.start(truncate_long_message=True)

    body = json.loads(captured[0].content)
    assert body == {"name": "request-log", "value": "truncated"}


def test_start_truncate_false_is_complete_mode() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.request_logs.start(truncate_long_message=False)

    body = json.loads(captured[0].content)
    assert body == {"name": "request-log", "value": "complete"}


def test_stop_sends_null_value() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.request_logs.stop()

    assert captured[0].url.path.endswith("/preferences/set")
    body = json.loads(captured[0].content)
    assert body == {"name": "request-log", "value": None}


@pytest.mark.asyncio
async def test_async_start_truncate_false_is_complete_mode() -> None:
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _capturing_transport(captured)
        await client.request_logs.start(truncate_long_message=False)

    body = json.loads(captured[0].content)
    assert body == {"name": "request-log", "value": "complete"}


@pytest.mark.asyncio
async def test_async_stop_sends_null_value() -> None:
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _capturing_transport(captured)
        await client.request_logs.stop()

    body = json.loads(captured[0].content)
    assert body == {"name": "request-log", "value": None}
