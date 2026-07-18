"""Async mirror of :mod:`unitysvc.broadcasts`.

Same active-record contract: :class:`AsyncBroadcast` wraps the generated
record and exposes ``dispatch()`` plus target-management methods that
delegate back to the parent :class:`AsyncClient`. See
:mod:`unitysvc.broadcasts` for the full contract and field reference.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET as _UNSET
from ._http import LowLevelClient, unwrap
from .broadcasts import _target_create

if TYPE_CHECKING:
    import httpx

    from ._generated.models.broadcast_public import BroadcastPublic
    from ._generated.models.broadcast_target_public import BroadcastTargetPublic
    from .aclient import AsyncClient


class AsyncBroadcast:
    """Active-record wrapper around a broadcast (async).

    See :class:`unitysvc.broadcasts.Broadcast` for the contract.
    Dispatched by name at ``/b/<name>``; managed by UUID.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: BroadcastPublic, parent: AsyncClient) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<AsyncBroadcast name={raw.name!r} id={raw.id!r}>"

    @property
    def path(self) -> str:
        """Gateway-relative dispatch path for this broadcast: ``b/<name>``."""
        return f"b/{object.__getattribute__(self, '_raw').name}"

    async def dispatch(
        self,
        *,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Dispatch a request through this broadcast at ``/b/<name>``.

        Fans the call out to every target. ``path`` is an optional
        sub-path appended after the broadcast name.
        """
        target = self.path if not path else f"{self.path}/{path.lstrip('/')}"
        return await self._parent.dispatch(
            target, method=method, json=json, data=data, headers=headers, timeout=timeout
        )

    # ------------------------------------------------------------------
    # Management (pre-bind this broadcast's id)
    # ------------------------------------------------------------------
    async def refresh(self) -> AsyncBroadcast:
        """Re-fetch this broadcast (latest targets / metadata)."""
        return await self._parent.broadcasts.get(self._raw.id)

    async def update(
        self,
        *,
        description: Any = _UNSET,
        mode: Any = _UNSET,
        target_timeout_ms: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> AsyncBroadcast:
        """Update this broadcast's metadata. See :meth:`AsyncBroadcasts.update`."""
        return await self._parent.broadcasts.update(
            self._raw.id,
            description=description,
            mode=mode,
            target_timeout_ms=target_timeout_ms,
            enabled=enabled,
        )

    async def delete(self) -> None:
        """Delete this broadcast."""
        await self._parent.broadcasts.delete(self._raw.id)

    async def add_target(
        self,
        *,
        name: str,
        target_path: str,
        routing_key_override: dict[str, Any] | None = None,
        sort_order: int = 0,
    ) -> BroadcastTargetPublic:
        """Add a target. See :meth:`AsyncBroadcasts.add_target`."""
        return await self._parent.broadcasts.add_target(
            self._raw.id,
            name=name,
            target_path=target_path,
            routing_key_override=routing_key_override,
            sort_order=sort_order,
        )

    async def remove_target(self, target_id: str | UUID) -> None:
        """Remove a target by id."""
        await self._parent.broadcasts.remove_target(self._raw.id, target_id)

    async def replace_targets(self, targets: builtins.list[dict[str, Any]]) -> AsyncBroadcast:
        """Replace all targets at once. See :meth:`AsyncBroadcasts.replace_targets`."""
        return await self._parent.broadcasts.replace_targets(self._raw.id, targets)


@dataclass
class AsyncBroadcastListPage:
    """Result of :meth:`AsyncBroadcasts.list` — ``data`` items are :class:`AsyncBroadcast`."""

    data: list[AsyncBroadcast] = field(default_factory=list)
    count: int = 0


class AsyncBroadcasts:
    """Async operations on customer broadcasts (``/v1/customer/broadcasts``).

    See :class:`unitysvc.broadcasts.Broadcasts` for the contract.
    """

    def __init__(self, client: LowLevelClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(self) -> AsyncBroadcastListPage:
        """List the customer's broadcasts."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_list_broadcasts

        raw = unwrap(await customer_broadcasts_list_broadcasts.asyncio_detailed(client=self._client))
        return AsyncBroadcastListPage(
            data=[AsyncBroadcast(b, parent=self._parent) for b in raw.data],
            count=raw.count,
        )

    async def get(self, broadcast_id: str | UUID) -> AsyncBroadcast:
        """Get one broadcast by id."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_get_broadcast

        raw = unwrap(
            await customer_broadcasts_get_broadcast.asyncio_detailed(UUID(str(broadcast_id)), client=self._client)
        )
        return AsyncBroadcast(raw, parent=self._parent)

    async def create(
        self,
        *,
        name: str,
        description: str | None = None,
        mode: str = "sync",
        target_timeout_ms: int = 30000,
        enabled: bool = True,
        targets: builtins.list[dict[str, Any]] | None = None,
    ) -> AsyncBroadcast:
        """Create a broadcast. See :meth:`unitysvc.broadcasts.Broadcasts.create`."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_create_broadcast
        from ._generated.models.broadcast_create import BroadcastCreate
        from ._generated.models.broadcast_create_mode import check_broadcast_create_mode
        from ._generated.types import UNSET

        body = BroadcastCreate(
            name=name,
            description=description if description is not None else UNSET,
            mode=check_broadcast_create_mode(mode),
            target_timeout_ms=target_timeout_ms,
            enabled=enabled,
            targets=_target_create(targets) if targets is not None else UNSET,
        )
        raw = unwrap(await customer_broadcasts_create_broadcast.asyncio_detailed(client=self._client, body=body))
        return AsyncBroadcast(raw, parent=self._parent)

    async def update(
        self,
        broadcast_id: str | UUID,
        *,
        description: Any = _UNSET,
        mode: Any = _UNSET,
        target_timeout_ms: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> AsyncBroadcast:
        """Update a broadcast's metadata (only the fields you pass)."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_update_broadcast
        from ._generated.models.broadcast_update import BroadcastUpdate
        from ._generated.models.broadcast_update_mode_type_0 import (
            check_broadcast_update_mode_type_0,
        )

        mode_val: Any = _UNSET if mode is _UNSET else check_broadcast_update_mode_type_0(mode)
        body = BroadcastUpdate(
            description=description,
            mode=mode_val,
            target_timeout_ms=target_timeout_ms,
            enabled=enabled,
        )
        raw = unwrap(
            await customer_broadcasts_update_broadcast.asyncio_detailed(
                UUID(str(broadcast_id)), client=self._client, body=body
            )
        )
        return AsyncBroadcast(raw, parent=self._parent)

    async def delete(self, broadcast_id: str | UUID) -> None:
        """Delete a broadcast."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_delete_broadcast

        unwrap(
            await customer_broadcasts_delete_broadcast.asyncio_detailed(UUID(str(broadcast_id)), client=self._client)
        )

    async def add_target(
        self,
        broadcast_id: str | UUID,
        *,
        name: str,
        target_path: str,
        routing_key_override: dict[str, Any] | None = None,
        sort_order: int = 0,
    ) -> BroadcastTargetPublic:
        """Add a target to a broadcast. Returns the created target."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_add_target
        from ._generated.models.broadcast_target_create import BroadcastTargetCreate
        from ._generated.models.broadcast_target_create_routing_key_override_type_0 import (
            BroadcastTargetCreateRoutingKeyOverrideType0,
        )
        from ._generated.types import UNSET

        body = BroadcastTargetCreate(
            name=name,
            target_path=target_path,
            routing_key_override=(
                BroadcastTargetCreateRoutingKeyOverrideType0.from_dict(routing_key_override)
                if routing_key_override is not None
                else UNSET
            ),
            sort_order=sort_order,
        )
        return unwrap(
            await customer_broadcasts_add_target.asyncio_detailed(
                UUID(str(broadcast_id)), client=self._client, body=body
            )
        )

    async def remove_target(self, broadcast_id: str | UUID, target_id: str | UUID) -> None:
        """Remove a target from a broadcast by id."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_remove_target

        unwrap(
            await customer_broadcasts_remove_target.asyncio_detailed(
                UUID(str(broadcast_id)), UUID(str(target_id)), client=self._client
            )
        )

    async def replace_targets(self, broadcast_id: str | UUID, targets: builtins.list[dict[str, Any]]) -> AsyncBroadcast:
        """Replace all targets of a broadcast at once. Returns the refreshed broadcast."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_replace_targets

        unwrap(
            await customer_broadcasts_replace_targets.asyncio_detailed(
                UUID(str(broadcast_id)), client=self._client, body=_target_create(targets)
            )
        )
        return await self.get(broadcast_id)
