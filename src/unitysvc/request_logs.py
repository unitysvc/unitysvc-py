"""``client.request_logs`` — customer request log access and toggle.

Wraps the customer-tagged ``/v1/customer/request-logs/*`` operations
from the generated low-level client. Each method calls
``sync_detailed`` and passes the result through
:func:`unitysvc._http.unwrap`, so callers always get a populated typed
model or a :class:`~unitysvc.exceptions.UnitysvcSDKError`.

Two halves of the surface:

* :meth:`start` / :meth:`stop` — flip the per-user logging preference.
  Until logging is started, gateway dispatches do **not** appear in
  the listing endpoint.
* :meth:`list` / :meth:`get` — paginated list of logged requests, plus
  full detail (request/response bodies) for one row.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, TypeVar
from uuid import UUID

from ._generated.types import UNSET, Unset
from ._http import unwrap

T = TypeVar("T")

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.logging_status_response import LoggingStatusResponse
    from ._generated.models.request_log_detail import RequestLogDetail
    from ._generated.models.request_log_list_response import RequestLogListResponse


class RequestLogs:
    """Operations on the customer's request log
    (``/v1/customer/request-logs``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Toggle
    # ------------------------------------------------------------------
    def start(
        self, *, truncate_long_message: bool | None = None
    ) -> LoggingStatusResponse:
        """Enable request logging for the authenticated user.

        Subsequent gateway dispatches will be persisted and visible via
        :meth:`list` / :meth:`get`. Idempotent — safe to call when
        logging is already on.

        Args:
            truncate_long_message: Picks the storage mode.

                * ``True`` → ``truncated``: 8 KB inline preview is
                  stored, no S3 upload. The listing endpoint serves
                  the preview; :meth:`get` returns the same preview
                  (full body is not preserved).
                * ``False`` → ``complete``: full request / response
                  bodies are uploaded to S3 so :meth:`get` can return
                  the full payload. The listing endpoint still
                  returns only the preview to keep paging cheap.
                * ``None`` (default) → preserve the user's existing
                  ``preference.logging`` mode if it's already
                  ``truncated`` or ``complete``; otherwise fall back
                  to ``truncated``. Use this when the frontend has
                  already set the preference via ``PATCH /users/me``
                  and you just want to flip the gateway on. SDK
                  scripts that don't manage preferences should pass
                  ``True`` or ``False`` explicitly.
        """
        from ._generated.api.customer import customer_start_request_logging
        from ._generated.types import UNSET

        return unwrap(
            customer_start_request_logging.sync_detailed(
                client=self._client,
                truncate_long_message=truncate_long_message if truncate_long_message is not None else UNSET,
            )
        )

    def stop(self) -> LoggingStatusResponse:
        """Disable request logging for the authenticated user.

        Already-persisted rows remain visible via :meth:`list` /
        :meth:`get`; only future dispatches are skipped. Idempotent.
        """
        from ._generated.api.customer import customer_stop_request_logging

        return unwrap(customer_stop_request_logging.sync_detailed(client=self._client))

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        service_id: UUID | None = None,
        service_enrollment_id: UUID | None = None,
        status_min: int | None = None,
        status_max: int | None = None,
        start_time: datetime.datetime | None = None,
        end_time: datetime.datetime | None = None,
        user_request_path: str | None = None,
        error_source: str | None = None,
        error_type: str | None = None,
        gateway_source: str | None = None,
    ) -> RequestLogListResponse:
        """List request logs for the authenticated customer.

        Returns lightweight columns (no body / header fields) for fast
        pagination. Default time range is the last 24 hours when both
        ``start_time`` and ``end_time`` are omitted.

        Args:
            skip: Pagination offset.
            limit: Page size (1–200).
            service_id: Filter by service listing.
            service_enrollment_id: Filter by enrollment.
            status_min: Min upstream status code (100–599).
            status_max: Max upstream status code (100–599).
            start_time: Inclusive lower bound on ``event_timestamp``.
            end_time:   Inclusive upper bound on ``event_timestamp``.
            user_request_path: Path-prefix filter.
            error_source: ``"gateway"`` or ``"upstream"``.
            error_type: Filter by error type.
            gateway_source: ``"apisix"`` or ``"backend"``.
        """
        from ._generated.api.customer import customer_list_request_logs

        return unwrap(
            customer_list_request_logs.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                service_id=_or_unset(service_id),
                service_enrollment_id=_or_unset(service_enrollment_id),
                status_min=_or_unset(status_min),
                status_max=_or_unset(status_max),
                start_time=_or_unset(start_time),
                end_time=_or_unset(end_time),
                user_request_path=_or_unset(user_request_path),
                error_source=_or_unset(error_source),
                error_type=_or_unset(error_type),
                gateway_source=_or_unset(gateway_source),
            )
        )

    def get(self, log_id: UUID | str) -> RequestLogDetail:
        """Get full detail of a single request log row.

        Includes request and response bodies (subject to the
        backend's redaction rules — upstream identity and credentials
        are stripped server-side).
        """
        from ._generated.api.customer import customer_get_request_log

        return unwrap(
            customer_get_request_log.sync_detailed(
                log_id=log_id if isinstance(log_id, UUID) else UUID(log_id),
                client=self._client,
            )
        )


def _or_unset(value: T | None) -> T | Unset:
    """Map ``None`` to ``UNSET`` so the generated client omits the query
    parameter entirely instead of sending ``?param=None``."""
    return UNSET if value is None else value


