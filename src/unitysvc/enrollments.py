"""``client.enrollments`` — customer service enrollment management.

Wraps the customer-tagged ``/v1/customer/enrollments/*`` operations.
Enrollments are the customer's record of "I've opted into this
service with these parameters (optionally BYOK/BYOE credentials)."

SDK shape:

- :meth:`list` / :meth:`get` — read-side.
- :meth:`create` — POST a new enrollment with optional parameters.
  The backend activates asynchronously; poll :meth:`get` to observe
  status transitions (``pending`` → ``active`` / ``incomplete``).
- :meth:`cancel` — unenroll (status ``cancelled``).
"""

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


class Enrollments:
    """Operations on the customer's enrollments (``/v1/customer/enrollments``).

    Example::

        enr = client.enrollments.create(
            service_id=svc.id,
            parameters={"endpoint": "https://my-host", "api_key": "..."},
        )
        # Poll for activation:
        for _ in range(10):
            enr = client.enrollments.get(enr.id)
            if enr.status != "pending":
                break
            time.sleep(1)
    """

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_service_details: bool = True,
    ) -> CustomerEnrollmentsResponse:
        """List enrollments owned by the calling customer."""
        from ._generated.api.customer import customer_list_enrollments

        return unwrap(
            customer_list_enrollments.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                include_service_details=include_service_details,
            )
        )

    def get(
        self,
        enrollment_id: str | UUID,
        *,
        include_service_details: bool = True,
    ) -> CustomerEnrollment:
        """Get one enrollment by UUID."""
        from ._generated.api.customer import customer_get_enrollment

        return unwrap(
            customer_get_enrollment.sync_detailed(
                enrollment_id=UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
                include_service_details=include_service_details,
            )
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def create(
        self,
        *,
        service_id: str | UUID,
        parameters: dict[str, Any] | None = None,
    ) -> CustomerEnrollmentCreateResponse:
        """Enroll in a service (async — poll status via :meth:`get`).

        Returns immediately with ``status="pending"`` and a Celery
        ``task_id`` for observability; the server activates the
        enrollment in a background worker once required parameters /
        secrets are satisfied.

        Args:
            service_id: Service UUID.
            parameters: Optional user parameters (BYOK/BYOE values,
                model selection, etc.). Secret-shaped keys
                (``api_key``, ``password``, ...) are masked on reads.
        """
        from ._generated.api.customer import customer_enroll
        from ._generated.models.service_enrollment_create import ServiceEnrollmentCreate
        from ._generated.models.service_enrollment_create_parameters_type_0 import (
            ServiceEnrollmentCreateParametersType0,
        )
        from ._generated.types import UNSET

        svc_uuid = UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id
        params_obj = ServiceEnrollmentCreateParametersType0.from_dict(parameters) if parameters else UNSET

        return unwrap(
            customer_enroll.sync_detailed(
                client=self._client,
                body=ServiceEnrollmentCreate(
                    service_id=svc_uuid,
                    parameters=params_obj,  # type: ignore[arg-type]
                ),
            )
        )

    def cancel(self, enrollment_id: str | UUID) -> CustomerEnrollmentCancelResponse:
        """Cancel (unenroll) — sets status to ``cancelled``.

        Access interfaces and parameters are preserved so the customer
        can re-enroll later with the same parameters to reactivate.
        """
        from ._generated.api.customer import customer_cancel_enrollment

        return unwrap(
            customer_cancel_enrollment.sync_detailed(
                enrollment_id=UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
            )
        )
