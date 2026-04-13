"""``client.recurrent_requests`` — customer recurrent-request management.

Wraps the customer-tagged ``/v1/customer/recurrent-requests/*``
operations from the generated low-level client. Recurrent requests
are scheduled HTTP requests the customer has configured against a
service enrollment.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.recurrent_request_create import RecurrentRequestCreate
    from .._generated.models.recurrent_request_public import RecurrentRequestPublic
    from .._generated.models.recurrent_request_status_enum import RecurrentRequestStatusEnum
    from .._generated.models.recurrent_request_update import RecurrentRequestUpdate
    from .._generated.models.recurrent_requests_public import RecurrentRequestsPublic


class RecurrentRequestsResource:
    """Operations on the customer's recurrent requests
    (``/v1/customer/recurrent-requests``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        service_id: str | UUID | None = None,
        enrollment_id: str | UUID | None = None,
        status: RecurrentRequestStatusEnum | str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> RecurrentRequestsPublic:
        """List recurrent requests owned by the authenticated customer."""
        from .._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_list_recurrent_requests,
        )
        from .._generated.types import UNSET

        return unwrap(
            customer_recurrent_requests_list_recurrent_requests.sync_detailed(
                client=self._client,
                service_id=(
                    UUID(str(service_id)) if service_id is not None and not isinstance(service_id, UUID) else service_id
                )
                if service_id is not None
                else UNSET,
                enrollment_id=(
                    UUID(str(enrollment_id))
                    if enrollment_id is not None and not isinstance(enrollment_id, UUID)
                    else enrollment_id
                )
                if enrollment_id is not None
                else UNSET,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
                skip=skip,
                limit=limit,
            )
        )

    def get(self, request_id: str | UUID) -> RecurrentRequestPublic:
        """Get a single recurrent request by id."""
        from .._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_get_recurrent_request_detail,
        )

        return unwrap(
            customer_recurrent_requests_get_recurrent_request_detail.sync_detailed(
                request_id=UUID(str(request_id)) if not isinstance(request_id, UUID) else request_id,
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def create(self, body: RecurrentRequestCreate | dict[str, Any]) -> RecurrentRequestPublic:
        """Create a new recurrent request."""
        from .._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_create_recurrent_request,
        )
        from .._generated.models.recurrent_request_create import RecurrentRequestCreate

        if isinstance(body, dict):
            body = RecurrentRequestCreate.from_dict(body)

        return unwrap(
            customer_recurrent_requests_create_recurrent_request.sync_detailed(
                client=self._client,
                body=body,
            )
        )

    def update(
        self,
        request_id: str | UUID,
        body: RecurrentRequestUpdate | dict[str, Any],
    ) -> RecurrentRequestPublic:
        """Update an existing recurrent request."""
        from .._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_update_recurrent_request,
        )
        from .._generated.models.recurrent_request_update import RecurrentRequestUpdate

        if isinstance(body, dict):
            body = RecurrentRequestUpdate.from_dict(body)

        return unwrap(
            customer_recurrent_requests_update_recurrent_request.sync_detailed(
                request_id=UUID(str(request_id)) if not isinstance(request_id, UUID) else request_id,
                client=self._client,
                body=body,
            )
        )

    def trigger(self, request_id: str | UUID) -> Any:
        """Force an immediate run of a recurrent request."""
        from .._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_trigger_recurrent_request,
        )

        return unwrap(
            customer_recurrent_requests_trigger_recurrent_request.sync_detailed(
                request_id=UUID(str(request_id)) if not isinstance(request_id, UUID) else request_id,
                client=self._client,
            )
        )

    def delete(self, request_id: str | UUID) -> Any:
        """Delete a recurrent request by id."""
        from .._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_remove_recurrent_request,
        )

        return unwrap(
            customer_recurrent_requests_remove_recurrent_request.sync_detailed(
                request_id=UUID(str(request_id)) if not isinstance(request_id, UUID) else request_id,
                client=self._client,
            )
        )
