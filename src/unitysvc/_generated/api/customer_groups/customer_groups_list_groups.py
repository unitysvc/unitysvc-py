from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_service_groups_response import CustomerServiceGroupsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
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

    params["skip"] = skip

    params["limit"] = limit

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
) -> CustomerServiceGroupsResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CustomerServiceGroupsResponse.from_dict(response.json())

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
) -> Response[CustomerServiceGroupsResponse | HTTPValidationError]:
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
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerServiceGroupsResponse | HTTPValidationError]:
    """List Groups

     List active platform service groups visible to the customer.

    Excludes draft/archived/private groups, empty nodes, and
    seller-owned or customer-owned groups. Ordered with ``misc``
    groups last, then by ``sort_order``, then alphabetically by name
    — matching the marketplace browse order.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        name (None | str | Unset): Filter by name (partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerServiceGroupsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
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
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerServiceGroupsResponse | HTTPValidationError | None:
    """List Groups

     List active platform service groups visible to the customer.

    Excludes draft/archived/private groups, empty nodes, and
    seller-owned or customer-owned groups. Ordered with ``misc``
    groups last, then by ``sort_order``, then alphabetically by name
    — matching the marketplace browse order.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        name (None | str | Unset): Filter by name (partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerServiceGroupsResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        skip=skip,
        limit=limit,
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerServiceGroupsResponse | HTTPValidationError]:
    """List Groups

     List active platform service groups visible to the customer.

    Excludes draft/archived/private groups, empty nodes, and
    seller-owned or customer-owned groups. Ordered with ``misc``
    groups last, then by ``sort_order``, then alphabetically by name
    — matching the marketplace browse order.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        name (None | str | Unset): Filter by name (partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerServiceGroupsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        name=name,
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
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerServiceGroupsResponse | HTTPValidationError | None:
    """List Groups

     List active platform service groups visible to the customer.

    Excludes draft/archived/private groups, empty nodes, and
    seller-owned or customer-owned groups. Ordered with ``misc``
    groups last, then by ``sort_order``, then alphabetically by name
    — matching the marketplace browse order.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        name (None | str | Unset): Filter by name (partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerServiceGroupsResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            limit=limit,
            name=name,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
