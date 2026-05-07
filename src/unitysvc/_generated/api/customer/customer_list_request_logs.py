import datetime
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx
from dateutil.parser import isoparse

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.request_log_list_response import RequestLogListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    service_id: None | Unset | UUID = UNSET,
    service_enrollment_id: None | Unset | UUID = UNSET,
    status_min: int | None | Unset = UNSET,
    status_max: int | None | Unset = UNSET,
    start_time: datetime.datetime | None | Unset = UNSET,
    end_time: datetime.datetime | None | Unset = UNSET,
    user_request_path: None | str | Unset = UNSET,
    error_source: None | str | Unset = UNSET,
    error_type: None | str | Unset = UNSET,
    gateway_source: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    json_service_id: None | str | Unset
    if isinstance(service_id, Unset):
        json_service_id = UNSET
    elif isinstance(service_id, UUID):
        json_service_id = str(service_id)
    else:
        json_service_id = service_id
    params["service_id"] = json_service_id

    json_service_enrollment_id: None | str | Unset
    if isinstance(service_enrollment_id, Unset):
        json_service_enrollment_id = UNSET
    elif isinstance(service_enrollment_id, UUID):
        json_service_enrollment_id = str(service_enrollment_id)
    else:
        json_service_enrollment_id = service_enrollment_id
    params["service_enrollment_id"] = json_service_enrollment_id

    json_status_min: int | None | Unset
    if isinstance(status_min, Unset):
        json_status_min = UNSET
    else:
        json_status_min = status_min
    params["status_min"] = json_status_min

    json_status_max: int | None | Unset
    if isinstance(status_max, Unset):
        json_status_max = UNSET
    else:
        json_status_max = status_max
    params["status_max"] = json_status_max

    json_start_time: None | str | Unset
    if isinstance(start_time, Unset):
        json_start_time = UNSET
    elif isinstance(start_time, datetime.datetime):
        json_start_time = start_time.isoformat()
    else:
        json_start_time = start_time
    params["start_time"] = json_start_time

    json_end_time: None | str | Unset
    if isinstance(end_time, Unset):
        json_end_time = UNSET
    elif isinstance(end_time, datetime.datetime):
        json_end_time = end_time.isoformat()
    else:
        json_end_time = end_time
    params["end_time"] = json_end_time

    json_user_request_path: None | str | Unset
    if isinstance(user_request_path, Unset):
        json_user_request_path = UNSET
    else:
        json_user_request_path = user_request_path
    params["user_request_path"] = json_user_request_path

    json_error_source: None | str | Unset
    if isinstance(error_source, Unset):
        json_error_source = UNSET
    else:
        json_error_source = error_source
    params["error_source"] = json_error_source

    json_error_type: None | str | Unset
    if isinstance(error_type, Unset):
        json_error_type = UNSET
    else:
        json_error_type = error_type
    params["error_type"] = json_error_type

    json_gateway_source: None | str | Unset
    if isinstance(gateway_source, Unset):
        json_gateway_source = UNSET
    else:
        json_gateway_source = gateway_source
    params["gateway_source"] = json_gateway_source

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/request-logs",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RequestLogListResponse | None:
    if response.status_code == 200:
        response_200 = RequestLogListResponse.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | RequestLogListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    service_id: None | Unset | UUID = UNSET,
    service_enrollment_id: None | Unset | UUID = UNSET,
    status_min: int | None | Unset = UNSET,
    status_max: int | None | Unset = UNSET,
    start_time: datetime.datetime | None | Unset = UNSET,
    end_time: datetime.datetime | None | Unset = UNSET,
    user_request_path: None | str | Unset = UNSET,
    error_source: None | str | Unset = UNSET,
    error_type: None | str | Unset = UNSET,
    gateway_source: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RequestLogListResponse]:
    """List request logs

     List request logs for the authenticated customer. Returns lightweight columns (no body/header
    fields) for fast pagination.

    Args:
        skip (int | Unset): Pagination offset Default: 0.
        limit (int | Unset): Page size Default: 50.
        service_id (None | Unset | UUID): Filter by service listing
        service_enrollment_id (None | Unset | UUID): Filter by enrollment
        status_min (int | None | Unset): Min upstream status code
        status_max (int | None | Unset): Max upstream status code
        start_time (datetime.datetime | None | Unset): Start of time range
        end_time (datetime.datetime | None | Unset): End of time range
        user_request_path (None | str | Unset): Path prefix filter
        error_source (None | str | Unset): Filter: 'gateway' or 'upstream'
        error_type (None | str | Unset): Filter by error type
        gateway_source (None | str | Unset): Filter: 'apisix' or 'backend'
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RequestLogListResponse]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        service_id=service_id,
        service_enrollment_id=service_enrollment_id,
        status_min=status_min,
        status_max=status_max,
        start_time=start_time,
        end_time=end_time,
        user_request_path=user_request_path,
        error_source=error_source,
        error_type=error_type,
        gateway_source=gateway_source,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    service_id: None | Unset | UUID = UNSET,
    service_enrollment_id: None | Unset | UUID = UNSET,
    status_min: int | None | Unset = UNSET,
    status_max: int | None | Unset = UNSET,
    start_time: datetime.datetime | None | Unset = UNSET,
    end_time: datetime.datetime | None | Unset = UNSET,
    user_request_path: None | str | Unset = UNSET,
    error_source: None | str | Unset = UNSET,
    error_type: None | str | Unset = UNSET,
    gateway_source: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RequestLogListResponse | None:
    """List request logs

     List request logs for the authenticated customer. Returns lightweight columns (no body/header
    fields) for fast pagination.

    Args:
        skip (int | Unset): Pagination offset Default: 0.
        limit (int | Unset): Page size Default: 50.
        service_id (None | Unset | UUID): Filter by service listing
        service_enrollment_id (None | Unset | UUID): Filter by enrollment
        status_min (int | None | Unset): Min upstream status code
        status_max (int | None | Unset): Max upstream status code
        start_time (datetime.datetime | None | Unset): Start of time range
        end_time (datetime.datetime | None | Unset): End of time range
        user_request_path (None | str | Unset): Path prefix filter
        error_source (None | str | Unset): Filter: 'gateway' or 'upstream'
        error_type (None | str | Unset): Filter by error type
        gateway_source (None | str | Unset): Filter: 'apisix' or 'backend'
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RequestLogListResponse
    """

    return sync_detailed(
        client=client,
        skip=skip,
        limit=limit,
        service_id=service_id,
        service_enrollment_id=service_enrollment_id,
        status_min=status_min,
        status_max=status_max,
        start_time=start_time,
        end_time=end_time,
        user_request_path=user_request_path,
        error_source=error_source,
        error_type=error_type,
        gateway_source=gateway_source,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    service_id: None | Unset | UUID = UNSET,
    service_enrollment_id: None | Unset | UUID = UNSET,
    status_min: int | None | Unset = UNSET,
    status_max: int | None | Unset = UNSET,
    start_time: datetime.datetime | None | Unset = UNSET,
    end_time: datetime.datetime | None | Unset = UNSET,
    user_request_path: None | str | Unset = UNSET,
    error_source: None | str | Unset = UNSET,
    error_type: None | str | Unset = UNSET,
    gateway_source: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RequestLogListResponse]:
    """List request logs

     List request logs for the authenticated customer. Returns lightweight columns (no body/header
    fields) for fast pagination.

    Args:
        skip (int | Unset): Pagination offset Default: 0.
        limit (int | Unset): Page size Default: 50.
        service_id (None | Unset | UUID): Filter by service listing
        service_enrollment_id (None | Unset | UUID): Filter by enrollment
        status_min (int | None | Unset): Min upstream status code
        status_max (int | None | Unset): Max upstream status code
        start_time (datetime.datetime | None | Unset): Start of time range
        end_time (datetime.datetime | None | Unset): End of time range
        user_request_path (None | str | Unset): Path prefix filter
        error_source (None | str | Unset): Filter: 'gateway' or 'upstream'
        error_type (None | str | Unset): Filter by error type
        gateway_source (None | str | Unset): Filter: 'apisix' or 'backend'
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RequestLogListResponse]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        service_id=service_id,
        service_enrollment_id=service_enrollment_id,
        status_min=status_min,
        status_max=status_max,
        start_time=start_time,
        end_time=end_time,
        user_request_path=user_request_path,
        error_source=error_source,
        error_type=error_type,
        gateway_source=gateway_source,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    service_id: None | Unset | UUID = UNSET,
    service_enrollment_id: None | Unset | UUID = UNSET,
    status_min: int | None | Unset = UNSET,
    status_max: int | None | Unset = UNSET,
    start_time: datetime.datetime | None | Unset = UNSET,
    end_time: datetime.datetime | None | Unset = UNSET,
    user_request_path: None | str | Unset = UNSET,
    error_source: None | str | Unset = UNSET,
    error_type: None | str | Unset = UNSET,
    gateway_source: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RequestLogListResponse | None:
    """List request logs

     List request logs for the authenticated customer. Returns lightweight columns (no body/header
    fields) for fast pagination.

    Args:
        skip (int | Unset): Pagination offset Default: 0.
        limit (int | Unset): Page size Default: 50.
        service_id (None | Unset | UUID): Filter by service listing
        service_enrollment_id (None | Unset | UUID): Filter by enrollment
        status_min (int | None | Unset): Min upstream status code
        status_max (int | None | Unset): Max upstream status code
        start_time (datetime.datetime | None | Unset): Start of time range
        end_time (datetime.datetime | None | Unset): End of time range
        user_request_path (None | str | Unset): Path prefix filter
        error_source (None | str | Unset): Filter: 'gateway' or 'upstream'
        error_type (None | str | Unset): Filter by error type
        gateway_source (None | str | Unset): Filter: 'apisix' or 'backend'
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RequestLogListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            limit=limit,
            service_id=service_id,
            service_enrollment_id=service_enrollment_id,
            status_min=status_min,
            status_max=status_max,
            start_time=start_time,
            end_time=end_time,
            user_request_path=user_request_path,
            error_source=error_source,
            error_type=error_type,
            gateway_source=gateway_source,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
