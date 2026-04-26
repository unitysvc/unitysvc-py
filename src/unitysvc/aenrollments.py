"""Async mirror of :mod:`unitysvc.enrollments`."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.customer_enrollment import CustomerEnrollment
    from ._generated.models.customer_enrollment_cancel_response import (
        CustomerEnrollmentCancelResponse,
    )
    from ._generated.models.customer_enrollment_create_response import (
        CustomerEnrollmentCreateResponse,
    )
    from .aclient import AsyncClient


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

    async def refresh(self, *, include_service_details: bool = True) -> AsyncEnrollment:
        return await self._parent.enrollments.get(
            self._raw.id, include_service_details=include_service_details
        )


@dataclass
class AsyncEnrollmentList:
    data: list[AsyncEnrollment] = field(default_factory=list)
    count: int = 0


class AsyncEnrollments:
    """Async operations on the customer's enrollments."""

    def __init__(self, client: AuthenticatedClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_service_details: bool = True,
    ) -> AsyncEnrollmentList:
        from ._generated.api.customer import customer_list_enrollments

        raw = unwrap(
            await customer_list_enrollments.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                include_service_details=include_service_details,
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
    ) -> AsyncEnrollment:
        from ._generated.api.customer import customer_enroll
        from ._generated.models.service_enrollment_create import ServiceEnrollmentCreate
        from ._generated.models.service_enrollment_create_parameters_type_0 import (
            ServiceEnrollmentCreateParametersType0,
        )
        from ._generated.types import UNSET

        svc_uuid = UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id
        params_obj = ServiceEnrollmentCreateParametersType0.from_dict(parameters) if parameters else UNSET
        raw = unwrap(
            await customer_enroll.asyncio_detailed(
                client=self._client,
                body=ServiceEnrollmentCreate(
                    service_id=svc_uuid,
                    parameters=params_obj,  # type: ignore[arg-type]
                ),
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
