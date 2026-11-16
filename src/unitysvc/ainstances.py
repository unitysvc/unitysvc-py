"""Async mirror of :mod:`unitysvc.instances`."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING
from uuid import UUID

from ._http import LowLevelClient, unwrap

if TYPE_CHECKING:
    from ._generated.models.enrollment_instance import EnrollmentInstance
    from ._generated.models.enrollment_instance_credentials import EnrollmentInstanceCredentials
    from .aclient import AsyncClient

# Statuses at which a start or stop request has finished.
INSTANCE_FINISHED = ("succeeded", "failed")


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

    async def wait(self, *, timeout: float = 300.0) -> EnrollmentInstance:
        """Wait until the current request has finished and return the instance.

        Returns on ``succeeded`` or ``failed`` (inspect ``status``, ``reason``
        and ``fault``). Raises :class:`TimeoutError` after ``timeout`` seconds.
        """
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"instance of enrollment {self.enrollment_id} did not finish in {timeout:g}s")
            state = await self.get(wait=int(min(60, max(1, remaining))))
            if state.status in INSTANCE_FINISHED:
                return state
            await asyncio.sleep(1)
