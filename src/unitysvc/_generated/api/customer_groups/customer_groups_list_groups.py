from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.service_group_list_response import ServiceGroupListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_name: None | str | Unset
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/groups",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ServiceGroupListResponse | None:
    if response.status_code == 200:
        response_200 = ServiceGroupListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ServiceGroupListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceGroupListResponse]:
    """List Groups

     List active platform service groups visible to the customer.

    Excludes draft/archived/private groups, empty nodes, and
    seller-owned or customer-owned groups. Ordered with ``misc``
    groups last, then by ``sort_order``, then alphabetically by name
    — matching the marketplace browse order.

    Args:
        name (None | str | Unset): Filter by name (partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceGroupListResponse]
    """

    kwargs = _get_kwargs(
        name=name,
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
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceGroupListResponse | None:
    """List Groups

     List active platform service groups visible to the customer.

    Excludes draft/archived/private groups, empty nodes, and
    seller-owned or customer-owned groups. Ordered with ``misc``
    groups last, then by ``sort_order``, then alphabetically by name
    — matching the marketplace browse order.

    Args:
        name (None | str | Unset): Filter by name (partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceGroupListResponse
    """

    return sync_detailed(
        client=client,
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceGroupListResponse]:
    """List Groups

     List active platform service groups visible to the customer.

    Excludes draft/archived/private groups, empty nodes, and
    seller-owned or customer-owned groups. Ordered with ``misc``
    groups last, then by ``sort_order``, then alphabetically by name
    — matching the marketplace browse order.

    Args:
        name (None | str | Unset): Filter by name (partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceGroupListResponse]
    """

    kwargs = _get_kwargs(
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceGroupListResponse | None:
    """List Groups

     List active platform service groups visible to the customer.

    Excludes draft/archived/private groups, empty nodes, and
    seller-owned or customer-owned groups. Ordered with ``misc``
    groups last, then by ``sort_order``, then alphabetically by name
    — matching the marketplace browse order.

    Args:
        name (None | str | Unset): Filter by name (partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceGroupListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
