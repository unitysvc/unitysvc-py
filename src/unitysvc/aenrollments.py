"""Async mirror of :mod:`unitysvc.enrollments`."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import LowLevelClient, unwrap

if TYPE_CHECKING:
    from ._generated.models.customer_enrollment import CustomerEnrollment
    from ._generated.models.customer_enrollment_cancel_response import (
        CustomerEnrollmentCancelResponse,
    )
    from ._generated.models.customer_enrollment_create_response import (
        CustomerEnrollmentCreateResponse,
    )
    from ._generated.models.enrollment_instance import EnrollmentInstance
    from ._generated.models.enrollment_instance_credentials import EnrollmentInstanceCredentials
    from ._generated.models.room_list import RoomList
    from .aclient import AsyncClient


# Statuses at which a start or stop request has finished.
INSTANCE_FINISHED = ("succeeded", "failed")


class AsyncEnrollment:
    """Async active-record wrapper. See :class:`unitysvc.enrollments.Enrollment`."""

    __slots__ = ("_raw", "_parent")

    def __init__(
        self,
        raw: CustomerEnrollment | CustomerEnrollmentCreateResponse,
        parent: AsyncClient,
    ) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<AsyncEnrollment id={raw.id!r} status={raw.status!r}>"

    async def cancel(self) -> CustomerEnrollmentCancelResponse:
        return await self._parent.enrollments.cancel(self._raw.id)

    async def rooms(self, *, kind: str | None = None) -> RoomList:
        """The rooms of this enrollment you can reach now (``client.rooms.list``
        narrowed to it)."""
        return await self._parent.rooms.list(enrollment=self._raw.id, kind=kind)

    async def refresh(self, *, include_service_details: bool = True) -> AsyncEnrollment:
        return await self._parent.enrollments.get(self._raw.id, include_service_details=include_service_details)

    async def instance(self, *, wait: int = 0) -> EnrollmentInstance:
        """This enrollment's container instance. See :meth:`Enrollments.instance`."""
        return await self._parent.enrollments.instance(self._raw.id, wait=wait)

    async def start_instance(self) -> EnrollmentInstance:
        """Start the instance. See :meth:`Enrollments.start_instance`."""
        return await self._parent.enrollments.start_instance(self._raw.id)

    async def stop_instance(self) -> EnrollmentInstance:
        """Stop the instance. See :meth:`Enrollments.stop_instance`."""
        return await self._parent.enrollments.stop_instance(self._raw.id)

    async def wait_for_instance(self, *, timeout: float = 300.0) -> EnrollmentInstance:
        """Wait for the current request to finish. See :meth:`Enrollments.wait_for_instance`."""
        return await self._parent.enrollments.wait_for_instance(self._raw.id, timeout=timeout)


@dataclass
class AsyncEnrollmentList:
    data: list[AsyncEnrollment] = field(default_factory=list)
    count: int = 0


