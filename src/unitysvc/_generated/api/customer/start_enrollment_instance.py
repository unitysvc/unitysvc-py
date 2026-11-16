from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.enrollment_instance import EnrollmentInstance
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
        "url": "/enrollments/{enrollment_id}/instance/start".format(
            enrollment_id=quote(str(enrollment_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | EnrollmentInstance | None:
    if response.status_code == 202:
        response_202 = EnrollmentInstance.from_dict(response.json())

        return response_202

    if response.status_code == 409:
        response_409 = cast(Any, None)
        return response_409

    if response.status_code == 422:
        response_422 = cast(Any, None)
        return response_422

    if response.status_code == 503:
        response_503 = cast(Any, None)
        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | EnrollmentInstance]:
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
) -> Response[Any | EnrollmentInstance]:
    """Start Enrollment Instance

     Ask for the enrollment's instance to run. Idempotent; the agent does the work.

    Answers 202 with the instance: ``status`` is ``pending`` until the agent has started it and reports
    every service ready (``succeeded``) or that it could not (``failed``, with ``reason`` and
    ``fault``).
    A start already requested for the same configuration keeps its progress.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EnrollmentInstance]
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
) -> Any | EnrollmentInstance | None:
    """Start Enrollment Instance

     Ask for the enrollment's instance to run. Idempotent; the agent does the work.

    Answers 202 with the instance: ``status`` is ``pending`` until the agent has started it and reports
    every service ready (``succeeded``) or that it could not (``failed``, with ``reason`` and
    ``fault``).
    A start already requested for the same configuration keeps its progress.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EnrollmentInstance
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
) -> Response[Any | EnrollmentInstance]:
    """Start Enrollment Instance

     Ask for the enrollment's instance to run. Idempotent; the agent does the work.

    Answers 202 with the instance: ``status`` is ``pending`` until the agent has started it and reports
    every service ready (``succeeded``) or that it could not (``failed``, with ``reason`` and
    ``fault``).
    A start already requested for the same configuration keeps its progress.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EnrollmentInstance]
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
) -> Any | EnrollmentInstance | None:
    """Start Enrollment Instance

     Ask for the enrollment's instance to run. Idempotent; the agent does the work.

    Answers 202 with the instance: ``status`` is ``pending`` until the agent has started it and reports
    every service ready (``succeeded``) or that it could not (``failed``, with ``reason`` and
    ``fault``).
    A start already requested for the same configuration keeps its progress.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EnrollmentInstance
    """

    return (
        await asyncio_detailed(
            enrollment_id=enrollment_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
