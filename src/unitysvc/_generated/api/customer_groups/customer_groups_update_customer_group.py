from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.service_collection_public import ServiceCollectionPublic
from ...models.service_collection_update import ServiceCollectionUpdate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    group_id: UUID,
    *,
    body: ServiceCollectionUpdate,
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
        "url": "/groups/{group_id}".format(
            group_id=quote(str(group_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ServiceCollectionPublic | None:
    if response.status_code == 200:
        response_200 = ServiceCollectionPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | ServiceCollectionPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: ServiceCollectionUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceCollectionPublic]:
    r"""Update Customer Group

     Update a customer-owned collection.

    Only the customer's own collections are editable. Platform groups
    are addressable by id or name but read-only: a UUID mapping to a
    visible platform group returns 403 (\"Platform groups are
    read-only\"); a UUID mapping to nothing visible returns 404.

    Args:
        group_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceCollectionUpdate): Schema for updating a ServiceCollection.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceCollectionPublic]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: ServiceCollectionUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceCollectionPublic | None:
    r"""Update Customer Group

     Update a customer-owned collection.

    Only the customer's own collections are editable. Platform groups
    are addressable by id or name but read-only: a UUID mapping to a
    visible platform group returns 403 (\"Platform groups are
    read-only\"); a UUID mapping to nothing visible returns 404.

    Args:
        group_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceCollectionUpdate): Schema for updating a ServiceCollection.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceCollectionPublic
    """

    return sync_detailed(
        group_id=group_id,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: ServiceCollectionUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceCollectionPublic]:
    r"""Update Customer Group

     Update a customer-owned collection.

    Only the customer's own collections are editable. Platform groups
    are addressable by id or name but read-only: a UUID mapping to a
    visible platform group returns 403 (\"Platform groups are
    read-only\"); a UUID mapping to nothing visible returns 404.

    Args:
        group_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceCollectionUpdate): Schema for updating a ServiceCollection.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceCollectionPublic]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: ServiceCollectionUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceCollectionPublic | None:
    r"""Update Customer Group

     Update a customer-owned collection.

    Only the customer's own collections are editable. Platform groups
    are addressable by id or name but read-only: a UUID mapping to a
    visible platform group returns 403 (\"Platform groups are
    read-only\"); a UUID mapping to nothing visible returns 404.

    Args:
        group_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceCollectionUpdate): Schema for updating a ServiceCollection.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceCollectionPublic
    """

    return (
        await asyncio_detailed(
            group_id=group_id,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
