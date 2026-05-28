from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_group_view import CustomerGroupView
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    name: None | str | Unset = UNSET,
    owner: str | Unset = "all",
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

    params["owner"] = owner

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
) -> HTTPValidationError | list[CustomerGroupView] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CustomerGroupView.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[CustomerGroupView]]:
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
    owner: str | Unset = "all",
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[CustomerGroupView]]:
    r"""List Groups

     List service groups visible to the customer as a single flat list.

    Merges two kinds of rows into one ``CustomerGroupView`` shape:

    - **Platform groups** (``owner_type=\"platform\"``, ``editable=False``)
      — active platform groups with at least one service. Excludes
      draft/archived/private groups, empty nodes, and seller-owned
      groups. ``member_count`` comes from the cached ``num_services``.
      Ordered with ``misc`` groups last, then by ``sort_order``, then
      alphabetically by name — matching the marketplace browse order.
    - **Own collections** (``owner_type=\"customer\"``, ``editable=True``)
      — the customer's own ``ServiceCollection`` rows. ``member_count``
      is counted live.

    The ``owner`` filter narrows this: ``system`` returns platform
    groups only, ``own`` returns collections only, ``all`` (default)
    returns both (platform first, then collections).

    Args:
        name (None | str | Unset): Filter by name (partial match)
        owner (str | Unset): Which rows to return: 'all' (platform + own), 'system' (platform
            only), or 'own' (collections only). Default: 'all'.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[CustomerGroupView]]
    """

    kwargs = _get_kwargs(
        name=name,
        owner=owner,
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
    owner: str | Unset = "all",
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | list[CustomerGroupView] | None:
    r"""List Groups

     List service groups visible to the customer as a single flat list.

    Merges two kinds of rows into one ``CustomerGroupView`` shape:

    - **Platform groups** (``owner_type=\"platform\"``, ``editable=False``)
      — active platform groups with at least one service. Excludes
      draft/archived/private groups, empty nodes, and seller-owned
      groups. ``member_count`` comes from the cached ``num_services``.
      Ordered with ``misc`` groups last, then by ``sort_order``, then
      alphabetically by name — matching the marketplace browse order.
    - **Own collections** (``owner_type=\"customer\"``, ``editable=True``)
      — the customer's own ``ServiceCollection`` rows. ``member_count``
      is counted live.

    The ``owner`` filter narrows this: ``system`` returns platform
    groups only, ``own`` returns collections only, ``all`` (default)
    returns both (platform first, then collections).

    Args:
        name (None | str | Unset): Filter by name (partial match)
        owner (str | Unset): Which rows to return: 'all' (platform + own), 'system' (platform
            only), or 'own' (collections only). Default: 'all'.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[CustomerGroupView]
    """

    return sync_detailed(
        client=client,
        name=name,
        owner=owner,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    owner: str | Unset = "all",
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[CustomerGroupView]]:
    r"""List Groups

     List service groups visible to the customer as a single flat list.

    Merges two kinds of rows into one ``CustomerGroupView`` shape:

    - **Platform groups** (``owner_type=\"platform\"``, ``editable=False``)
      — active platform groups with at least one service. Excludes
      draft/archived/private groups, empty nodes, and seller-owned
      groups. ``member_count`` comes from the cached ``num_services``.
      Ordered with ``misc`` groups last, then by ``sort_order``, then
      alphabetically by name — matching the marketplace browse order.
    - **Own collections** (``owner_type=\"customer\"``, ``editable=True``)
      — the customer's own ``ServiceCollection`` rows. ``member_count``
      is counted live.

    The ``owner`` filter narrows this: ``system`` returns platform
    groups only, ``own`` returns collections only, ``all`` (default)
    returns both (platform first, then collections).

    Args:
        name (None | str | Unset): Filter by name (partial match)
        owner (str | Unset): Which rows to return: 'all' (platform + own), 'system' (platform
            only), or 'own' (collections only). Default: 'all'.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[CustomerGroupView]]
    """

    kwargs = _get_kwargs(
        name=name,
        owner=owner,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    owner: str | Unset = "all",
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | list[CustomerGroupView] | None:
    r"""List Groups

     List service groups visible to the customer as a single flat list.

    Merges two kinds of rows into one ``CustomerGroupView`` shape:

    - **Platform groups** (``owner_type=\"platform\"``, ``editable=False``)
      — active platform groups with at least one service. Excludes
      draft/archived/private groups, empty nodes, and seller-owned
      groups. ``member_count`` comes from the cached ``num_services``.
      Ordered with ``misc`` groups last, then by ``sort_order``, then
      alphabetically by name — matching the marketplace browse order.
    - **Own collections** (``owner_type=\"customer\"``, ``editable=True``)
      — the customer's own ``ServiceCollection`` rows. ``member_count``
      is counted live.

    The ``owner`` filter narrows this: ``system`` returns platform
    groups only, ``own`` returns collections only, ``all`` (default)
    returns both (platform first, then collections).

    Args:
        name (None | str | Unset): Filter by name (partial match)
        owner (str | Unset): Which rows to return: 'all' (platform + own), 'system' (platform
            only), or 'own' (collections only). Default: 'all'.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[CustomerGroupView]
    """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            owner=owner,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
