"""Async mirror of :mod:`unitysvc.preferences`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._http import LowLevelClient, unwrap

if TYPE_CHECKING:
    from ._generated.models.user_public import UserPublic


class AsyncPreferences:
    """Async operations on the customer's preferences.

    Mirrors :class:`unitysvc.preferences.Preferences` — see that class for
    the ``set`` surface and rationale.
    """

    def __init__(self, client: LowLevelClient) -> None:
        self._client = client

    async def set(self, name: str, value: Any = None) -> UserPublic:
        """See :meth:`unitysvc.preferences.Preferences.set`."""
        from ._generated.api.customer import customer_set_preference
        from ._generated.models.preference_set_request import PreferenceSetRequest

        return unwrap(
            await customer_set_preference.asyncio_detailed(
                client=self._client,
                body=PreferenceSetRequest(name=name, value=value),
            )
        )

    async def set_notification_destination(self, service: str | None) -> UserPublic:
        """See :meth:`unitysvc.preferences.Preferences.set_notification_destination`."""
        return await self.set("notification-destination", service)
