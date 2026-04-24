from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_enrollment_cancel_response import CustomerEnrollmentCancelResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    enrollment_id: UUID,
    *,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/enrollments/{enrollment_id}".format(
            enrollment_id=quote(str(enrollment_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerEnrollmentCancelResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CustomerEnrollmentCancelResponse.from_dict(response.json())

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
) -> Response[CustomerEnrollmentCancelResponse | HTTPValidationError]:
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerEnrollmentCancelResponse | HTTPValidationError]:
    """Cancel Enrollment

     Cancel (unenroll from) an enrollment.

    Sets status to ``cancelled`` and invalidates the gateway routing
    cache so in-flight requests stop being proxied. The enrollment
    row and its AccessInterfaces are preserved for potential
    reactivation via re-enrollment with matching parameters.

    Callers can only cancel their own customer's enrollments.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerEnrollmentCancelResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        enrollment_id=enrollment_id,
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerEnrollmentCancelResponse | HTTPValidationError | None:
    """Cancel Enrollment

     Cancel (unenroll from) an enrollment.

    Sets status to ``cancelled`` and invalidates the gateway routing
    cache so in-flight requests stop being proxied. The enrollment
    row and its AccessInterfaces are preserved for potential
    reactivation via re-enrollment with matching parameters.

    Callers can only cancel their own customer's enrollments.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerEnrollmentCancelResponse | HTTPValidationError
    """

    return sync_detailed(
        enrollment_id=enrollment_id,
        client=client,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerEnrollmentCancelResponse | HTTPValidationError]:
    """Cancel Enrollment

     Cancel (unenroll from) an enrollment.

    Sets status to ``cancelled`` and invalidates the gateway routing
    cache so in-flight requests stop being proxied. The enrollment
    row and its AccessInterfaces are preserved for potential
    reactivation via re-enrollment with matching parameters.

    Callers can only cancel their own customer's enrollments.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerEnrollmentCancelResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        enrollment_id=enrollment_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerEnrollmentCancelResponse | HTTPValidationError | None:
    """Cancel Enrollment

     Cancel (unenroll from) an enrollment.

    Sets status to ``cancelled`` and invalidates the gateway routing
    cache so in-flight requests stop being proxied. The enrollment
    row and its AccessInterfaces are preserved for potential
    reactivation via re-enrollment with matching parameters.

    Callers can only cancel their own customer's enrollments.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerEnrollmentCancelResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            enrollment_id=enrollment_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
