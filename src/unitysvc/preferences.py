"""``client.preferences`` — named preferences on the account a key acts for.

Wraps the account-scoped preferences API (unitysvc#2659):
``GET /v1/preferences``, and ``GET`` / ``PUT`` / ``DELETE
/v1/preferences/{name}``. The URL names the preference; the account is the
key's own (a personal key → the user, a team key → that team, a seller key →
that seller).

Every call returns the preference as that account sees it: its own
``value``, the ``effective`` value calls and notices use, and the ``source``
of that effective value (``account``, ``user`` or ``default``), so a caller
never re-derives a fallback rule.

Today's preferences:

* ``notification`` — where notices are forwarded: a service path, or a
  ``b/<name>`` broadcast / ``e/<CODE>`` enrollment you own.
* ``ai`` — the AI behind ``/ai``: a service name (e.g.
  ``labs/llm-balanced``) or ``a/<name>`` alias. Services that require
  enrollment are refused.
* ``request-log`` — request-logging mode, ``truncated`` or ``complete``.

:meth:`Preferences.set` / :meth:`Preferences.clear` work for any name;
:meth:`Preferences.set_notification`, :meth:`Preferences.set_ai` and
:meth:`Preferences.set_request_log_mode` are typed conveniences.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from ._http import LowLevelClient, unwrap

if TYPE_CHECKING:
    from ._generated.models.preference_public import PreferencePublic
    from ._generated.models.preference_update import PreferenceUpdate
    from ._generated.models.preferences_public import PreferencesPublic

RequestLogMode = Literal["truncated", "complete"]


def preference_update(value: str | dict[str, Any]) -> PreferenceUpdate:
    """Build the ``PUT`` body: a string (service or mode) or a ``{"service": ...}`` dict."""
    from ._generated.models.preference_update import PreferenceUpdate
    from ._generated.models.preference_value import PreferenceValue

    if isinstance(value, dict):
        return PreferenceUpdate(value=PreferenceValue.from_dict(value))
    return PreferenceUpdate(value=value)


class Preferences:
    """Operations on the current account's preferences (``/v1/preferences``)."""

    def __init__(self, client: LowLevelClient) -> None:
        self._client = client

    def list(self) -> PreferencesPublic:
        """Every preference, as the current account sees it."""
        from ._generated.api.preferences import preferences_read_preferences

        return unwrap(preferences_read_preferences.sync_detailed(client=self._client))

    def get(self, name: str) -> PreferencePublic:
        """One preference, as the current account sees it."""
        from ._generated.api.preferences import preferences_read_named_preference

        return unwrap(preferences_read_named_preference.sync_detailed(name, client=self._client))

    def set(self, name: str, value: str | dict[str, Any] | None) -> PreferencePublic:
        """Set one preference on the current account; ``value=None`` clears it.

        ``value`` is a service (``"labs/llm-balanced"`` or
        ``{"service": "labs/llm-balanced"}``) for ``notification`` / ``ai``,
        or a mode string for ``request-log``. The backend validates it on
        write.
        """
        if value is None:
            return self.clear(name)
        from ._generated.api.preferences import preferences_set_named_preference

        return unwrap(
            preferences_set_named_preference.sync_detailed(name, client=self._client, body=preference_update(value))
        )

    def clear(self, name: str) -> PreferencePublic:
        """Clear one preference on the current account, back to its fallback. Idempotent."""
        from ._generated.api.preferences import preferences_clear_named_preference

        return unwrap(preferences_clear_named_preference.sync_detailed(name, client=self._client))

    def set_notification(self, service: str | None) -> PreferencePublic:
        """Where notices are forwarded.

        ``service`` is a service path (e.g. ``"labs/discord-relay"``), or a
        ``"b/<name>"`` broadcast / ``"e/<CODE>"`` enrollment you own. ``None``
        clears it: in-app delivery only, or, for a team, its notices fall
        back to each member's own destination.
        """
        return self.set("notification", service)

    def set_ai(self, service: str | None) -> PreferencePublic:
        """The AI that ``/ai`` uses.

        ``service`` is a service name (e.g. ``"labs/llm-balanced"``) or an
        ``"a/<name>"`` alias. Services that require enrollment are refused.
        ``None`` clears it, and the platform default applies.
        """
        return self.set("ai", service)

    def set_request_log_mode(self, mode: RequestLogMode | None) -> PreferencePublic:
        """Enable request logging, or disable it with ``mode=None``.

        Already-persisted rows remain visible via
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
