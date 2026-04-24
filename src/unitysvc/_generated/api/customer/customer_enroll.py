from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_enrollment_create_response import CustomerEnrollmentCreateResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_enrollment_create import ServiceEnrollmentCreate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ServiceEnrollmentCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/enrollments/",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerEnrollmentCreateResponse | HTTPValidationError | None:
    if response.status_code == 202:
        response_202 = CustomerEnrollmentCreateResponse.from_dict(response.json())

        return response_202

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CustomerEnrollmentCreateResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceEnrollmentCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerEnrollmentCreateResponse | HTTPValidationError]:
    """Enroll

     Enroll in a service asynchronously.

    Creates a pending enrollment and dispatches a Celery task to activate it.
    Returns a task_id for polling via GET /tasks/{task_id}.

    Requires X-Role-Id header (JWT) or a svcpass customer API key with
    customer context.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceEnrollmentCreate): Model for creating new Enrollments.

            customer_id is derived from the X-Role-Id header at the route level.
            service_id references the Service identity layer (not listing_id).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerEnrollmentCreateResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
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
    body: ServiceEnrollmentCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerEnrollmentCreateResponse | HTTPValidationError | None:
    """Enroll

     Enroll in a service asynchronously.

    Creates a pending enrollment and dispatches a Celery task to activate it.
    Returns a task_id for polling via GET /tasks/{task_id}.

    Requires X-Role-Id header (JWT) or a svcpass customer API key with
    customer context.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceEnrollmentCreate): Model for creating new Enrollments.

            customer_id is derived from the X-Role-Id header at the route level.
            service_id references the Service identity layer (not listing_id).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerEnrollmentCreateResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceEnrollmentCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerEnrollmentCreateResponse | HTTPValidationError]:
    """Enroll

     Enroll in a service asynchronously.

    Creates a pending enrollment and dispatches a Celery task to activate it.
    Returns a task_id for polling via GET /tasks/{task_id}.

    Requires X-Role-Id header (JWT) or a svcpass customer API key with
    customer context.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceEnrollmentCreate): Model for creating new Enrollments.

            customer_id is derived from the X-Role-Id header at the route level.
            service_id references the Service identity layer (not listing_id).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerEnrollmentCreateResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceEnrollmentCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerEnrollmentCreateResponse | HTTPValidationError | None:
    """Enroll

     Enroll in a service asynchronously.

    Creates a pending enrollment and dispatches a Celery task to activate it.
    Returns a task_id for polling via GET /tasks/{task_id}.

    Requires X-Role-Id header (JWT) or a svcpass customer API key with
    customer context.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceEnrollmentCreate): Model for creating new Enrollments.

            customer_id is derived from the X-Role-Id header at the route level.
            service_id references the Service identity layer (not listing_id).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerEnrollmentCreateResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
