"""Account-scoped rooms, messages, owner settings and invitation codes.

Room descriptions are Markdown. Read the returned retention fields for current
policy instead of deriving rules from description text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET
from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.live_lease import LiveLease
    from ._generated.models.live_request_lease import LiveRequestLease
    from ._generated.models.live_waiting import LiveWaiting
    from ._generated.models.room_active_response import RoomActiveResponse
    from ._generated.models.room_attention import RoomAttention
    from ._generated.models.room_command_availability import RoomCommandAvailability
    from ._generated.models.room_command_list import RoomCommandList
    from ._generated.models.room_delivery import RoomDelivery
    from ._generated.models.room_feed import RoomFeed
    from ._generated.models.room_follow_up import RoomFollowUp
    from ._generated.models.room_invitation_code import RoomInvitationCode
    from ._generated.models.room_invitation_codes import RoomInvitationCodes
    from ._generated.models.room_list import RoomList
    from ._generated.models.room_live_status import RoomLiveStatus
    from ._generated.models.room_members import RoomMembers
    from ._generated.models.room_post_response import RoomPostResponse
    from ._generated.models.room_summary import RoomSummary
    from ._generated.models.room_unread import RoomUnread
    from ._generated.models.room_view import RoomView
    from ._generated.models.room_work_claim import RoomWorkClaim


def _id(value: Any) -> Any:
    """An id from an id or an SDK object carrying ``.id``; UNSET for None."""
    if value is None:
        return UNSET
    raw = getattr(value, "id", value)
    return raw if isinstance(raw, UUID) else UUID(str(raw))


def _member_id(value: Any) -> UUID:
    """A room member's id from an id, or an SDK object carrying ``.member_id``
    (a live status row) or ``.id`` (a member row)."""
    raw = getattr(value, "member_id", None)
    if raw is None:
        raw = getattr(value, "id", value)
    return raw if isinstance(raw, UUID) else UUID(str(raw))


def _room_id(value: Any) -> UUID:
    """A room's id from an id, or an SDK object carrying ``.room_id`` (a work
    claim) or ``.id`` (a room)."""
    raw = getattr(value, "room_id", None)
    if raw is None:
        raw = getattr(value, "id", value)
    return raw if isinstance(raw, UUID) else UUID(str(raw))


class Rooms:
    """Room operations for the key's customer account (``client.rooms``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(
        self,
        *,
        kind: str | None = None,
        enrollment: Any = None,
        service: Any = None,
        q: str | None = None,
        new_activity: bool = False,
        include_closed: bool = False,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> RoomList:
        """List the rooms the account can reach, most recently active first,
        narrowed by kind, enrollment, service, a case-insensitive name prefix
        (``q``) or activity you haven't acknowledged (``new_activity``).
        ``enrollment`` / ``service`` take an id or the SDK object; each matches
        that exact scope (a service's rooms, not its enrollments').
        ``include_closed`` also lists rooms the account is still a member of
        but can't reach now (a paused or cancelled enrollment, an inactive
        service), each with ``closed_reason`` set. Without ``limit`` every
        room is returned; with it, pass the result's ``next_cursor`` as
        ``cursor`` for the next page. Each row carries ``can_post`` (for this
        key), ``last_sender_name``, ``origin`` (the service and enrollments
        the room was provisioned for) and ``attention_pending`` (the room
        waits for your account, see :meth:`next_room`)."""
        from ._generated.api.customer_rooms import customer_rooms_list_rooms

        return unwrap(
            customer_rooms_list_rooms.sync_detailed(
                client=self._client,
                kind=UNSET if kind is None else kind,
                enrollment=_id(enrollment),
                service=_id(service),
                q=UNSET if q is None else q,
                new_activity=new_activity or UNSET,
                include_closed=include_closed or UNSET,
                limit=UNSET if limit is None else limit,
                cursor=UNSET if cursor is None else cursor,
            )
        )

    def feed(
        self,
        *,
        since: str | None = None,
        wait: float = 0,
        limit: int = 100,
        rooms: Any = None,
    ) -> RoomFeed:
        """New messages across the account's rooms, each tagged with ``room_id``.

        Omit ``since`` to start at the current end (no backlog); pass the
        result's ``cursor`` as ``since`` to get only what came after it.
        ``wait`` (at most 25 s) long-polls until a message is stored; keep it
        below the client's timeout (30 s by default). ``rooms`` narrows the
        feed to some room ids (or SDK objects). An invalid ``since`` raises
        ValidationError: start again without it."""
        from ._generated.api.customer_rooms import customer_rooms_room_feed

        return unwrap(
            customer_rooms_room_feed.sync_detailed(
                client=self._client,
                since=UNSET if since is None else since,
                wait=wait,
                limit=limit,
                room=UNSET if rooms is None else [_id(room) for room in rooms],
            )
        )

    def leave(self, target: str) -> None:
        """Leave a room the account joined, if its kind allows it (a chat room).
        The owner can't leave, and a membership that comes from an enrollment
        follows the enrollment instead."""
        from ._generated.api.customer_rooms import customer_rooms_leave_room

        unwrap(customer_rooms_leave_room.sync_detailed(target, client=self._client))

    def get(
        self,
        target: str,
        *,
        after: int | None = None,
        limit: int = 50,
        tail: int | None = None,
        before: int | None = None,
    ) -> RoomView:
        """Read a room by UUID or handle; resume history with the previous messages.next.
        ``tail`` (instead of ``after``) reads the latest N messages, still oldest first;
        their ``next`` resumes with newer messages only, and ``messages.previous``
        (null when nothing older is stored) reads the page before them with
        ``tail=N, before=previous``. A message with ``recipient_member_id`` set
        (a ``!`` command line and its answer) is private to that member."""
        from ._generated.api.customer_rooms import customer_rooms_get_room_messages

        return unwrap(
            customer_rooms_get_room_messages.sync_detailed(
                target,
                client=self._client,
                after=UNSET if after is None else after,
                limit=limit,
                tail=UNSET if tail is None else tail,
                before=UNSET if before is None else before,
            )
        )

    def unread(self) -> RoomUnread:
        """How many of the account's rooms have activity you haven't acknowledged."""
        from ._generated.api.customer_rooms import customer_rooms_count_unread_rooms

        return unwrap(customer_rooms_count_unread_rooms.sync_detailed(client=self._client))

    def mark_active(self, target: str, offset: int) -> RoomActiveResponse:
        """Record that you have read the room through ``offset`` (a message's offset).
        The position is personal to the calling user, not the account. Call it
        when a person opens a room and when they stop viewing it; reading
        history records nothing. ``capped`` means storage hasn't reached
        ``offset`` yet."""
        from ._generated.api.customer_rooms import customer_rooms_mark_room_active
        from ._generated.models.room_active_request import RoomActiveRequest

        return unwrap(
            customer_rooms_mark_room_active.sync_detailed(
                target, client=self._client, body=RoomActiveRequest(offset=offset)
            )
        )

    def set_follow_up(self, target: str, follow_up: bool = True) -> RoomFollowUp:
        """Flag the room for this account to revisit, or clear the flag."""
        from ._generated.api.customer_rooms import customer_rooms_set_room_follow_up
        from ._generated.models.room_follow_up import RoomFollowUp

        return unwrap(
            customer_rooms_set_room_follow_up.sync_detailed(
                target, client=self._client, body=RoomFollowUp(follow_up=follow_up)
            )
        )

    def members(self, target: str) -> RoomMembers:
        """List active member accounts without their private delivery settings."""
        from ._generated.api.customer_rooms import customer_rooms_list_room_members

        return unwrap(customer_rooms_list_room_members.sync_detailed(target, client=self._client))

    # ---- commands -----------------------------------------------------------

    def commands(self) -> RoomCommandList:
        """Every ``!`` command the platform knows, with its syntax, example and
        pattern (the server's own regular expression, to validate a line
        before posting it). :meth:`available_commands` says which you may
        send in one room now."""
        from ._generated.api.customer_rooms import customer_rooms_list_room_commands

        return unwrap(customer_rooms_list_room_commands.sync_detailed(client=self._client))

    def available_commands(self, target: str) -> RoomCommandAvailability:
        """The commands you may send in the room right now and, for each
        unavailable one, ``reason`` and ``code``: the same evaluation ``!help``
        prints and a post is gated on."""
        from ._generated.api.customer_rooms import customer_rooms_list_room_commands_here

        return unwrap(customer_rooms_list_room_commands_here.sync_detailed(target, client=self._client))

    # ---- delivery -----------------------------------------------------------

    def delivery(self, target: str) -> RoomDelivery:
        """How this room reaches your account: its connectors, oldest first,
        each with a ``notify``, ``email`` and ``post`` service or null (off),
        and whether you may edit them (``can_edit``). A new member starts with
        one connector, ``main``, holding the account's room defaults."""
        from ._generated.api.customer_rooms import customer_rooms_get_room_delivery

        return unwrap(customer_rooms_get_room_delivery.sync_detailed(target, client=self._client))

    def add_connector(
        self,
        target: str,
        name: str,
        *,
        notify: str | None = None,
        email: str | None = None,
        post: str | None = None,
    ) -> RoomDelivery:
        """Add a named connector (lowercase letters, digits and hyphens; at most
        five per room) and return the room's delivery. Each channel is a
        service: ``notify`` / ``email`` the account's Me service of that name,
        or a path such as ``labs/msg-to-discord``; ``post`` the service a
        keyless sender posts through. None leaves the channel off."""
        from ._generated.api.customer_rooms import customer_rooms_add_room_connector
        from ._generated.models.room_connector_create import RoomConnectorCreate

        channels = {key: value for key, value in (("notify", notify), ("email", email), ("post", post)) if value}
        return unwrap(
            customer_rooms_add_room_connector.sync_detailed(
                target, client=self._client, body=RoomConnectorCreate.from_dict({"name": name, **channels})
            )
        )

    def update_connector(self, target: str, name: str, **channels: str | None) -> RoomDelivery:
        """Change one connector's ``notify``, ``email`` or ``post`` service.
        Channels left out keep their value; None turns one off."""
        from ._generated.api.customer_rooms import customer_rooms_update_room_connector
        from ._generated.models.room_connector_update import RoomConnectorUpdate

        return unwrap(
            customer_rooms_update_room_connector.sync_detailed(
                target, name, client=self._client, body=RoomConnectorUpdate.from_dict(channels)
            )
        )

    def remove_connector(self, target: str, name: str) -> RoomDelivery:
        """Remove a connector: its reply address and any URL naming it stop routing."""
        from ._generated.api.customer_rooms import customer_rooms_delete_room_connector

        return unwrap(customer_rooms_delete_room_connector.sync_detailed(target, name, client=self._client))

    # ---- live help ----------------------------------------------------------

    def accept_live_requests(self, *, client_id: str | None = None, mode: str = "accepting") -> LiveLease:
        """Accept live requests for this account from this client, until the
        lease lapses (``expires_in`` seconds) or :meth:`stop_accepting_live_requests`.
        Renew it with the returned ``client_id`` before then. ``mode="draining"``
        finishes the queue instead, taking no new requests. Only this call
        accepts; reading and posting never do."""
        from ._generated.api.customer_rooms import customer_rooms_accept_live_requests
        from ._generated.models.live_accepting import LiveAccepting

        return unwrap(
            customer_rooms_accept_live_requests.sync_detailed(
                client=self._client, body=LiveAccepting.from_dict({"client_id": client_id, "mode": mode})
            )
        )

    def stop_accepting_live_requests(self, *, client_id: str | None = None) -> None:
        """Stop accepting from one client, or from every client of the account."""
        from ._generated.api.customer_rooms import customer_rooms_stop_accepting_live_requests
        from ._generated.models.live_stop import LiveStop

        unwrap(
            customer_rooms_stop_accepting_live_requests.sync_detailed(
                client=self._client, body=LiveStop(client_id=client_id)
            )
        )

    def live_waiting(self) -> LiveWaiting:
        """The rooms whose live request waits for this account, oldest first."""
        from ._generated.api.customer_rooms import customer_rooms_list_live_waiting

        return unwrap(customer_rooms_list_live_waiting.sync_detailed(client=self._client))

    def live_status(self, target: str) -> RoomLiveStatus:
        """For each other member of the room: whether its party is accepting
        live requests (``state``: accepting, draining or off) and the room's
        live request to it, with your place in line when it is yours."""
        from ._generated.api.customer_rooms import customer_rooms_get_room_live_status

        return unwrap(customer_rooms_get_room_live_status.sync_detailed(target, client=self._client))

    def request_live_help(
        self, target: str, member: Any, *, client_id: str | None = None, generation: str | None = None
    ) -> LiveRequestLease:
        """Ask ``member`` (a member id, or a row of :meth:`live_status`) for live
        help, or renew the ask: pass back the lease's ``client_id`` and
        ``generation`` before ``expires_in`` seconds pass. The request lives
        while any requester keeps renewing. It may start while nobody is
        accepting (``available`` says so) but not while the party is only
        finishing its queue (409), and 409 when ``generation`` was resolved:
        ask again without it."""
        from ._generated.api.customer_rooms import customer_rooms_request_live_help
        from ._generated.models.live_request_start import LiveRequestStart

        return unwrap(
            customer_rooms_request_live_help.sync_detailed(
                target,
                client=self._client,
                body=LiveRequestStart(target_member_id=_member_id(member), client_id=client_id, generation=generation),
            )
        )

    def cancel_live_help(self, target: str, member: Any, *, client_id: str) -> None:
        """End this client's own part of the live request to ``member``; other
        requesters keep theirs, and the request ends with the last one."""
        from ._generated.api.customer_rooms import customer_rooms_cancel_live_help
        from ._generated.models.live_request_cancel import LiveRequestCancel

        unwrap(
            customer_rooms_cancel_live_help.sync_detailed(
                target,
                client=self._client,
                body=LiveRequestCancel(target_member_id=_member_id(member), client_id=client_id),
            )
        )

    def resolve_live_help(self, target: str, *, generation: str | None = None) -> None:
        """Resolve the room's live request to this account, for every requester;
        with ``generation``, only that request, never a newer one."""
        from ._generated.api.customer_rooms import customer_rooms_resolve_live_help
        from ._generated.models.live_resolve import LiveResolve

        unwrap(
            customer_rooms_resolve_live_help.sync_detailed(
                target, client=self._client, body=LiveResolve(generation=generation)
            )
        )

    # ---- work queue ---------------------------------------------------------

    def next_room(
        self, current: Any = None, *, claim_token: str | None = None, offset: int | None = None
    ) -> RoomWorkClaim:
        """Claim the room that has waited longest for this account (``room_id``
        is null when none is waiting), first completing ``current`` (a room id
        or the previous claim) through ``offset``, the highest message offset
        shown, if ``claim_token`` is still held. Renew the claim with
        :meth:`renew_claim` while the room is open; it lapses after
        ``expires_in`` seconds. Rooms another worker holds, and rooms you
        left with :meth:`return_later` in the last few minutes, are skipped."""
        from ._generated.api.customer_rooms import customer_rooms_next_room
        from ._generated.models.room_next_request import RoomNextRequest
        from ._generated.models.room_work_ref import RoomWorkRef

        if current is None:
            body = RoomNextRequest()
        else:
            token = claim_token if claim_token is not None else getattr(current, "claim_token", None)
            body = RoomNextRequest(
                current=RoomWorkRef(
                    room_id=_room_id(current),
                    claim_token=UNSET if token is None else token,
                    offset=UNSET if offset is None else offset,
                )
            )
        return unwrap(customer_rooms_next_room.sync_detailed(client=self._client, body=body))

    def renew_claim(self, target: str, claim_token: str) -> RoomWorkClaim:
        """Keep holding the room claimed by :meth:`next_room`. 409 when the
        claim has lapsed: someone else may have the room now."""
        from ._generated.api.customer_rooms import customer_rooms_renew_room_claim
        from ._generated.models.room_claim_renew import RoomClaimRenew

        return unwrap(
            customer_rooms_renew_room_claim.sync_detailed(
                target, client=self._client, body=RoomClaimRenew(claim_token=claim_token)
            )
        )

    def return_later(self, target: str, *, claim_token: str | None = None) -> RoomAttention:
        """Step away without completing the room: it keeps waiting for this
        account with its place, the claim is released, and your next
        :meth:`next_room` skips it for a few minutes."""
        from ._generated.api.customer_rooms import customer_rooms_return_to_room_later
        from ._generated.models.room_return_later import RoomReturnLater

        return unwrap(
            customer_rooms_return_to_room_later.sync_detailed(
                target, client=self._client, body=RoomReturnLater(claim_token=claim_token)
            )
        )

    def mark_done(self, target: str, offset: int) -> RoomAttention:
        """Complete the room for this account through ``offset``, the highest
        message offset shown; a mention newer than it keeps the room waiting."""
        from ._generated.api.customer_rooms import customer_rooms_complete_room_attention
        from ._generated.models.room_attention_done import RoomAttentionDone

        return unwrap(
            customer_rooms_complete_room_attention.sync_detailed(
                target, client=self._client, body=RoomAttentionDone(offset=offset)
            )
        )

    # ---- settings and posting ------------------------------------------------

    def update(self, target: str, **settings: Any) -> RoomSummary:
        """Update owner settings: name, Markdown description, retention_seconds or status
        (active or readonly). Omitted fields are unchanged; null clears optional values.
        """
        from ._generated.api.customer_rooms import customer_rooms_update_room_settings
        from ._generated.models.room_settings_update import RoomSettingsUpdate

        return unwrap(
            customer_rooms_update_room_settings.sync_detailed(
                target, client=self._client, body=RoomSettingsUpdate.from_dict(settings)
            )
        )

    def post(
        self,
        target: str | None = None,
        *,
        body: str = "",
        attachments: Any = None,
        mentions: Any = None,
        fallback: bool = True,
        **message: Any,
    ) -> RoomPostResponse:
        """Post a message in msg format. Target is a UUID or handle; None uses a leading @handle or the me
        fallback. With a target and ``fallback=False``, a room that can't take the post raises
        (NotFoundError / PermissionError) instead of posting to ``me``. Pass client_message_id for
        idempotent retries.

        ``attachments`` takes file paths, ``http(s)`` URLs (kept as links) or entries from
        :mod:`unitysvc.attachments`; files are stored for 7 days. A message needs a ``body`` or a
        file (a URL alone needs a ``body``): otherwise ValueError, before anything is sent.

        ``mentions`` lists the members (ids, or member rows) the message calls for: the room then
        waits for their accounts (``attention_pending``). A body whose first line is a ``!``
        command is run by the platform; the response's ``command`` says what it did, and the line
        and its answer are private to you.
        """
        if attachments:
            from .attachments import check_content, prepare

            message["attachments"] = prepare(attachments)
            check_content(body, message["attachments"])
        if mentions is not None:
            message["mentions"] = [str(_member_id(member)) for member in mentions]
        from ._generated.api.customer_rooms import customer_rooms_post_room_message
        from ._generated.models.room_post_request import RoomPostRequest

        if target is not None:
            from ._generated.api.customer_rooms import customer_rooms_post_room_message_to

            return unwrap(
                customer_rooms_post_room_message_to.sync_detailed(
                    target,
                    client=self._client,
                    body=RoomPostRequest.from_dict({"body": body, **message}),
                    fallback=fallback,
                )
            )

        return unwrap(
            customer_rooms_post_room_message.sync_detailed(
                client=self._client, body=RoomPostRequest.from_dict({"body": body, **message})
            )
        )

    def join(self, token: str) -> RoomSummary:
        """Redeem an invitation as this account; already-member joins preserve its role."""
        from ._generated.api.customer_rooms import customer_rooms_join_room
        from ._generated.models.room_join_request import RoomJoinRequest

        return unwrap(customer_rooms_join_room.sync_detailed(client=self._client, body=RoomJoinRequest(token=token)))

    def invitations(self, target: str, *, include_inactive: bool = False) -> RoomInvitationCodes:
        """List invitation codes the caller is authorized to manage."""
        from ._generated.api.customer_rooms import customer_rooms_list_room_invitation_codes

        return unwrap(
            customer_rooms_list_room_invitation_codes.sync_detailed(
                target, client=self._client, include_inactive=include_inactive
            )
        )

    def create_invitation(self, target: str, *, role: str = "member", **options: Any) -> RoomInvitationCode:
        """Create an invitation. Options: expires_in_days, max_uses and note; the server enforces the inviter
        role cap.
        """
        from ._generated.api.customer_rooms import customer_rooms_create_room_invitation_code
        from ._generated.models.room_invitation_create import RoomInvitationCreate

        return unwrap(
            customer_rooms_create_room_invitation_code.sync_detailed(
                target, client=self._client, body=RoomInvitationCreate.from_dict({"role": role, **options})
            )
        )

    def revoke_invitation(self, target: str, code_id: str | UUID) -> RoomInvitationCode:
        """Revoke a code for future joins; existing memberships are preserved."""
        from ._generated.api.customer_rooms import customer_rooms_revoke_room_invitation_code

        return unwrap(
            customer_rooms_revoke_room_invitation_code.sync_detailed(target, UUID(str(code_id)), client=self._client)
        )
