from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_enrollments_response import CustomerEnrollmentsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    include_service_details: bool | Unset = True,
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

    params["include_service_details"] = include_service_details

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/enrollments/",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerEnrollmentsResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CustomerEnrollmentsResponse.from_dict(response.json())

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
) -> Response[CustomerEnrollmentsResponse | HTTPValidationError]:
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
    limit: int | Unset = 100,
    include_service_details: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerEnrollmentsResponse | HTTPValidationError]:
    """List Enrollments

     List user's service enrollments with optional enriched service data.

    Uses ServiceMView for efficient data retrieval when include_service_details=True.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        include_service_details (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerEnrollmentsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        include_service_details=include_service_details,
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
    limit: int | Unset = 100,
    include_service_details: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerEnrollmentsResponse | HTTPValidationError | None:
    """List Enrollments

     List user's service enrollments with optional enriched service data.

    Uses ServiceMView for efficient data retrieval when include_service_details=True.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        include_service_details (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerEnrollmentsResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        skip=skip,
        limit=limit,
        include_service_details=include_service_details,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    include_service_details: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerEnrollmentsResponse | HTTPValidationError]:
    """List Enrollments

     List user's service enrollments with optional enriched service data.

    Uses ServiceMView for efficient data retrieval when include_service_details=True.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        include_service_details (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerEnrollmentsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        include_service_details=include_service_details,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    include_service_details: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerEnrollmentsResponse | HTTPValidationError | None:
    """List Enrollments

     List user's service enrollments with optional enriched service data.

    Uses ServiceMView for efficient data retrieval when include_service_details=True.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        include_service_details (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerEnrollmentsResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            limit=limit,
            include_service_details=include_service_details,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
