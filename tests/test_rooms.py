"""Room facade wire contracts and typed parsing, through real generated clients."""

import inspect
import json
from uuid import UUID

import httpx
import pytest

from unitysvc import AsyncClient, Client
from unitysvc.exceptions import NotFoundError

ROOM = "11111111-1111-4111-8111-111111111111"
MEMBER = "22222222-2222-4222-8222-222222222222"
CODE = "33333333-3333-4333-8333-333333333333"
MESSAGE = "44444444-4444-4444-8444-444444444444"
AT = "2026-10-30T00:00:00Z"


def summary(**overrides):
    return {
        "id": ROOM,
        "member_id": MEMBER,
        "kind": "helpdesk",
        "name": "Help desk",
        "handle": "helpdesk",
        "status": "active",
        "role": "owner",
        "created_at": AT,
        "description": "Talk with **support**",
        "owner_name": "Acme",
        "keep_forever": True,
        "fixed_membership": True,
        "can_manage": True,
        "delivery_state": "inbox",
        **overrides,
    }


def invitation():
    return {
        "id": CODE,
        "token": "ABCDEF",
        "role": "member",
        "status": "active",
        "use_count": 0,
        "max_uses": 3,
        "expires_at": AT,
        "created_at": AT,
    }


def connector(**overrides):
    return {
        "id": CODE,
        "name": "main",
        "notify": "notify",
        "email": None,
        "post": None,
        "inbound_url": None,
        **overrides,
    }


def command(**overrides):
    return {
        "name": "allow",
        "syntax": "!allow $<amount>[/month]",
        "example": "!allow $6",
        "summary": "Allow charges up to an amount",
        "sender": "customer",
        "effect": "consent",
        "pattern": r"^!allow \\$(?P<amount>\\d+)$",
        **overrides,
    }


def body_of(request):
    return json.loads(request.content) if request.content else None


