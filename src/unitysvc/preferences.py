"""``client.preferences`` — generic per-user preference set/clear (unitysvc#2063).

Wraps ``POST /v1/customer/preferences/set``, the API-key-reachable door onto
per-user preferences (``User.preference``) — the same field the frontend
writes to via a JWT-authenticated ``PATCH /users/me``. One preference per
call: pass its name and new value, or ``value=None`` to clear it.

Higher-level, typed wrappers build on this rather than duplicating it —
:class:`unitysvc.request_logs.RequestLogs` implements ``start``/``stop`` as
calls to :meth:`Preferences.set` with the ``"request-log"`` preference. Call
:meth:`set` directly for any preference this SDK doesn't have a typed
wrapper for yet.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._http import LowLevelClient, unwrap

if TYPE_CHECKING:
    from ._generated.models.user_public import UserPublic


class Preferences:
    """Operations on the customer's preferences (``/v1/customer/preferences``)."""

    def __init__(self, client: LowLevelClient) -> None:
        self._client = client

    def set(self, name: str, value: Any = None) -> UserPublic:
        """Set (or clear, with ``value=None``) one named preference.

        Returns the updated user, including the full ``preference`` dict —
        useful for confirming what was actually persisted.
        """
        from ._generated.api.customer import customer_set_preference
        from ._generated.models.preference_set_request import PreferenceSetRequest

        return unwrap(
            customer_set_preference.sync_detailed(
                client=self._client,
                body=PreferenceSetRequest(name=name, value=value),
            )
        )

    def set_notification_destination(self, service: str | None) -> UserPublic:
        """Typed convenience for the ``"notification-destination"`` preference.

        ``service`` is where personal notifications (in-app events routed
        through ``notify://user``) get forwarded — a service path (e.g.
        ``"labs/discord-relay"``), or a ``"b/<name>"`` broadcast /
        ``"e/<CODE>"`` enrollment shorthand you own. Pass ``None`` to clear
        it (falls back to in-app delivery only).
        """
        return self.set("notification-destination", service)
