"""``client.preferences`` — generic per-user preference set/clear (unitysvc#2063).

Wraps ``POST /v1/customer/preferences/set``, the API-key-reachable door onto
per-user preferences (``User.preference``) — the same field the frontend
writes to via a JWT-authenticated ``PATCH /users/me``. One preference per
call: pass its name and new value, or ``value=None`` to clear it.

This is the one place a preference is ever written from — including
request-log toggling, which used to have its own duplicate ``start``/``stop``
wrapper on :class:`unitysvc.request_logs.RequestLogs`. Call :meth:`set`
directly for any preference this SDK doesn't have a typed convenience for
yet; :meth:`set_notification_destination` and :meth:`set_request_log_mode`
are the typed ones for today's two.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from ._http import LowLevelClient, unwrap

if TYPE_CHECKING:
    from ._generated.models.user_public import UserPublic

RequestLogMode = Literal["truncated", "complete"]


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

    def set_request_log_mode(self, mode: RequestLogMode | None) -> UserPublic:
        """Typed convenience for the ``"request-log"`` preference.

        Enable request logging for the authenticated user, or disable it
        with ``mode=None``. Already-persisted rows remain visible via
        :meth:`unitysvc.request_logs.RequestLogs.list` /
        :meth:`~unitysvc.request_logs.RequestLogs.get` either way; only
        future gateway dispatches are affected. Idempotent.

        Args:
            mode: ``"truncated"`` — every request is logged with bodies
                clipped at 8 KB, no S3 upload. ``"complete"`` — full
                request/response bodies are uploaded to S3 so ``get()``
                can return the full payload (the listing endpoint still
                returns only the clipped preview, to keep paging cheap).
                ``None`` disables logging.
        """
        return self.set("request-log", mode)
