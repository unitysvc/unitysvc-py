from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.broadcast_public import BroadcastPublic
from ...models.broadcast_target_create import BroadcastTargetCreate
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    broadcast_id: UUID,
    *,
    body: list[BroadcastTargetCreate],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/broadcasts/{broadcast_id}/targets".format(
            broadcast_id=quote(str(broadcast_id), safe=""),
        ),
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BroadcastPublic | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = BroadcastPublic.from_dict(response.json())

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
) -> Response[BroadcastPublic | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    broadcast_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: list[BroadcastTargetCreate],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[BroadcastPublic | HTTPValidationError]:
    """Replace Targets

     Replace the full target set for a broadcast.

    Args:
        broadcast_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (list[BroadcastTargetCreate]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BroadcastPublic | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        broadcast_id=broadcast_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    broadcast_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: list[BroadcastTargetCreate],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> BroadcastPublic | HTTPValidationError | None:
    """Replace Targets

     Replace the full target set for a broadcast.

    Args:
        broadcast_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (list[BroadcastTargetCreate]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BroadcastPublic | HTTPValidationError
    """

    return sync_detailed(
        broadcast_id=broadcast_id,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    broadcast_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: list[BroadcastTargetCreate],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[BroadcastPublic | HTTPValidationError]:
    """Replace Targets

     Replace the full target set for a broadcast.

    Args:
        broadcast_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (list[BroadcastTargetCreate]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BroadcastPublic | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        broadcast_id=broadcast_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    broadcast_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: list[BroadcastTargetCreate],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> BroadcastPublic | HTTPValidationError | None:
    """Replace Targets

     Replace the full target set for a broadcast.

    Args:
        broadcast_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (list[BroadcastTargetCreate]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BroadcastPublic | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            broadcast_id=broadcast_id,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
