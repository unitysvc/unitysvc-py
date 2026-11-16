"""Provisioned rooms are discoverable as typed enrollment resources."""

from uuid import UUID

import httpx
import pytest

from unitysvc import AsyncClient, Client

ENROLLMENT = "11111111-1111-4111-8111-111111111111"
SERVICE = "22222222-2222-4222-8222-222222222222"
ROOM = "33333333-3333-4333-8333-333333333333"
SHARED_ROOM = "44444444-4444-4444-8444-444444444444"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_enrollment_get_and_list_parse_provisioned_room_resources(asynchronous):
    payload = {
        "id": ENROLLMENT,
        "service_id": SERVICE,
        "status": "active",
        "channel": "free",
        "created_at": "2026-10-31T00:00:00Z",
        "updated_at": "2026-10-31T00:00:00Z",
        "resources": [
            {"object": "resource:room", "kind": "chat", "room_id": ROOM},
            {
                "object": "resource:room",
                "kind": "chat",
                "room_id": SHARED_ROOM,
                "name": "Customers of acme",
                "role": "member",
                "scope": "service",
                "open": False,
                "url": "https://unitysvc.com/rooms/" + SHARED_ROOM,
            },
        ],
    }

    def handler(request):
        return httpx.Response(
            200,
            json={"data": [payload], "count": 1, "skip": 0, "limit": 100}
            if request.url.path.endswith("/enrollments/")
            else payload,
        )

    cls = AsyncClient if asynchronous else Client
    client = cls(api_key="svcpass_test", base_url="https://test.example/v1/customer")
    wire = httpx.MockTransport(handler)
    if asynchronous:
        client._client.get_async_httpx_client()._transport = wire
    else:
        client._client.get_httpx_client()._transport = wire
    try:
        if asynchronous:
            enrollment = await client.enrollments.get(ENROLLMENT)
            listed = await client.enrollments.list()
        else:
            enrollment = client.enrollments.get(ENROLLMENT)
            listed = client.enrollments.list()
        for parsed in [enrollment, listed.data[0]]:
            [own, shared] = parsed.resources
            assert own.object_ == "resource:room"
            assert own.kind == "chat"
            assert own.room_id == UUID(ROOM)
            # Fields the server left out stay UNSET and are not re-serialised.
            assert own.to_dict() == payload["resources"][0]
            # An enrollment may admit the customer to further rooms (unitysvc#2969):
            # the seller's, or one the service's customers share.
            assert shared.room_id == UUID(SHARED_ROOM)
            assert shared.name == "Customers of acme"
            assert (shared.role, shared.scope, shared.open_) == ("member", "service", False)
            assert shared.url == "https://unitysvc.com/rooms/" + SHARED_ROOM
            assert shared.to_dict() == payload["resources"][1]
    finally:
        if asynchronous:
            await client.aclose()
        else:
            client.close()
