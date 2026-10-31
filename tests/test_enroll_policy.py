"""``enrollments.create`` sends the channel and the approved access policy
(unitysvc#2846): a customer approves a channel's ``customer_access_requests``
— for example a ``resource:room`` — when enrolling."""

from __future__ import annotations

import inspect
import json

import httpx
import pytest

from unitysvc import AsyncClient, Client

SERVICE = "11111111-1111-4111-8111-111111111111"
ENROLLMENT = "22222222-2222-4222-8222-222222222222"
ROOM_REQUEST = {"object": "resource:room", "permissions": ["create"], "options": "kind=chat&max_members=3"}


def _client(asynchronous: bool, captured: list[httpx.Request]) -> Client | AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            202,
            json={
                "id": ENROLLMENT,
                "service_id": SERVICE,
                "channel": "default",
                "status": "pending",
                "task_id": "t1",
                "message": "queued",
            },
        )

    cls = AsyncClient if asynchronous else Client
    client = cls(api_key="svcpass_test", base_url="https://test.example/v1/customer")
    wire = httpx.MockTransport(handler)
    if asynchronous:
        client._client.get_async_httpx_client()._transport = wire
    else:
        client._client.get_httpx_client()._transport = wire
    return client


async def _call(client: Client | AsyncClient, **kwargs: object) -> object:
    result = client.enrollments.create(service_id=SERVICE, **kwargs)
    return await result if inspect.isawaitable(result) else result


async def _close(client: Client | AsyncClient) -> None:
    result = client.aclose() if isinstance(client, AsyncClient) else client.close()
    if inspect.isawaitable(result):
        await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_channel_and_policy_reach_the_request(asynchronous: bool) -> None:
    captured: list[httpx.Request] = []
    client = _client(asynchronous, captured)
    try:
        enrollment = await _call(client, channel="free", policy=[ROOM_REQUEST], parameters={"plan": "a"})
        assert str(enrollment.id) == ENROLLMENT  # type: ignore[attr-defined]
        assert json.loads(captured[-1].content) == {
            "service_id": SERVICE,
            "parameters": {"plan": "a"},
            "channel": "free",
            "policy": [ROOM_REQUEST],
        }
        # An explicit empty policy declines every optional request.
        await _call(client, policy=[])
        assert json.loads(captured[-1].content) == {"service_id": SERVICE, "policy": []}
        # Omitted, nothing extra is sent: the backend's defaults apply.
        await _call(client)
        assert json.loads(captured[-1].content) == {"service_id": SERVICE}
    finally:
        await _close(client)
