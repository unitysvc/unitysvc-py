"""Async mirror of :mod:`unitysvc.enrollments`."""

from __future__ import annotations

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
    from ._generated.models.customer_enrollments_response import (
        CustomerEnrollmentsResponse,
    )


class AsyncEnrollments:
    """Async operations on the customer's enrollments."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_service_details: bool = True,
    ) -> CustomerEnrollmentsResponse:
        from ._generated.api.customer import customer_list_enrollments

        return unwrap(
            await customer_list_enrollments.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                include_service_details=include_service_details,
            )
        )

    async def get(
        self,
        enrollment_id: str | UUID,
        *,
        include_service_details: bool = True,
    ) -> CustomerEnrollment:
        from ._generated.api.customer import customer_get_enrollment

        return unwrap(
            await customer_get_enrollment.asyncio_detailed(
                enrollment_id=UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
                include_service_details=include_service_details,
            )
        )

    async def create(
        self,
        *,
        service_id: str | UUID,
        parameters: dict[str, Any] | None = None,
    ) -> CustomerEnrollmentCreateResponse:
        from ._generated.api.customer import customer_enroll
        from ._generated.models.service_enrollment_create import ServiceEnrollmentCreate
        from ._generated.models.service_enrollment_create_parameters_type_0 import (
            ServiceEnrollmentCreateParametersType0,
        )
        from ._generated.types import UNSET

        svc_uuid = UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id
        params_obj = ServiceEnrollmentCreateParametersType0.from_dict(parameters) if parameters else UNSET
        return unwrap(
            await customer_enroll.asyncio_detailed(
                client=self._client,
                body=ServiceEnrollmentCreate(
                    service_id=svc_uuid,
                    parameters=params_obj,  # type: ignore[arg-type]
                ),
            )
        )

    async def cancel(self, enrollment_id: str | UUID) -> CustomerEnrollmentCancelResponse:
        from ._generated.api.customer import customer_cancel_enrollment

        return unwrap(
            await customer_cancel_enrollment.asyncio_detailed(
                enrollment_id=UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
            )
        )
