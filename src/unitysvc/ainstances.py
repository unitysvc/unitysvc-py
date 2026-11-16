"""Async mirror of :mod:`unitysvc.instances`."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING
from uuid import UUID

from ._http import LowLevelClient, unwrap
from .exceptions import InstanceSuperseded
from .instances import INSTANCE_FINISHED, _poll_seconds

if TYPE_CHECKING:
    from ._generated.models.enrollment_instance import EnrollmentInstance
    from ._generated.models.enrollment_instance_credentials import EnrollmentInstanceCredentials
    from .aclient import AsyncClient


class AsyncInstance:
    """The instance of one enrollment: ``start`` / ``stop`` / ``get`` / ``wait`` / ``credentials``."""

    def __init__(self, client: LowLevelClient, enrollment_id: str | UUID, *, parent: AsyncClient | None = None) -> None:
        self._client = client
        self._parent = parent
        self.enrollment_id = enrollment_id if isinstance(enrollment_id, UUID) else UUID(str(enrollment_id))

    def __repr__(self) -> str:
        return f"AsyncInstance(enrollment_id={self.enrollment_id})"

    async def get(self, *, wait: int = 0) -> EnrollmentInstance:
        """The request, its status and the pods.

        ``wait`` (0-60 seconds) holds the answer until the current request has
        finished (``succeeded`` or ``failed``) or the time is up. Raises
        :class:`~unitysvc.exceptions.NotFoundError` while nothing has been
        started. A ``failed`` instance names whose problem it is in ``fault``
        (``"platform"`` or ``"seller"``).
        """
        from ._generated.api.customer import get_enrollment_instance

        return unwrap(
            await get_enrollment_instance.asyncio_detailed(self.enrollment_id, client=self._client, wait=wait)
        )

    async def start(self) -> EnrollmentInstance:
        """Ask for the instance to be started (idempotent); the platform does the work.

        Returns at once with the request (status ``pending``); follow it with
        :meth:`get` or :meth:`wait`.
        """
        from ._generated.api.customer import start_enrollment_instance

        return unwrap(await start_enrollment_instance.asyncio_detailed(self.enrollment_id, client=self._client))

    async def stop(self) -> EnrollmentInstance:
        """Ask for the instance to be stopped (idempotent)."""
        from ._generated.api.customer import stop_enrollment_instance

        return unwrap(await stop_enrollment_instance.asyncio_detailed(self.enrollment_id, client=self._client))

    async def credentials(self) -> EnrollmentInstanceCredentials:
        """The instance's application key (``.key``), for calling its entries.

        Never part of :meth:`get`; treat it as a secret.
        """
        from ._generated.api.customer import get_enrollment_instance_credentials

        return unwrap(
            await get_enrollment_instance_credentials.asyncio_detailed(self.enrollment_id, client=self._client)
        )

    async def wait(self, *, timeout: float = 300.0, request: EnrollmentInstance | None = None) -> EnrollmentInstance:
        """Wait until the current request has finished and return the instance.

        Returns on ``succeeded`` or ``failed`` (inspect ``status``, ``reason``
        and ``fault``). Raises :class:`TimeoutError` after ``timeout`` seconds.

        Pass the state :meth:`start` or :meth:`stop` returned as ``request`` to wait for *that*
        request: if a newer one replaces it first (``stop`` right after your ``start``, say),
        :class:`~unitysvc.exceptions.InstanceSuperseded` is raised instead of reporting the other
        request's outcome as yours.
        """
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"instance of enrollment {self.enrollment_id} did not finish in {timeout:g}s")
            state = await self.get(wait=_poll_seconds(self._client, remaining))
            if request is not None and state.generation != request.generation:
                raise InstanceSuperseded(
                    f"{request.requested_action} #{request.generation} of enrollment {self.enrollment_id} was "
                    f"replaced by {state.requested_action} #{state.generation}"
                )
            if state.status in INSTANCE_FINISHED:
                return state
            await asyncio.sleep(1)
