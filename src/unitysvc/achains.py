"""Async mirror of :mod:`unitysvc.chains`.

Same active-record contract: :class:`AsyncChain` wraps the generated
record and exposes ``dispatch()`` plus step-management methods that
delegate back to the parent :class:`AsyncClient`. See
:mod:`unitysvc.chains` for the full contract and field reference.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET as _UNSET
from ._http import LowLevelClient, unwrap
from .chains import _step_create

if TYPE_CHECKING:
    import httpx

    from ._generated.models.chain_public import ChainPublic
    from ._generated.models.chain_step_public import ChainStepPublic
    from .aclient import AsyncClient


class AsyncChain:
    """Active-record wrapper around a request chain (async).

    See :class:`unitysvc.chains.Chain` for the contract. Dispatched by
    name at ``/c/<name>``; managed by UUID.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: ChainPublic, parent: AsyncClient) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<AsyncChain name={raw.name!r} id={raw.id!r}>"

    @property
    def path(self) -> str:
        """Gateway-relative dispatch path for this chain: ``c/<name>``."""
        return f"c/{object.__getattribute__(self, '_raw').name}"

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
        """Dispatch a request through this chain at ``/c/<name>``.

        ``path`` is an optional sub-path appended after the chain name
        (e.g. ``"v1/chat/completions"``).
        """
        target = self.path if not path else f"{self.path}/{path.lstrip('/')}"
        return await self._parent.dispatch(
            target, method=method, json=json, data=data, headers=headers, timeout=timeout
        )

    # ------------------------------------------------------------------
    # Management (pre-bind this chain's id)
    # ------------------------------------------------------------------
    async def refresh(self) -> AsyncChain:
        """Re-fetch this chain (latest steps / metadata)."""
        return await self._parent.chains.get(self._raw.id)

    async def update(
        self,
        *,
        description: Any = _UNSET,
        default_timeout_ms: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> AsyncChain:
        """Update this chain's metadata. See :meth:`AsyncChains.update`."""
        return await self._parent.chains.update(
            self._raw.id,
            description=description,
            default_timeout_ms=default_timeout_ms,
            enabled=enabled,
        )

    async def delete(self) -> None:
        """Delete this chain."""
        await self._parent.chains.delete(self._raw.id)

    async def add_step(
        self,
        *,
        name: str,
        target_path: str,
        sort_order: int,
        on_success: str = "stop",
        on_failure: str = "continue",
        timeout_ms: int | None = None,
    ) -> ChainStepPublic:
        """Append a step. See :meth:`AsyncChains.add_step`."""
        return await self._parent.chains.add_step(
            self._raw.id,
            name=name,
            target_path=target_path,
            sort_order=sort_order,
            on_success=on_success,
            on_failure=on_failure,
            timeout_ms=timeout_ms,
        )

    async def remove_step(self, step_id: str | UUID) -> None:
        """Remove a step by id."""
        await self._parent.chains.remove_step(self._raw.id, step_id)

    async def update_step(
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
        """Update one step. See :meth:`AsyncChains.update_step`."""
        return await self._parent.chains.update_step(
            self._raw.id,
            step_id,
            name=name,
            target_path=target_path,
            on_success=on_success,
            on_failure=on_failure,
            timeout_ms=timeout_ms,
            sort_order=sort_order,
        )

    async def replace_steps(self, steps: builtins.list[dict[str, Any]]) -> AsyncChain:
        """Replace all steps at once. See :meth:`AsyncChains.replace_steps`."""
        return await self._parent.chains.replace_steps(self._raw.id, steps)


@dataclass
class AsyncChainListPage:
    """Result of :meth:`AsyncChains.list` — ``data`` items are :class:`AsyncChain`."""

    data: list[AsyncChain] = field(default_factory=list)
    count: int = 0


class AsyncChains:
    """Async operations on customer request chains (``/v1/customer/chains``).

    See :class:`unitysvc.chains.Chains` for the contract.
    """

    def __init__(self, client: LowLevelClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(self) -> AsyncChainListPage:
        """List the customer's chains."""
        from ._generated.api.customer_chains import customer_chains_list_chains

        raw = unwrap(await customer_chains_list_chains.asyncio_detailed(client=self._client))
        return AsyncChainListPage(
            data=[AsyncChain(c, parent=self._parent) for c in raw.data],
            count=raw.count,
        )

    async def get(self, chain_id: str | UUID) -> AsyncChain:
        """Get one chain by id."""
        from ._generated.api.customer_chains import customer_chains_get_chain

        raw = unwrap(await customer_chains_get_chain.asyncio_detailed(UUID(str(chain_id)), client=self._client))
        return AsyncChain(raw, parent=self._parent)

    async def create(
        self,
        *,
        name: str,
        description: str | None = None,
        default_timeout_ms: int = 10000,
        enabled: bool = True,
        steps: builtins.list[dict[str, Any]] | None = None,
    ) -> AsyncChain:
        """Create a chain. See :meth:`unitysvc.chains.Chains.create`."""
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
        raw = unwrap(await customer_chains_create_chain.asyncio_detailed(client=self._client, body=body))
        return AsyncChain(raw, parent=self._parent)

    async def update(
        self,
        chain_id: str | UUID,
        *,
        description: Any = _UNSET,
        default_timeout_ms: Any = _UNSET,
        enabled: Any = _UNSET,
    ) -> AsyncChain:
        """Update a chain's metadata (only the fields you pass)."""
        from ._generated.api.customer_chains import customer_chains_update_chain
        from ._generated.models.chain_update import ChainUpdate

        body = ChainUpdate(description=description, default_timeout_ms=default_timeout_ms, enabled=enabled)
        raw = unwrap(
            await customer_chains_update_chain.asyncio_detailed(UUID(str(chain_id)), client=self._client, body=body)
        )
        return AsyncChain(raw, parent=self._parent)

    async def delete(self, chain_id: str | UUID) -> None:
        """Delete a chain."""
        from ._generated.api.customer_chains import customer_chains_delete_chain

        unwrap(await customer_chains_delete_chain.asyncio_detailed(UUID(str(chain_id)), client=self._client))

    async def add_step(
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
        return unwrap(
            await customer_chains_add_step.asyncio_detailed(UUID(str(chain_id)), client=self._client, body=body)
        )

    async def remove_step(self, chain_id: str | UUID, step_id: str | UUID) -> None:
        """Remove a step from a chain by id."""
        from ._generated.api.customer_chains import customer_chains_remove_step

        unwrap(
            await customer_chains_remove_step.asyncio_detailed(
                UUID(str(chain_id)), UUID(str(step_id)), client=self._client
            )
        )

    async def update_step(
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
            await customer_chains_update_step.asyncio_detailed(
                UUID(str(chain_id)), UUID(str(step_id)), client=self._client, body=body
            )
        )

    async def replace_steps(self, chain_id: str | UUID, steps: builtins.list[dict[str, Any]]) -> AsyncChain:
        """Replace all steps of a chain at once. Returns the refreshed chain."""
        from ._generated.api.customer_chains import customer_chains_replace_steps

        unwrap(
            await customer_chains_replace_steps.asyncio_detailed(
                UUID(str(chain_id)), client=self._client, body=_step_create(steps)
            )
        )
        return await self.get(chain_id)
