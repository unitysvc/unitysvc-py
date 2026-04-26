from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_enrollment import CustomerEnrollment
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    enrollment_id: UUID,
    *,
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

    params["include_service_details"] = include_service_details

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/enrollments/{enrollment_id}".format(
            enrollment_id=quote(str(enrollment_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerEnrollment | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CustomerEnrollment.from_dict(response.json())

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
) -> Response[CustomerEnrollment | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    include_service_details: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerEnrollment | HTTPValidationError]:
    """Get Enrollment

     Get a specific enrollment by ID with enriched service data.
    Users can only access their own customer's enrollments.

    Uses ServiceMView and AccessInterface resolution for comprehensive data.

    Args:
        enrollment_id (UUID):
        include_service_details (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerEnrollment | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        enrollment_id=enrollment_id,
        include_service_details=include_service_details,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    include_service_details: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerEnrollment | HTTPValidationError | None:
    """Get Enrollment

     Get a specific enrollment by ID with enriched service data.
    Users can only access their own customer's enrollments.

    Uses ServiceMView and AccessInterface resolution for comprehensive data.

    Args:
        enrollment_id (UUID):
        include_service_details (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerEnrollment | HTTPValidationError
    """

    return sync_detailed(
        enrollment_id=enrollment_id,
        client=client,
        include_service_details=include_service_details,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    include_service_details: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerEnrollment | HTTPValidationError]:
    """Get Enrollment

     Get a specific enrollment by ID with enriched service data.
    Users can only access their own customer's enrollments.

    Uses ServiceMView and AccessInterface resolution for comprehensive data.

    Args:
        enrollment_id (UUID):
        include_service_details (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerEnrollment | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        enrollment_id=enrollment_id,
        include_service_details=include_service_details,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    include_service_details: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerEnrollment | HTTPValidationError | None:
    """Get Enrollment

     Get a specific enrollment by ID with enriched service data.
    Users can only access their own customer's enrollments.

    Uses ServiceMView and AccessInterface resolution for comprehensive data.

    Args:
        enrollment_id (UUID):
        include_service_details (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerEnrollment | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            enrollment_id=enrollment_id,
            client=client,
            include_service_details=include_service_details,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