def transport(captured):
    def handler(request):
        captured.append(request)
        path = request.url.path
        if path.endswith("/missing"):
            return httpx.Response(404, json={"detail": "Room not found"})
        if path.endswith("/rooms/commands"):
            return httpx.Response(200, json={"data": [command()]})
        if path.endswith("/commands"):
            return httpx.Response(
                200,
                json={
                    "data": [
                        command(available=True, code=None, reason=None),
                        command(name="charge", syntax="!charge $<amount>", available=False, reason="Sellers only"),
                    ]
                },
            )
        if path.endswith("/delivery"):
            return httpx.Response(200, json={"connectors": [connector()], "can_edit": True})
        if path.endswith("/connectors"):
            sent = body_of(request)
            return httpx.Response(201, json={"connectors": [connector(), connector(**sent)], "can_edit": True})
        if "/connectors/" in path:
            changed = connector(**(body_of(request) or {}))
            return httpx.Response(
                200, json={"connectors": [] if request.method == "DELETE" else [changed], "can_edit": True}
            )
        if path.endswith("/live/accepting"):
            lease = {"client_id": body_of(request).get("client_id") or "c-new", "expires_in": 60}
            return httpx.Response(200, json=lease)
        if (
            path.endswith("/live/accepting/stop")
            or path.endswith("/live/request/cancel")
            or path.endswith("/live/resolve")
        ):
            return httpx.Response(204)
        if path.endswith("/live/waiting"):
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "room_id": ROOM,
                            "handle": "acme",
                            "generation": "g1",
                            "first_requested_at": AT,
                            "requesters": 2,
                        }
                    ]
                },
            )
        if path.endswith("/live/request"):
            sent = body_of(request)
            return httpx.Response(
                200,
                json={
                    "target_member_id": sent["target_member_id"],
                    "generation": sent.get("generation") or "g1",
                    "client_id": sent.get("client_id") or "c-new",
                    "first_requested_at": AT,
                    "available": False,
                    "state": "draining",
                },
            )
        if path.endswith("/live"):
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "member_id": MEMBER,
                            "account_type": "seller",
                            "name": "Tailor",
                            "available": True,
                            "state": "accepting",
                            "request": {
                                "generation": "g1",
                                "first_requested_at": AT,
                                "requesters": 1,
                                "mine": True,
                                "position": 1,
                            },
                        }
                    ]
                },
            )
        if path.endswith("/work/next") or path.endswith("/work/claim"):
            return httpx.Response(200, json={"room_id": ROOM, "handle": "acme", "claim_token": "t1", "expires_in": 60})
        if path.endswith("/work/return-later") or path.endswith("/attention/done"):
            return httpx.Response(
                200, json={"attention_pending": path.endswith("/return-later"), "attention_since": AT}
            )
        if path.endswith("/codes"):
            return httpx.Response(
                201 if request.method == "POST" else 200,
                json=invitation() if request.method == "POST" else {"data": [invitation()]},
            )
        if "/codes/" in path:
            return httpx.Response(200, json={**invitation(), "status": "revoked"})
        if path.endswith("/members"):
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": MEMBER,
                            "account_type": "customer",
                            "account_id": ROOM,
                            "name": "Acme",
                            "role": "owner",
                            "joined_at": AT,
                        }
                    ]
                },
            )
        if path.endswith("/join"):
            return httpx.Response(200, json=summary())
        if path.endswith("/leave"):
            return httpx.Response(204)
        if path.endswith("/feed"):
            return httpx.Response(
                200,
                json={
                    "messages": [
                        {
                            "id": MESSAGE,
                            "offset": 7,
                            "sent_at": AT,
                            "sender_type": "customer",
                            "sender_member_id": MEMBER,
                            "sender_name": "Ann",
                            "via": None,
                            "origin_service": None,
                            "origin_author": None,
                            "reply_to_id": None,
                            "event": None,
                            "event_data": None,
                            "title": None,
                            "body": "hi",
                            "type": "info",
                            "format": "text",
                            "links": [],
                            "attachments": [],
                            "is_internal": False,
                            "is_system": False,
                            "room_id": ROOM,
                        }
                    ],
                    "cursor": "c2",
                    "rooms_with_new_activity": 1,
                },
            )
        if path.endswith("/unread"):
            return httpx.Response(200, json={"rooms_with_new_activity": 2})
        if path.endswith("/active"):
            offset = json.loads(request.content)["offset"]
            return httpx.Response(200, json={"last_active_offset": offset, "capped": False})
        if path.endswith("/follow-up"):
            return httpx.Response(200, json=json.loads(request.content))
        if request.method == "POST":
            posted = {"room_id": ROOM, "message_id": MESSAGE, "offset": 42, "routed": "handle", "command": None}
            if body_of(request).get("body", "").startswith("!"):
                posted["command"] = {
                    "status": "executed",
                    "name": "allow",
                    "message": "You allowed charges up to $6.00",
                    "answer_message_id": CODE,
                }
            return httpx.Response(202, json=posted)
        if request.method == "PATCH":
            return httpx.Response(200, json=summary(**json.loads(request.content)))
        if path.endswith("/rooms"):
            return httpx.Response(200, json={"data": [summary()]})
        return httpx.Response(200, json={**summary(), "messages": {"data": [], "next": 41}})

    return httpx.MockTransport(handler)


def client_for(asynchronous, captured):
    cls = AsyncClient if asynchronous else Client
    client = cls(api_key="svcpass_test", base_url="https://test.example/v1/customer")
    if asynchronous:
        client._client.get_async_httpx_client()._transport = transport(captured)
    else:
        client._client.get_httpx_client()._transport = transport(captured)
    return client


