"""Unit tests for :class:`unitysvc.preferences.Preferences` (unitysvc#2659).

Focused on the wire shape the account-scoped ``/preferences`` API receives:
the method, the path (which names the preference) and the ``PUT`` body.
"""

from __future__ import annotations

import json

import httpx
import pytest

from unitysvc import AsyncClient, Client

_ACCOUNT = {"type": "user", "id": "00000000-0000-0000-0000-000000000000", "name": "u@example.com"}


def _preference(name: str, value: object = None) -> dict[str, object]:
    return {
        "name": name,
        "account": _ACCOUNT,
        "value": value,
        "effective": value,
        "source": "account",
        "can_edit": True,
    }


def _capturing_transport(captured: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        if request.url.path.rstrip("/").endswith("/preferences"):
            return httpx.Response(200, json={"data": [_preference("ai")]})
        name = request.url.path.rsplit("/", 1)[-1]
        value = json.loads(request.content)["value"] if request.content else None
        return httpx.Response(200, json=_preference(name, value))

    return httpx.MockTransport(handler)


def _client(captured: list[httpx.Request]) -> Client:
    client = Client(api_key="svcpass_test")
    client._client.get_httpx_client()._transport = _capturing_transport(captured)
    return client


def test_set_puts_value_at_the_named_path() -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        result = client.preferences.set("request-log", "truncated")

    assert captured[0].method == "PUT"
    assert captured[0].url.path.endswith("/preferences/request-log")
    assert json.loads(captured[0].content) == {"value": "truncated"}
    assert result.name == "request-log"
    assert result.value == "truncated"


def test_set_accepts_a_service_dict() -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        client.preferences.set("ai", {"service": "labs/llm-balanced"})

    assert json.loads(captured[0].content) == {"value": {"service": "labs/llm-balanced"}}


def test_set_none_clears_with_delete() -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        client.preferences.set("request-log", None)

    assert captured[0].method == "DELETE"
    assert captured[0].url.path.endswith("/preferences/request-log")


def test_clear_deletes() -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        client.preferences.clear("ai")

    assert captured[0].method == "DELETE"
    assert captured[0].url.path.endswith("/preferences/ai")


def test_get_reads_the_named_path() -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        result = client.preferences.get("notification")

    assert captured[0].method == "GET"
    assert captured[0].url.path.endswith("/preferences/notification")
    assert result.name == "notification"
    assert result.account.name == "u@example.com"


def test_list_reads_every_preference() -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        result = client.preferences.list()

    assert captured[0].method == "GET"
    assert captured[0].url.path.rstrip("/").endswith("/preferences")
    assert [p.name for p in result.data] == ["ai"]


@pytest.mark.parametrize(
    ("method", "name"),
    [("set_notification", "notification"), ("set_ai", "ai")],
)
def test_service_conveniences_put_the_service(method: str, name: str) -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        getattr(client.preferences, method)("labs/discord-relay")

    assert captured[0].method == "PUT"
    assert captured[0].url.path.endswith(f"/preferences/{name}")
    assert json.loads(captured[0].content) == {"value": "labs/discord-relay"}


@pytest.mark.parametrize(
    ("method", "name"),
    [("set_notification", "notification"), ("set_ai", "ai"), ("set_request_log_mode", "request-log")],
)
def test_conveniences_clear_with_none(method: str, name: str) -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        getattr(client.preferences, method)(None)

    assert captured[0].method == "DELETE"
    assert captured[0].url.path.endswith(f"/preferences/{name}")


def test_set_request_log_mode_complete() -> None:
    captured: list[httpx.Request] = []
    with _client(captured) as client:
        client.preferences.set_request_log_mode("complete")

    assert captured[0].url.path.endswith("/preferences/request-log")
    assert json.loads(captured[0].content) == {"value": "complete"}


@pytest.mark.asyncio
async def test_async_set_and_clear() -> None:
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _capturing_transport(captured)
        result = await client.preferences.set_ai("labs/llm-balanced")
        await client.preferences.set_request_log_mode(None)

    assert (captured[0].method, captured[0].url.path.rsplit("/", 1)[-1]) == ("PUT", "ai")
    assert json.loads(captured[0].content) == {"value": "labs/llm-balanced"}
    assert result.value == "labs/llm-balanced"
    assert (captured[1].method, captured[1].url.path.rsplit("/", 1)[-1]) == ("DELETE", "request-log")


@pytest.mark.asyncio
async def test_async_list_and_get() -> None:
    captured: list[httpx.Request] = []
    async with AsyncClient(api_key="svcpass_test") as client:
        client._client.get_async_httpx_client()._transport = _capturing_transport(captured)
        listed = await client.preferences.list()
        one = await client.preferences.get("ai")

    assert [p.name for p in listed.data] == ["ai"]
    assert one.name == "ai"
    assert [r.method for r in captured] == ["GET", "GET"]
