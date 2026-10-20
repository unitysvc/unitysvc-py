"""Async mirror of :mod:`unitysvc.preferences`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._http import LowLevelClient, unwrap
from .preferences import RequestLogMode, preference_update

if TYPE_CHECKING:
    from ._generated.models.preference_public import PreferencePublic
    from ._generated.models.preferences_public import PreferencesPublic


class AsyncPreferences:
    """Async operations on the current account's preferences.

    Mirrors :class:`unitysvc.preferences.Preferences` — see that class for
    the surface and rationale.
    """

    def __init__(self, client: LowLevelClient) -> None:
        self._client = client

    async def list(self) -> PreferencesPublic:
        """See :meth:`unitysvc.preferences.Preferences.list`."""
        from ._generated.api.preferences import preferences_read_preferences

        return unwrap(await preferences_read_preferences.asyncio_detailed(client=self._client))

    async def get(self, name: str) -> PreferencePublic:
        """See :meth:`unitysvc.preferences.Preferences.get`."""
        from ._generated.api.preferences import preferences_read_named_preference

        return unwrap(await preferences_read_named_preference.asyncio_detailed(name, client=self._client))

    async def set(self, name: str, value: str | dict[str, Any] | None) -> PreferencePublic:
        """See :meth:`unitysvc.preferences.Preferences.set`."""
        if value is None:
            return await self.clear(name)
        from ._generated.api.preferences import preferences_set_named_preference

        return unwrap(
            await preferences_set_named_preference.asyncio_detailed(
                name, client=self._client, body=preference_update(value)
            )
        )

    async def clear(self, name: str) -> PreferencePublic:
        """See :meth:`unitysvc.preferences.Preferences.clear`."""
        from ._generated.api.preferences import preferences_clear_named_preference

        return unwrap(await preferences_clear_named_preference.asyncio_detailed(name, client=self._client))

    async def set_notification(self, service: str | None) -> PreferencePublic:
        """See :meth:`unitysvc.preferences.Preferences.set_notification`."""
        return await self.set("notification", service)

    async def set_ai(self, service: str | None) -> PreferencePublic:
        """See :meth:`unitysvc.preferences.Preferences.set_ai`."""
        return await self.set("ai", service)

    async def set_request_log_mode(self, mode: RequestLogMode | None) -> PreferencePublic:
        """See :meth:`unitysvc.preferences.Preferences.set_request_log_mode`."""
        return await self.set("request-log", mode)
