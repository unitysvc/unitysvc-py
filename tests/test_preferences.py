"""Unit tests for :class:`unitysvc.preferences.Preferences` (unitysvc#2063).

Focused on the wire shape POST /preferences/set actually receives —
mirrors the pattern in ``test_request_logs.py``.
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


def test_set_sends_name_and_value() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.preferences.set("request-log", "truncated")

    assert captured[0].url.path.endswith("/preferences/set")
    assert json.loads(captured[0].content) == {"name": "request-log", "value": "truncated"}


def test_set_default_value_is_null() -> None:
    """Omitting ``value`` clears the preference — same as explicit ``None``."""
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.preferences.set("request-log")

    assert json.loads(captured[0].content) == {"name": "request-log", "value": None}


def test_set_notification_destination_sends_service() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.preferences.set_notification_destination("labs/discord-relay")

    body = json.loads(captured[0].content)
    assert body == {"name": "notification-destination", "value": "labs/discord-relay"}


def test_set_notification_destination_none_clears() -> None:
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _capturing_transport(captured)
        client.preferences.set_notification_destination(None)

    body = json.loads(captured[0].content)
    assert body == {"name": "notification-destination", "value": None}


@pytest.mark.asyncio
async def test_async_set_notification_destination_sends_service() -> None:
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _capturing_transport(captured)
        await client.preferences.set_notification_destination("labs/discord-relay")

    body = json.loads(captured[0].content)
    assert body == {"name": "notification-destination", "value": "labs/discord-relay"}
