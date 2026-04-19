from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.recurrent_request_public import RecurrentRequestPublic
from ...models.recurrent_request_update import RecurrentRequestUpdate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    request_id: UUID,
    *,
    body: RecurrentRequestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/recurrent-requests/{request_id}".format(
            request_id=quote(str(request_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RecurrentRequestPublic | None:
    if response.status_code == 200:
        response_200 = RecurrentRequestPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | RecurrentRequestPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    request_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RecurrentRequestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RecurrentRequestPublic]:
    """Update Recurrent Request

     Update a recurrent request (template, schedule, name, or status).

    Setting a schedule on a draft transitions it to active and creates
    a RedBeat entry for periodic execution.

    Args:
        request_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RecurrentRequestUpdate): Schema for updating a RecurrentRequest.

            ``request_headers`` replaces the stored dict wholesale when provided
            (partial/PATCH semantics apply at the top level, not inside the dict).
            See :class:`RecurrentRequestCreate` for the rationale.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RecurrentRequestPublic]
    """

    kwargs = _get_kwargs(
        request_id=request_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    request_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RecurrentRequestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RecurrentRequestPublic | None:
    """Update Recurrent Request

     Update a recurrent request (template, schedule, name, or status).

    Setting a schedule on a draft transitions it to active and creates
    a RedBeat entry for periodic execution.

    Args:
        request_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RecurrentRequestUpdate): Schema for updating a RecurrentRequest.

            ``request_headers`` replaces the stored dict wholesale when provided
            (partial/PATCH semantics apply at the top level, not inside the dict).
            See :class:`RecurrentRequestCreate` for the rationale.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RecurrentRequestPublic
    """

    return sync_detailed(
        request_id=request_id,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    request_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RecurrentRequestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RecurrentRequestPublic]:
    """Update Recurrent Request

     Update a recurrent request (template, schedule, name, or status).

    Setting a schedule on a draft transitions it to active and creates
    a RedBeat entry for periodic execution.

    Args:
        request_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RecurrentRequestUpdate): Schema for updating a RecurrentRequest.

            ``request_headers`` replaces the stored dict wholesale when provided
            (partial/PATCH semantics apply at the top level, not inside the dict).
            See :class:`RecurrentRequestCreate` for the rationale.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RecurrentRequestPublic]
    """

    kwargs = _get_kwargs(
        request_id=request_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    request_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RecurrentRequestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RecurrentRequestPublic | None:
    """Update Recurrent Request

     Update a recurrent request (template, schedule, name, or status).

    Setting a schedule on a draft transitions it to active and creates
    a RedBeat entry for periodic execution.

    Args:
        request_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RecurrentRequestUpdate): Schema for updating a RecurrentRequest.

            ``request_headers`` replaces the stored dict wholesale when provided
            (partial/PATCH semantics apply at the top level, not inside the dict).
            See :class:`RecurrentRequestCreate` for the rationale.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RecurrentRequestPublic
    """

    return (
        await asyncio_detailed(
            request_id=request_id,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
