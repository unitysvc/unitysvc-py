from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.recurrent_request_status_enum import RecurrentRequestStatusEnum, check_recurrent_request_status_enum
from ...models.recurrent_requests_public import RecurrentRequestsPublic
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    service_id: None | Unset | UUID = UNSET,
    enrollment_id: None | Unset | UUID = UNSET,
    status: None | RecurrentRequestStatusEnum | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_service_id: None | str | Unset
    if isinstance(service_id, Unset):
        json_service_id = UNSET
    elif isinstance(service_id, UUID):
        json_service_id = str(service_id)
    else:
        json_service_id = service_id
    params["service_id"] = json_service_id

    json_enrollment_id: None | str | Unset
    if isinstance(enrollment_id, Unset):
        json_enrollment_id = UNSET
    elif isinstance(enrollment_id, UUID):
        json_enrollment_id = str(enrollment_id)
    else:
        json_enrollment_id = enrollment_id
    params["enrollment_id"] = json_enrollment_id

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, str):
        json_status = status
    else:
        json_status = status
    params["status"] = json_status

    params["skip"] = skip

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/recurrent-requests/",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RecurrentRequestsPublic | None:
    if response.status_code == 200:
        response_200 = RecurrentRequestsPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | RecurrentRequestsPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    service_id: None | Unset | UUID = UNSET,
    enrollment_id: None | Unset | UUID = UNSET,
    status: None | RecurrentRequestStatusEnum | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RecurrentRequestsPublic]:
    """List Recurrent Requests

     List recurrent requests for the current customer.

    Args:
        service_id (None | Unset | UUID):
        enrollment_id (None | Unset | UUID):
        status (None | RecurrentRequestStatusEnum | Unset):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RecurrentRequestsPublic]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        enrollment_id=enrollment_id,
        status=status,
        skip=skip,
        limit=limit,
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
    service_id: None | Unset | UUID = UNSET,
    enrollment_id: None | Unset | UUID = UNSET,
    status: None | RecurrentRequestStatusEnum | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RecurrentRequestsPublic | None:
    """List Recurrent Requests

     List recurrent requests for the current customer.

    Args:
        service_id (None | Unset | UUID):
        enrollment_id (None | Unset | UUID):
        status (None | RecurrentRequestStatusEnum | Unset):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RecurrentRequestsPublic
    """

    return sync_detailed(
        client=client,
        service_id=service_id,
        enrollment_id=enrollment_id,
        status=status,
        skip=skip,
        limit=limit,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    service_id: None | Unset | UUID = UNSET,
    enrollment_id: None | Unset | UUID = UNSET,
    status: None | RecurrentRequestStatusEnum | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RecurrentRequestsPublic]:
    """List Recurrent Requests

     List recurrent requests for the current customer.

    Args:
        service_id (None | Unset | UUID):
        enrollment_id (None | Unset | UUID):
        status (None | RecurrentRequestStatusEnum | Unset):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RecurrentRequestsPublic]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        enrollment_id=enrollment_id,
        status=status,
        skip=skip,
        limit=limit,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    service_id: None | Unset | UUID = UNSET,
    enrollment_id: None | Unset | UUID = UNSET,
    status: None | RecurrentRequestStatusEnum | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RecurrentRequestsPublic | None:
    """List Recurrent Requests

     List recurrent requests for the current customer.

    Args:
        service_id (None | Unset | UUID):
        enrollment_id (None | Unset | UUID):
        status (None | RecurrentRequestStatusEnum | Unset):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RecurrentRequestsPublic
    """

    return (
        await asyncio_detailed(
            client=client,
            service_id=service_id,
            enrollment_id=enrollment_id,
            status=status,
            skip=skip,
            limit=limit,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
