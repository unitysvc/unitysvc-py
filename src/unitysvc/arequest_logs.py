"""Async mirror of :mod:`unitysvc.request_logs`."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from ._http import unwrap
from .request_logs import _or_unset

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.logging_status_response import LoggingStatusResponse
    from ._generated.models.request_log_detail import RequestLogDetail
    from ._generated.models.request_log_list_response import RequestLogListResponse


class AsyncRequestLogs:
    """Async operations on the customer's request log.

    Mirrors :class:`unitysvc.request_logs.RequestLogs` — see that class
    for the ``start`` / ``stop`` / ``list`` / ``get`` surface and
    rationale.
    """

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def start(
        self, *, truncate_long_message: bool | None = None
    ) -> LoggingStatusResponse:
        """See :meth:`unitysvc.request_logs.RequestLogs.start`."""
        from ._generated.api.customer import customer_start_request_logging
        from ._generated.types import UNSET

        return unwrap(
            await customer_start_request_logging.asyncio_detailed(
                client=self._client,
                truncate_long_message=truncate_long_message if truncate_long_message is not None else UNSET,
            )
        )

    async def stop(self) -> LoggingStatusResponse:
        from ._generated.api.customer import customer_stop_request_logging

        return unwrap(await customer_stop_request_logging.asyncio_detailed(client=self._client))

    async def list(
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
        from ._generated.api.customer import customer_list_request_logs

        return unwrap(
            await customer_list_request_logs.asyncio_detailed(
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

    async def get(self, log_id: UUID | str) -> RequestLogDetail:
        from ._generated.api.customer import customer_get_request_log

        return unwrap(
            await customer_get_request_log.asyncio_detailed(
                log_id=log_id if isinstance(log_id, UUID) else UUID(log_id),
                client=self._client,
            )
        )
