"""``client.chains`` — customer request chains (the ``/c/`` primitive).

A chain runs a sequence of steps where each step's **success** and
**failure** branch to a different next step — covering failover (advance
on failure) and ordered workflows (advance on success) in one construct.

Chains are **managed by UUID** (``client.chains.get(id)``) but
**dispatched by name** at ``/c/<name>`` on the gateway. This module
exposes the :class:`Chains` resource manager (``client.chains``) plus a
:class:`Chain` active-record wrapper whose step-management methods
pre-bind the chain id and which — via :class:`~unitysvc._wrappers._Wrappable`
— supports ``chain.dispatch(...)`` / ``chain.cached(...)`` / etc.
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
    from ._generated.models.chain_public import ChainPublic
    from ._generated.models.chain_step_public import ChainStepPublic
    from .client import Client


class Chain(_Wrappable):
    """Active-record wrapper around a request chain.

    Forwards field access (``ch.name``, ``ch.steps``, ``ch.enabled``, …)
    to the underlying generated :class:`ChainPublic`. Adds step-management
    methods that pre-bind this chain's id, plus ``update`` / ``delete`` /
    ``refresh``.

    Inherits :class:`~unitysvc._wrappers._Wrappable`, so the gateway
    wrapper primitives compose on the chain's ``/c/<name>`` path:
    ``ch.logged().dispatch(json=body)``, ``ch.cached(ttl="1h")``, etc.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: ChainPublic, parent: Client) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<Chain name={raw.name!r} id={raw.id!r}>"

    @property
    def path(self) -> str:
        """Gateway-relative dispatch path for this chain: ``c/<name>``."""
        return f"c/{object.__getattribute__(self, '_raw').name}"

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
        """Dispatch a request through this chain at ``/c/<name>``.

        Generic gateway dispatch on this chain's :attr:`path`. ``path`` is
        an optional sub-path appended after the chain name (e.g.
        ``"v1/chat/completions"``). Compose wrapper primitives first for
        cache/log/retry, e.g. ``ch.logged().dispatch(json=body)``.
        """
        target = self.path if not path else f"{self.path}/{path.lstrip('/')}"
        return self._parent.dispatch(target, method=method, json=json, data=data, headers=headers, timeout=timeout)

    # ------------------------------------------------------------------
    # Management (pre-bind this chain's id)
    # ------------------------------------------------------------------
    def refresh(self) -> Chain:
        """Re-fetch this chain (latest steps / metadata)."""
        return self._parent.chains.get(self._raw.id)

    def update(
        self,
        *,
        description: Any = _UNSET,
        default_timeout_ms: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> Chain:
        """Update this chain's metadata. See :meth:`Chains.update`."""
        return self._parent.chains.update(
            self._raw.id,
            description=description,
            default_timeout_ms=default_timeout_ms,
            enabled=enabled,
        )

    def delete(self) -> None:
        """Delete this chain."""
        self._parent.chains.delete(self._raw.id)

    def add_step(
        self,
        *,
        name: str,
        target_path: str,
        sort_order: int,
        on_success: str = "stop",
        on_failure: str = "continue",
        timeout_ms: int | None = None,
    ) -> ChainStepPublic:
        """Append a step. See :meth:`Chains.add_step`."""
        return self._parent.chains.add_step(
            self._raw.id,
            name=name,
            target_path=target_path,
            sort_order=sort_order,
            on_success=on_success,
            on_failure=on_failure,
            timeout_ms=timeout_ms,
        )

    def remove_step(self, step_id: str | UUID) -> None:
        """Remove a step by id."""
        self._parent.chains.remove_step(self._raw.id, step_id)

    def update_step(
        self,
        step_id: str | UUID,
        *,
        name: Any = _UNSET,
        target_path: Any = _UNSET,
        on_success: Any = _UNSET,
        on_failure: Any = _UNSET,
        timeout_ms: Any = _UNSET,
        sort_order: Any = _UNSET,
    ) -> ChainStepPublic:
        """Update one step. See :meth:`Chains.update_step`."""
        return self._parent.chains.update_step(
            self._raw.id,
            step_id,
            name=name,
            target_path=target_path,
            on_success=on_success,
            on_failure=on_failure,
            timeout_ms=timeout_ms,
            sort_order=sort_order,
        )

    def replace_steps(self, steps: builtins.list[dict[str, Any]]) -> Chain:
        """Replace all steps at once. See :meth:`Chains.replace_steps`."""
        return self._parent.chains.replace_steps(self._raw.id, steps)


@dataclass
class ChainListPage:
    """Result of :meth:`Chains.list` — ``data`` items are :class:`Chain` wrappers."""

    data: list[Chain] = field(default_factory=list)
    count: int = 0


def _step_create(steps: builtins.list[dict[str, Any]]) -> list[Any]:
    from ._generated.models.chain_step_create import ChainStepCreate
    from ._generated.types import UNSET

    return [
        ChainStepCreate(
            name=s["name"],
            target_path=s["target_path"],
            sort_order=s.get("sort_order", i),
            on_success=s.get("on_success", "stop"),
            on_failure=s.get("on_failure", "continue"),
            timeout_ms=s["timeout_ms"] if s.get("timeout_ms") is not None else UNSET,
        )
        for i, s in enumerate(steps)
    ]


class Chains:
    """Operations on customer request chains (``/v1/customer/chains``).

    Example::

        ch = client.chains.create(
            name="llm-failover",
            steps=[
                {"name": "primary", "target_path": "anthropic", "on_failure": "continue"},
                {"name": "backup", "target_path": "openai", "on_success": "stop"},
            ],
        )
        resp = ch.dispatch(json={"messages": [...]})   # POST /c/llm-failover
    """

    def __init__(self, client: AuthenticatedClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    def list(self) -> ChainListPage:
        """List the customer's chains."""
        from ._generated.api.customer_chains import customer_chains_list_chains

        raw = unwrap(customer_chains_list_chains.sync_detailed(client=self._client))
        return ChainListPage(
            data=[Chain(c, parent=self._parent) for c in raw.data],
            count=raw.count,
        )

    def get(self, chain_id: str | UUID) -> Chain:
        """Get one chain by id."""
        from ._generated.api.customer_chains import customer_chains_get_chain

        raw = unwrap(customer_chains_get_chain.sync_detailed(UUID(str(chain_id)), client=self._client))
        return Chain(raw, parent=self._parent)

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        default_timeout_ms: int = 10000,
        enabled: bool = True,
        steps: builtins.list[dict[str, Any]] | None = None,
    ) -> Chain:
        """Create a chain.

        ``steps`` is an optional list of dicts, each with ``name`` and
        ``target_path`` (required) plus optional ``sort_order``,
        ``on_success`` (default ``"stop"``), ``on_failure`` (default
        ``"continue"``), and ``timeout_ms``. Returns the created
        :class:`Chain` (dispatchable at ``/c/<name>``).
        """
        from ._generated.api.customer_chains import customer_chains_create_chain
        from ._generated.models.chain_create import ChainCreate
        from ._generated.types import UNSET

        body = ChainCreate(
            name=name,
            description=description if description is not None else UNSET,
            default_timeout_ms=default_timeout_ms,
            enabled=enabled,
            steps=_step_create(steps) if steps is not None else UNSET,
        )
        raw = unwrap(customer_chains_create_chain.sync_detailed(client=self._client, body=body))
        return Chain(raw, parent=self._parent)

    def update(
        self,
        chain_id: str | UUID,
        *,
        description: Any = _UNSET,
        default_timeout_ms: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> Chain:
        """Update a chain's metadata (only the fields you pass)."""
        from ._generated.api.customer_chains import customer_chains_update_chain
        from ._generated.models.chain_update import ChainUpdate

        body = ChainUpdate(description=description, default_timeout_ms=default_timeout_ms, enabled=enabled)
        raw = unwrap(customer_chains_update_chain.sync_detailed(UUID(str(chain_id)), client=self._client, body=body))
        return Chain(raw, parent=self._parent)

    def delete(self, chain_id: str | UUID) -> None:
        """Delete a chain."""
        from ._generated.api.customer_chains import customer_chains_delete_chain

        unwrap(customer_chains_delete_chain.sync_detailed(UUID(str(chain_id)), client=self._client))

    def add_step(
        self,
        chain_id: str | UUID,
        *,
        name: str,
        target_path: str,
        sort_order: int,
        on_success: str = "stop",
        on_failure: str = "continue",
        timeout_ms: int | None = None,
    ) -> ChainStepPublic:
        """Append a step to a chain. Returns the created step."""
        from ._generated.api.customer_chains import customer_chains_add_step
        from ._generated.models.chain_step_create import ChainStepCreate
        from ._generated.types import UNSET

        body = ChainStepCreate(
            name=name,
            target_path=target_path,
            sort_order=sort_order,
            on_success=on_success,
            on_failure=on_failure,
            timeout_ms=timeout_ms if timeout_ms is not None else UNSET,
        )
        return unwrap(customer_chains_add_step.sync_detailed(UUID(str(chain_id)), client=self._client, body=body))

    def remove_step(self, chain_id: str | UUID, step_id: str | UUID) -> None:
        """Remove a step from a chain by id."""
        from ._generated.api.customer_chains import customer_chains_remove_step

        unwrap(customer_chains_remove_step.sync_detailed(UUID(str(chain_id)), UUID(str(step_id)), client=self._client))

    def update_step(
        self,
        chain_id: str | UUID,
        step_id: str | UUID,
        *,
        name: Any = _UNSET,
        target_path: Any = _UNSET,
        on_success: Any = _UNSET,
        on_failure: Any = _UNSET,
        timeout_ms: Any = _UNSET,
        sort_order: Any = _UNSET,
    ) -> ChainStepPublic:
        """Update one step (only the fields you pass)."""
        from ._generated.api.customer_chains import customer_chains_update_step
        from ._generated.models.chain_step_update import ChainStepUpdate

        body = ChainStepUpdate(
            name=name,
            target_path=target_path,
            on_success=on_success,
            on_failure=on_failure,
            timeout_ms=timeout_ms,
            sort_order=sort_order,
        )
        return unwrap(
            customer_chains_update_step.sync_detailed(
                UUID(str(chain_id)), UUID(str(step_id)), client=self._client, body=body
            )
        )

    def replace_steps(self, chain_id: str | UUID, steps: builtins.list[dict[str, Any]]) -> Chain:
        """Replace all steps of a chain at once. Returns the refreshed chain."""
        from ._generated.api.customer_chains import customer_chains_replace_steps

        unwrap(
            customer_chains_replace_steps.sync_detailed(
                UUID(str(chain_id)), client=self._client, body=_step_create(steps)
            )
        )
        return self.get(chain_id)
