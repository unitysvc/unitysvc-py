from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.enrollment_instance import EnrollmentInstance
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
        "method": "post",
        "url": "/enrollments/{enrollment_id}/instance/stop".format(
            enrollment_id=quote(str(enrollment_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | EnrollmentInstance | HTTPValidationError | None:
    if response.status_code == 202:
        response_202 = EnrollmentInstance.from_dict(response.json())

        return response_202

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | EnrollmentInstance | HTTPValidationError]:
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
) -> Response[Any | EnrollmentInstance | HTTPValidationError]:
    """Stop Enrollment Instance

     Ask for the enrollment's instance to be removed. Idempotent; the agent does the work.

    Answers 202 with the instance: ``status`` is ``succeeded`` once it is gone.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EnrollmentInstance | HTTPValidationError]
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
) -> Any | EnrollmentInstance | HTTPValidationError | None:
    """Stop Enrollment Instance

     Ask for the enrollment's instance to be removed. Idempotent; the agent does the work.

    Answers 202 with the instance: ``status`` is ``succeeded`` once it is gone.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EnrollmentInstance | HTTPValidationError
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
) -> Response[Any | EnrollmentInstance | HTTPValidationError]:
    """Stop Enrollment Instance

     Ask for the enrollment's instance to be removed. Idempotent; the agent does the work.

    Answers 202 with the instance: ``status`` is ``succeeded`` once it is gone.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EnrollmentInstance | HTTPValidationError]
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
) -> Any | EnrollmentInstance | HTTPValidationError | None:
    """Stop Enrollment Instance

     Ask for the enrollment's instance to be removed. Idempotent; the agent does the work.

    Answers 202 with the instance: ``status`` is ``succeeded`` once it is gone.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EnrollmentInstance | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            enrollment_id=enrollment_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
