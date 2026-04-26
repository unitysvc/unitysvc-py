"""``client.enrollments`` — customer service enrollment management.

Wraps the customer-tagged ``/v1/customer/enrollments/*`` operations.
Enrollments are the customer's record of "I've opted into this
service with these parameters (optionally BYOK/BYOE credentials)."

This module exposes the :class:`Enrollments` resource manager plus
an :class:`Enrollment` active-record wrapper. Returned by
:meth:`Enrollments.create`, :meth:`Enrollments.get`, and (as items)
:meth:`Enrollments.list`. The wrapper carries the same fields as
the generated record (forwarded via ``__getattr__``) and adds
:meth:`cancel` / :meth:`refresh` so the natural chained form works:

    enr = svc.enroll(parameters={"api_key": "..."})
    while enr.status == "pending":
        time.sleep(1)
        enr = enr.refresh()
    enr.cancel()
"""

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
    from .client import Client


class Enrollment:
    """Active-record wrapper around an enrollment.

    Forwards field access (``enr.id``, ``enr.status``, ``enr.parameters``,
    …) to the underlying generated record via ``__getattr__``. Adds:

    - :meth:`cancel` — sets status to ``cancelled`` (preserves
      parameters so a re-enroll reactivates).
    - :meth:`refresh` — re-fetch the enrollment with the latest server
      state. Returns a new :class:`Enrollment` wrapping the full
      :class:`CustomerEnrollment` record (useful when this wrapper
      came from :meth:`Enrollments.create`, which returns the slim
      ack shape).
    """

    __slots__ = ("_raw", "_parent")

    def __init__(
        self,
        raw: CustomerEnrollment | CustomerEnrollmentCreateResponse,
        parent: Client,
    ) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<Enrollment id={raw.id!r} status={raw.status!r}>"

    def cancel(self) -> CustomerEnrollmentCancelResponse:
        """Cancel this enrollment. See :meth:`Enrollments.cancel`."""
        return self._parent.enrollments.cancel(self._raw.id)

    def refresh(self, *, include_service_details: bool = True) -> Enrollment:
        """Re-fetch this enrollment to observe status transitions.

        After :meth:`Enrollments.create` (or :meth:`unitysvc.services.Service.enroll`),
        the wrapper holds the slim ack response. Polling for activation
        typically looks like::

            while enr.status == "pending":
                time.sleep(1)
                enr = enr.refresh()
        """
        return self._parent.enrollments.get(
            self._raw.id, include_service_details=include_service_details
        )


@dataclass
class EnrollmentList:
    """Result of :meth:`Enrollments.list` — wraps the raw list response.

    ``data`` items are :class:`Enrollment` wrappers with bound methods.
    ``count`` mirrors the upstream response.
    """

    data: list[Enrollment] = field(default_factory=list)
    count: int = 0


class Enrollments:
    """Operations on the customer's enrollments (``/v1/customer/enrollments``).

    Example::

        enr = client.enrollments.create(
            service_id=svc.id,
            parameters={"endpoint": "https://my-host", "api_key": "..."},
        )
        # Poll for activation:
        while enr.status == "pending":
            time.sleep(1)
            enr = enr.refresh()

    Or via the :class:`~unitysvc.services.Service` shortcut:

        enr = svc.enroll(parameters={...})
    """

    def __init__(self, client: AuthenticatedClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_service_details: bool = True,
    ) -> EnrollmentList:
        """List enrollments owned by the calling customer."""
        from ._generated.api.customer import customer_list_enrollments

        raw = unwrap(
            customer_list_enrollments.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                include_service_details=include_service_details,
            )
        )
        return EnrollmentList(
            data=[Enrollment(item, parent=self._parent) for item in raw.data],
            count=raw.count,
        )

    def get(
        self,
        enrollment_id: str | UUID,
        *,
        include_service_details: bool = True,
    ) -> Enrollment:
        """Get one enrollment by UUID."""
        from ._generated.api.customer import customer_get_enrollment

        raw = unwrap(
            customer_get_enrollment.sync_detailed(
                enrollment_id=UUID(str(enrollment_id)) if not isinstance(enrollment_id, UUID) else enrollment_id,
                client=self._client,
                include_service_details=include_service_details,
            )
        )
        return Enrollment(raw, parent=self._parent)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def create(
        self,
        *,
        service_id: str | UUID,
        parameters: dict[str, Any] | None = None,
    ) -> Enrollment:
        """Enroll in a service (async — poll status via :meth:`Enrollment.refresh`).

        Returns immediately with ``status="pending"``; the server
        activates the enrollment in a background worker once required
        parameters / secrets are satisfied.

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

        raw = unwrap(
            customer_enroll.sync_detailed(
                client=self._client,
                body=ServiceEnrollmentCreate(
                    service_id=svc_uuid,
                    parameters=params_obj,  # type: ignore[arg-type]
                ),
            )
        )
        return Enrollment(raw, parent=self._parent)

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