async def call(resource, method, *args, **kwargs):
    result = getattr(resource, method)(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result


async def close(client, asynchronous):
    if asynchronous:
        await client.aclose()
    else:
        client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("owner_sets_retention", [False, True])
async def test_indefinite_room_retention_policy_is_typed(asynchronous, owner_sets_retention):
    captured = []
    client = client_for(asynchronous, captured)
    policy = summary(
        kind="helpdesk" if not owner_sets_retention else "discussion",
        retention_seconds=None,
        max_retention_seconds=None,
        owner_sets_retention=owner_sets_retention,
    )

    def handler(request):
        captured.append(request)
        return httpx.Response(
            200,
            json={"data": [policy]}
            if request.url.path.endswith("/rooms")
            else {**policy, "messages": {"data": [], "next": None}},
        )

    wire = httpx.MockTransport(handler)
    if asynchronous:
        client._client.get_async_httpx_client()._transport = wire
    else:
        client._client.get_httpx_client()._transport = wire
    try:
        room = await call(client.rooms, "get", ROOM)
        listed = await call(client.rooms, "list")
        for parsed in [room, listed.data[0]]:
            assert parsed.retention_seconds is None
            assert parsed.max_retention_seconds is None
            assert parsed.owner_sets_retention is owner_sets_retention
            assert parsed.keep_forever is True
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_room_delivery_is_a_list_of_connectors(asynchronous):
    """Delivery is read as connectors (unitysvc#2896) and changed one
    connector at a time; a channel left out of an update is kept, None
    turns it off, and the deprecated ``default`` flag is never sent."""
    captured = []
    client = client_for(asynchronous, captured)
    try:
        delivery = await call(client.rooms, "delivery", ROOM)
        assert delivery.can_edit is True
        assert [(c.name, c.notify, c.email) for c in delivery.connectors] == [("main", "notify", None)]

        added = await call(client.rooms, "add_connector", ROOM, "discord", notify="labs/msg-to-discord", email=None)
        assert captured[-1].method == "POST"
        assert captured[-1].url.path.endswith(f"/rooms/{ROOM}/connectors")
        assert json.loads(captured[-1].content) == {"name": "discord", "notify": "labs/msg-to-discord"}
        assert [c.name for c in added.connectors] == ["main", "discord"]

        updated = await call(client.rooms, "update_connector", ROOM, "discord", email="email", post=None)
        assert captured[-1].method == "PATCH"
        assert captured[-1].url.path.endswith(f"/rooms/{ROOM}/connectors/discord")
        assert json.loads(captured[-1].content) == {"email": "email", "post": None}
        assert updated.connectors[0].email == "email" and updated.connectors[0].post is None

        removed = await call(client.rooms, "remove_connector", ROOM, "discord")
        assert captured[-1].method == "DELETE"
        assert captured[-1].url.path.endswith(f"/rooms/{ROOM}/connectors/discord")
        assert removed.connectors == []
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_commands_are_listed_and_a_command_post_reports_its_outcome(asynchronous):
    """The registry (unitysvc#2904) and its availability in a room; a post
    whose first line is a command carries what it did."""
    captured = []
    client = client_for(asynchronous, captured)
    try:
        everything = await call(client.rooms, "commands")
        assert [c.name for c in everything.data] == ["allow"]
        assert everything.data[0].pattern.startswith("^!allow")
        here = await call(client.rooms, "available_commands", "helpdesk")
        assert [(c.name, c.available, c.reason) for c in here.data] == [
            ("allow", True, None),
            ("charge", False, "Sellers only"),
        ]
        posted = await call(client.rooms, "post", "helpdesk", body="!allow $6", fallback=False)
        assert posted.command.status == "executed"
        assert posted.command.message == "You allowed charges up to $6.00"
        assert str(posted.command.answer_message_id) == CODE
        plain = await call(client.rooms, "post", "helpdesk", body="hi")
        assert plain.command is None
    finally:
        await close(client, asynchronous)
    assert [r.url.path.rsplit("/rooms", 1)[1] for r in captured[:2]] == ["/commands", "/helpdesk/commands"]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_live_help_reaches_the_wire(asynchronous):
    """The traffic light (unitysvc#2926): accepting leases, the waiting list,
    a room's status, and requesting, cancelling and resolving help."""
    captured = []
    client = client_for(asynchronous, captured)
    try:
        lease = await call(client.rooms, "accept_live_requests")
        assert lease.client_id == "c-new" and lease.expires_in == 60
        await call(client.rooms, "accept_live_requests", client_id="c-new", mode="draining")
        assert await call(client.rooms, "stop_accepting_live_requests", client_id="c-new") is None
        waiting = await call(client.rooms, "live_waiting")
        assert (str(waiting.data[0].room_id), waiting.data[0].requesters) == (ROOM, 2)
        status = await call(client.rooms, "live_status", "acme")
        party = status.data[0]
        assert (party.state, party.available, party.request.mine, party.request.position) == (
            "accepting",
            True,
            True,
            1,
        )
        asked = await call(client.rooms, "request_live_help", "acme", party)
        assert (asked.generation, asked.client_id, asked.state, asked.available) == ("g1", "c-new", "draining", False)
        await call(client.rooms, "request_live_help", "acme", MEMBER, client_id="c-new", generation="g1")
        assert await call(client.rooms, "cancel_live_help", "acme", MEMBER, client_id="c-new") is None
        assert await call(client.rooms, "resolve_live_help", "acme", generation="g1") is None
        await call(client.rooms, "resolve_live_help", "acme")
    finally:
        await close(client, asynchronous)

    assert [
        (r.method, r.url.path.rsplit("/rooms", 1)[1], json.loads(r.content) if r.content else None) for r in captured
    ] == [
        ("POST", "/live/accepting", {"client_id": None, "mode": "accepting"}),
        ("POST", "/live/accepting", {"client_id": "c-new", "mode": "draining"}),
        ("POST", "/live/accepting/stop", {"client_id": "c-new"}),
        ("GET", "/live/waiting", None),
        ("GET", "/acme/live", None),
        ("POST", "/acme/live/request", {"target_member_id": MEMBER, "client_id": None, "generation": None}),
        ("POST", "/acme/live/request", {"target_member_id": MEMBER, "client_id": "c-new", "generation": "g1"}),
        ("POST", "/acme/live/request/cancel", {"target_member_id": MEMBER, "client_id": "c-new"}),
        ("POST", "/acme/live/resolve", {"generation": "g1"}),
        ("POST", "/acme/live/resolve", {"generation": None}),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_work_queue_reaches_the_wire(asynchronous):
    """Next, claims, Return later and Done (unitysvc#2929)."""
    captured = []
    client = client_for(asynchronous, captured)
    try:
        claim = await call(client.rooms, "next_room")
        assert (str(claim.room_id), claim.handle, claim.claim_token) == (ROOM, "acme", "t1")
        renewed = await call(client.rooms, "renew_claim", "acme", "t1")
        assert renewed.claim_token == "t1"
        # The previous claim completes the room it holds, through what was shown.
        await call(client.rooms, "next_room", claim, offset=42)
        await call(client.rooms, "next_room", ROOM, claim_token="t2")
        later = await call(client.rooms, "return_later", "acme", claim_token="t1")
        assert later.attention_pending is True
        done = await call(client.rooms, "mark_done", "acme", 42)
        assert done.attention_pending is False
    finally:
        await close(client, asynchronous)

    assert [(r.method, r.url.path.rsplit("/rooms", 1)[1], json.loads(r.content)) for r in captured] == [
        ("POST", "/work/next", {}),
        ("POST", "/acme/work/claim", {"claim_token": "t1"}),
        ("POST", "/work/next", {"current": {"room_id": ROOM, "claim_token": "t1", "offset": 42}}),
        ("POST", "/work/next", {"current": {"room_id": ROOM, "claim_token": "t2"}}),
        ("POST", "/acme/work/return-later", {"claim_token": "t1"}),
        ("POST", "/acme/attention/done", {"offset": 42}),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_mentions_closed_rooms_and_origin(asynchronous):
    """post() sends mentions as member ids (from ids or member rows), list()
    sends include_closed, and a room's origin, attention and closed_reason
    are typed."""
    from types import SimpleNamespace

    captured = []
    client = client_for(asynchronous, captured)
    listed = {
        **summary(),
        "closed_reason": "enrollment_paused",
        "attention_pending": True,
        "attention_since": AT,
        "origin": {
            "service": {"id": CODE, "name": "tailor/alterations", "display_name": "Alterations"},
            "enrollments": [{"id": MEMBER, "code": "E-1", "status": "paused"}],
        },
    }
    try:
        await call(client.rooms, "post", "helpdesk", body="@staff please", mentions=[MEMBER, SimpleNamespace(id=CODE)])
        assert json.loads(captured[-1].content)["mentions"] == [MEMBER, CODE]

        client_transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"data": [listed]}))
        if asynchronous:
            client._client.get_async_httpx_client()._transport = client_transport
        else:
            client._client.get_httpx_client()._transport = client_transport
        rooms = await call(client.rooms, "list", include_closed=True)
        room = rooms.data[0]
        assert room.closed_reason == "enrollment_paused"
        assert room.attention_pending is True
        assert room.origin.service.name == "tailor/alterations"
        assert room.origin.enrollments[0].code == "E-1"
    finally:
        await close(client, asynchronous)
    assert captured[0].url.path.endswith("/rooms/helpdesk")


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_room_metadata_management_and_private_members(asynchronous):
    captured = []
    client = client_for(asynchronous, captured)
    try:
        listed = await call(client.rooms, "list", kind="helpdesk")
        assert listed.data[0].owner_name == "Acme"
        room = await call(client.rooms, "get", "helpdesk", after=40, limit=20)
        assert room.description == "Talk with **support**"
        assert room.messages.next_ == 41
        changed = await call(client.rooms, "update", ROOM, description="# Our support", name="Support")
        assert changed.description == "# Our support"
        assert changed.name == "Support"
        await call(client.rooms, "update", ROOM, description=None)
        members = await call(client.rooms, "members", ROOM)
        assert members.data[0].name == "Acme"
        assert captured[0].url.params["kind"] == "helpdesk"
        assert captured[1].url.params["after"] == "40"
        assert json.loads(captured[2].content) == {"name": "Support", "description": "# Our support"}
        assert json.loads(captured[3].content) == {"description": None}
        assert captured[2].method == "PATCH"
        assert captured[4].url.path.endswith(f"/rooms/{ROOM}/members")
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_invitation_lifecycle_and_posting(asynchronous):
    captured = []
    client = client_for(asynchronous, captured)
    try:
        code = await call(client.rooms, "create_invitation", ROOM, role="member", max_uses=3)
        assert code.token == "ABCDEF"
        codes = await call(client.rooms, "invitations", ROOM, include_inactive=True)
        assert len(codes.data) == 1
        joined = await call(client.rooms, "join", "ABCDEF")
        assert str(joined.id) == ROOM
        revoked = await call(client.rooms, "revoke_invitation", ROOM, CODE)
        assert revoked.status == "revoked"
        posted = await call(client.rooms, "post", "helpdesk", body="Help", client_message_id="test-1")
        assert posted.offset == 42
        await call(client.rooms, "post", body="@helpdesk Help")
        assert captured[3].method == "DELETE"
        assert captured[4].url.path.endswith("/rooms/helpdesk")
        assert captured[5].url.path.endswith("/rooms")
        assert json.loads(captured[4].content)["client_message_id"] == "test-1"
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_room_errors_are_sdk_errors(asynchronous):
    client = client_for(asynchronous, [])
    try:
        with pytest.raises(NotFoundError):
            await call(client.rooms, "get", "missing")
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_owner_status_reaches_the_wire(asynchronous):
    """rooms.update sends the owner's operational status (#2843 S5b)."""
    captured = []
    client = client_for(asynchronous, captured)
    try:
        changed = await call(client.rooms, "update", ROOM, status="readonly")
        assert json.loads(captured[-1].content) == {"status": "readonly"}
        assert changed.status == "readonly"
        await call(client.rooms, "update", ROOM, status="active")
        assert json.loads(captured[-1].content) == {"status": "active"}
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_rooms_narrow_by_enrollment_and_service_and_leave(asynchronous):
    """list() sends the scope filters, from an id or an SDK object, and
    leave() posts to the room's leave route (unitysvc#2846 C2, C6)."""
    captured = []
    client = client_for(asynchronous, captured)
    enrollment = "22222222-2222-4222-8222-222222222222"
    service = "33333333-3333-4333-8333-333333333333"

    class _Holder:
        id = service

    try:
        listed = await call(client.rooms, "list", kind="chat", enrollment=enrollment)
        assert listed.data[0].id == UUID(ROOM)
        assert dict(captured[-1].url.params) == {"kind": "chat", "enrollment": enrollment}
        await call(client.rooms, "list", service=_Holder())
        assert dict(captured[-1].url.params) == {"service": service}
        await call(client.rooms, "list")
        assert dict(captured[-1].url.params) == {}

        assert await call(client.rooms, "leave", ROOM) is None
        assert captured[-1].method == "POST"
        assert captured[-1].url.path.endswith(f"/rooms/{ROOM}/leave")
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_an_enrollment_lists_its_rooms(asynchronous):
    """enrollment.rooms() is client.rooms.list narrowed to the enrollment."""
    from types import SimpleNamespace

    from unitysvc.aenrollments import AsyncEnrollment
    from unitysvc.enrollments import Enrollment

    captured = []
    client = client_for(asynchronous, captured)
    enrollment_id = UUID("22222222-2222-4222-8222-222222222222")
    wrapper = (AsyncEnrollment if asynchronous else Enrollment)(SimpleNamespace(id=enrollment_id), parent=client)
    try:
        listed = await call(wrapper, "rooms", kind="chat")
        assert listed.data[0].id == UUID(ROOM)
        assert dict(captured[-1].url.params) == {"kind": "chat", "enrollment": str(enrollment_id)}
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_unread_active_and_follow_up_reach_the_wire(asynchronous):
    captured = []
    client = client_for(asynchronous, captured)
    try:
        assert (await call(client.rooms, "unread")).rooms_with_new_activity == 2
        marked = await call(client.rooms, "mark_active", "helpdesk", 42)
        assert (marked.last_active_offset, marked.capped) == (42, False)
        assert (await call(client.rooms, "set_follow_up", "helpdesk", False)).follow_up is False
    finally:
        await close(client, asynchronous)

    assert [(r.method, r.url.path.rsplit("/rooms", 1)[1]) for r in captured] == [
        ("GET", "/unread"),
        ("POST", "/helpdesk/active"),
        ("PATCH", "/helpdesk/follow-up"),
    ]
    assert json.loads(captured[1].content) == {"offset": 42}
    assert json.loads(captured[2].content) == {"follow_up": False}


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_tail_and_strict_post_reach_the_wire(asynchronous):
    captured = []
    client = client_for(asynchronous, captured)
    try:
        await call(client.rooms, "get", "helpdesk", tail=20)
        await call(client.rooms, "post", "helpdesk", body="hi", fallback=False)
        await call(client.rooms, "post", "helpdesk", body="hi")
    finally:
        await close(client, asynchronous)

    assert captured[0].url.params.get("tail") == "20" and "after" not in captured[0].url.params
    assert captured[1].url.params.get("fallback") == "false"
    assert captured[2].url.params.get("fallback") == "true"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_list_filters_paging_and_the_feed_reach_the_wire(asynchronous):
    captured = []
    client = client_for(asynchronous, captured)
    try:
        await call(client.rooms, "list")
        await call(client.rooms, "list", q="Acme", new_activity=True, limit=20, cursor="c1")
        feed = await call(client.rooms, "feed", since="c1", wait=20, rooms=[ROOM])
    finally:
        await close(client, asynchronous)

    assert dict(captured[0].url.params) == {}  # an unpaged list: every room
    assert dict(captured[1].url.params) == {"q": "Acme", "new_activity": "true", "limit": "20", "cursor": "c1"}
    assert captured[2].url.path.endswith("/rooms/feed")
    assert dict(captured[2].url.params) == {"since": "c1", "wait": "20", "limit": "100", "room": ROOM}
    assert feed.cursor == "c2" and feed.rooms_with_new_activity == 1
    assert str(feed.messages[0].room_id) == ROOM and feed.messages[0].body == "hi"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_files_are_posted_as_msg_format_attachments(asynchronous, tmp_path):
    (tmp_path / "shot.png").write_bytes(b"\x89PNG")
    captured = []
    client = client_for(asynchronous, captured)
    try:
        await call(
            client.rooms,
            "post",
            "helpdesk",
            attachments=[tmp_path / "shot.png", "https://example.com/spec.pdf"],
            fallback=False,
        )
    finally:
        await close(client, asynchronous)

    sent = json.loads(captured[0].content)
    assert sent["body"] == ""  # files alone are a message
    assert sent["attachments"] == [
        {"base64": "iVBORw==", "filename": "shot.png"},
        {"url": "https://example.com/spec.pdf"},
    ]
