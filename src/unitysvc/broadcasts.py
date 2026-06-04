"""``client.broadcasts`` — customer broadcasts (the ``/b/`` primitive).

A broadcast fans one call out to many targets in parallel — either a
``sync`` envelope of per-target results, or ``async`` enqueued tasks.

Broadcasts are **managed by UUID** (``client.broadcasts.get(id)``) but
**dispatched by name** at ``/b/<name>`` on the gateway. This module
exposes the :class:`Broadcasts` resource manager (``client.broadcasts``)
plus a :class:`Broadcast` active-record wrapper whose target-management
methods pre-bind the broadcast id and which — via
:class:`~unitysvc._wrappers._Wrappable` — supports
``bc.dispatch(...)`` / ``bc.logged()`` / etc.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET as _UNSET
from ._http import unwrap
from ._wrappers import _Wrappable

if TYPE_CHECKING:
    import httpx

    from ._generated.client import AuthenticatedClient
    from ._generated.models.broadcast_public import BroadcastPublic
    from ._generated.models.broadcast_target_public import BroadcastTargetPublic
    from .client import Client


class Broadcast(_Wrappable):
    """Active-record wrapper around a broadcast.

    Forwards field access (``bc.name``, ``bc.mode``, ``bc.targets``, …)
    to the underlying generated :class:`BroadcastPublic`. Adds
    target-management methods that pre-bind this broadcast's id, plus
    ``update`` / ``delete`` / ``refresh``.

    Inherits :class:`~unitysvc._wrappers._Wrappable`, so the gateway
    wrapper primitives compose on the broadcast's ``/b/<name>`` path:
    ``bc.logged().dispatch(json=body)``, etc.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: BroadcastPublic, parent: Client) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<Broadcast name={raw.name!r} id={raw.id!r}>"

    @property
    def path(self) -> str:
        """Gateway-relative dispatch path for this broadcast: ``b/<name>``."""
        return f"b/{object.__getattribute__(self, '_raw').name}"

    def _get_client(self) -> Client:
        return object.__getattribute__(self, "_parent")

    def dispatch(
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
        sub-path appended after the broadcast name. Compose wrapper
        primitives first for cache/log/retry, e.g.
        ``bc.logged().dispatch(json=body)``.
        """
        target = self.path if not path else f"{self.path}/{path.lstrip('/')}"
        return self._parent.dispatch(target, method=method, json=json, data=data, headers=headers, timeout=timeout)

    # ------------------------------------------------------------------
    # Management (pre-bind this broadcast's id)
    # ------------------------------------------------------------------
    def refresh(self) -> Broadcast:
        """Re-fetch this broadcast (latest targets / metadata)."""
        return self._parent.broadcasts.get(self._raw.id)

    def update(
        self,
        *,
        description: Any = _UNSET,
        mode: Any = _UNSET,
        target_timeout_ms: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> Broadcast:
        """Update this broadcast's metadata. See :meth:`Broadcasts.update`."""
        return self._parent.broadcasts.update(
            self._raw.id,
            description=description,
            mode=mode,
            target_timeout_ms=target_timeout_ms,
            enabled=enabled,
        )

    def delete(self) -> None:
        """Delete this broadcast."""
        self._parent.broadcasts.delete(self._raw.id)

    def add_target(
        self,
        *,
        name: str,
        target_path: str,
        routing_key_override: dict[str, Any] | None = None,
        sort_order: int = 0,
    ) -> BroadcastTargetPublic:
        """Add a target. See :meth:`Broadcasts.add_target`."""
        return self._parent.broadcasts.add_target(
            self._raw.id,
            name=name,
            target_path=target_path,
            routing_key_override=routing_key_override,
            sort_order=sort_order,
        )

    def remove_target(self, target_id: str | UUID) -> None:
        """Remove a target by id."""
        self._parent.broadcasts.remove_target(self._raw.id, target_id)

    def replace_targets(self, targets: builtins.list[dict[str, Any]]) -> Broadcast:
        """Replace all targets at once. See :meth:`Broadcasts.replace_targets`."""
        return self._parent.broadcasts.replace_targets(self._raw.id, targets)


@dataclass
class BroadcastListPage:
    """Result of :meth:`Broadcasts.list` — ``data`` items are :class:`Broadcast` wrappers."""

    data: list[Broadcast] = field(default_factory=list)
    count: int = 0


def _target_create(targets: builtins.list[dict[str, Any]]) -> list[Any]:
    from ._generated.models.broadcast_target_create import BroadcastTargetCreate
    from ._generated.models.broadcast_target_create_routing_key_override_type_0 import (
        BroadcastTargetCreateRoutingKeyOverrideType0,
    )
    from ._generated.types import UNSET

    out = []
    for i, t in enumerate(targets):
        rk = t.get("routing_key_override")
        out.append(
            BroadcastTargetCreate(
                name=t["name"],
                target_path=t["target_path"],
                routing_key_override=(
                    BroadcastTargetCreateRoutingKeyOverrideType0.from_dict(rk) if rk is not None else UNSET
                ),
                sort_order=t.get("sort_order", i),
            )
        )
    return out


class Broadcasts:
    """Operations on customer broadcasts (``/v1/customer/broadcasts``).

    Example::

        bc = client.broadcasts.create(
            name="eval-fanout",
            mode="sync",
            targets=[
                {"name": "anthropic", "target_path": "anthropic"},
                {"name": "openai", "target_path": "openai"},
            ],
        )
        resp = bc.dispatch(json={"messages": [...]})   # POST /b/eval-fanout
    """

    def __init__(self, client: AuthenticatedClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    def list(self) -> BroadcastListPage:
        """List the customer's broadcasts."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_list_broadcasts

        raw = unwrap(customer_broadcasts_list_broadcasts.sync_detailed(client=self._client))
        return BroadcastListPage(
            data=[Broadcast(b, parent=self._parent) for b in raw.data],
            count=raw.count,
        )

    def get(self, broadcast_id: str | UUID) -> Broadcast:
        """Get one broadcast by id."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_get_broadcast

        raw = unwrap(customer_broadcasts_get_broadcast.sync_detailed(UUID(str(broadcast_id)), client=self._client))
        return Broadcast(raw, parent=self._parent)

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        mode: str = "sync",
        target_timeout_ms: int = 30000,
        enabled: bool = True,
        targets: builtins.list[dict[str, Any]] | None = None,
    ) -> Broadcast:
        """Create a broadcast.

        ``mode`` is ``"sync"`` (envelope of results) or ``"async"``
        (enqueued tasks). ``targets`` is an optional list of dicts, each
        with ``name`` and ``target_path`` (required) plus optional
        ``routing_key_override`` (dict) and ``sort_order``. Returns the
        created :class:`Broadcast` (dispatchable at ``/b/<name>``).
        """
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
        raw = unwrap(customer_broadcasts_create_broadcast.sync_detailed(client=self._client, body=body))
        return Broadcast(raw, parent=self._parent)

    def update(
        self,
        broadcast_id: str | UUID,
        *,
        description: Any = _UNSET,
        mode: Any = _UNSET,
        target_timeout_ms: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> Broadcast:
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
            customer_broadcasts_update_broadcast.sync_detailed(UUID(str(broadcast_id)), client=self._client, body=body)
        )
        return Broadcast(raw, parent=self._parent)

    def delete(self, broadcast_id: str | UUID) -> None:
        """Delete a broadcast."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_delete_broadcast

        unwrap(customer_broadcasts_delete_broadcast.sync_detailed(UUID(str(broadcast_id)), client=self._client))

    def add_target(
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
            customer_broadcasts_add_target.sync_detailed(UUID(str(broadcast_id)), client=self._client, body=body)
        )

    def remove_target(self, broadcast_id: str | UUID, target_id: str | UUID) -> None:
        """Remove a target from a broadcast by id."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_remove_target

        unwrap(
            customer_broadcasts_remove_target.sync_detailed(
                UUID(str(broadcast_id)), UUID(str(target_id)), client=self._client
            )
        )

    def replace_targets(self, broadcast_id: str | UUID, targets: builtins.list[dict[str, Any]]) -> Broadcast:
        """Replace all targets of a broadcast at once. Returns the refreshed broadcast."""
        from ._generated.api.customer_broadcasts import customer_broadcasts_replace_targets

        unwrap(
            customer_broadcasts_replace_targets.sync_detailed(
                UUID(str(broadcast_id)), client=self._client, body=_target_create(targets)
            )
        )
        return self.get(broadcast_id)