class AsyncEnrollments:
    """Async operations on the customer's enrollments."""

    def __init__(self, client: LowLevelClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_service_details: bool = True,
        shared: bool = True,
    ) -> AsyncEnrollmentList:
        """List shared team enrollments by default; pass ``shared=False`` for personal enrollments."""
        from ._generated.api.customer import customer_list_enrollments

        raw = unwrap(
            await customer_list_enrollments.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                include_service_details=include_service_details,
                shared=shared,
            )
        )
        return AsyncEnrollmentList(
            data=[AsyncEnrollment(item, parent=self._parent) for item in raw.data],
            count=raw.count,
        )

    async def get(
        self,
        enrollment_id: str | UUID,
        *,
        include_service_details: bool = True,
    ) -> AsyncEnrollment:
        from ._generated.api.customer import customer_get_enrollment

        raw = unwrap(
            await customer_get_enrollment.asyncio_detailed(
                enrollment_id=UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
                include_service_details=include_service_details,
            )
        )
        return AsyncEnrollment(raw, parent=self._parent)

    async def create(
        self,
        *,
        service_id: str | UUID,
        parameters: dict[str, Any] | None = None,
        shared: bool = False,
        channel: str | None = None,
        policy: Sequence[dict[str, Any]] | None = None,
    ) -> AsyncEnrollment:
        """Create a personal enrollment by default; pass ``shared=True`` for team scope.

        ``channel`` picks the channel; ``policy`` approves its access requests
        (see :meth:`unitysvc.enrollments.Enrollments.create`)."""
        from ._generated.api.customer import customer_enroll
        from ._generated.models.service_enrollment_create import ServiceEnrollmentCreate

        body: dict[str, Any] = {"service_id": str(service_id)}
        if parameters:
            body["parameters"] = parameters
        if channel is not None:
            body["channel"] = channel
        if policy is not None:
            body["policy"] = [dict(entry) for entry in policy]
        raw = unwrap(
            await customer_enroll.asyncio_detailed(
                client=self._client,
                body=ServiceEnrollmentCreate.from_dict(body),
                shared=shared,
            )
        )
        return AsyncEnrollment(raw, parent=self._parent)

    async def cancel(self, enrollment_id: str | UUID) -> CustomerEnrollmentCancelResponse:
        from ._generated.api.customer import customer_cancel_enrollment

        return unwrap(
            await customer_cancel_enrollment.asyncio_detailed(
                enrollment_id=UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Container instance (start / stop / status / key)
    # ------------------------------------------------------------------
    async def instance(self, enrollment_id: str | UUID, *, wait: int = 0) -> EnrollmentInstance:
        """The enrollment's container instance: the request, its status and the pods.

        ``wait`` (0-60 seconds) holds the answer until the current request has
        finished (``succeeded`` or ``failed``) or the time is up. Raises
        :class:`~unitysvc.exceptions.NotFoundError` while nothing has been
        started. A ``failed`` instance names whose problem it is in ``fault``
        (``"platform"`` or ``"seller"``).
        """
        from ._generated.api.customer import get_enrollment_instance

        return unwrap(
            await get_enrollment_instance.asyncio_detailed(
                UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
                wait=wait,
            )
        )

    async def start_instance(self, enrollment_id: str | UUID) -> EnrollmentInstance:
        """Ask for the instance to be started (idempotent); the platform does the work.

        Returns at once with the request (status ``pending``); follow it with
        :meth:`instance` or :meth:`wait_for_instance`.
        """
        from ._generated.api.customer import start_enrollment_instance

        return unwrap(
            await start_enrollment_instance.asyncio_detailed(
                UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
            )
        )

    async def stop_instance(self, enrollment_id: str | UUID) -> EnrollmentInstance:
        """Ask for the instance to be stopped (idempotent)."""
        from ._generated.api.customer import stop_enrollment_instance

        return unwrap(
            await stop_enrollment_instance.asyncio_detailed(
                UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
            )
        )

    async def instance_credentials(self, enrollment_id: str | UUID) -> EnrollmentInstanceCredentials:
        """The instance's application key (``.key``), for calling its entries.

        Never part of :meth:`instance`; treat it as a secret.
        """
        from ._generated.api.customer import get_enrollment_instance_credentials

        return unwrap(
            await get_enrollment_instance_credentials.asyncio_detailed(
                UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
            )
        )

    async def wait_for_instance(self, enrollment_id: str | UUID, *, timeout: float = 300.0) -> EnrollmentInstance:
        """Wait until the current request has finished and return the instance.

        Returns on ``succeeded`` or ``failed`` (inspect ``status``, ``reason``
        and ``fault``). Raises :class:`TimeoutError` after ``timeout`` seconds.
        """
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"instance of enrollment {enrollment_id} did not finish in {timeout:g}s")
            state = await self.instance(enrollment_id, wait=int(min(60, max(1, remaining))))
            if state.status in INSTANCE_FINISHED:
                return state
            await asyncio.sleep(1)
