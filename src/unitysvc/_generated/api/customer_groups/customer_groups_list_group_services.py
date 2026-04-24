from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_services_response import CustomerServicesResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    group_id: UUID,
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
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

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/groups/{group_id}/services".format(
            group_id=quote(str(group_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerServicesResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CustomerServicesResponse.from_dict(response.json())

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
) -> Response[CustomerServicesResponse | HTTPValidationError]:
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
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerServicesResponse | HTTPValidationError]:
    """List Group Services

     List customer-visible services that belong to a group.

    Mirrors the visibility rule used by the GraphQL
    ``resolve_group_services`` resolver for non-admin / non-seller
    callers: service must be ``status='active'`` and
    ``visibility='public'``. The group itself must be in the
    customer-visible set (active + platform + non-empty).

    Ordering is by ``name`` so SDK consumers can rely on stable
    pagination for ``group.services()``.

    Args:
        group_id (UUID):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        search (None | str | Unset): Case-insensitive substring match on display_name,
            description, provider_name, or seller_name.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerServicesResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        skip=skip,
        limit=limit,
        search=search,
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
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerServicesResponse | HTTPValidationError | None:
    """List Group Services

     List customer-visible services that belong to a group.

    Mirrors the visibility rule used by the GraphQL
    ``resolve_group_services`` resolver for non-admin / non-seller
    callers: service must be ``status='active'`` and
    ``visibility='public'``. The group itself must be in the
    customer-visible set (active + platform + non-empty).

    Ordering is by ``name`` so SDK consumers can rely on stable
    pagination for ``group.services()``.

    Args:
        group_id (UUID):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        search (None | str | Unset): Case-insensitive substring match on display_name,
            description, provider_name, or seller_name.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerServicesResponse | HTTPValidationError
    """

    return sync_detailed(
        group_id=group_id,
        client=client,
        skip=skip,
        limit=limit,
        search=search,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerServicesResponse | HTTPValidationError]:
    """List Group Services

     List customer-visible services that belong to a group.

    Mirrors the visibility rule used by the GraphQL
    ``resolve_group_services`` resolver for non-admin / non-seller
    callers: service must be ``status='active'`` and
    ``visibility='public'``. The group itself must be in the
    customer-visible set (active + platform + non-empty).

    Ordering is by ``name`` so SDK consumers can rely on stable
    pagination for ``group.services()``.

    Args:
        group_id (UUID):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        search (None | str | Unset): Case-insensitive substring match on display_name,
            description, provider_name, or seller_name.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerServicesResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        skip=skip,
        limit=limit,
        search=search,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerServicesResponse | HTTPValidationError | None:
    """List Group Services

     List customer-visible services that belong to a group.

    Mirrors the visibility rule used by the GraphQL
    ``resolve_group_services`` resolver for non-admin / non-seller
    callers: service must be ``status='active'`` and
    ``visibility='public'``. The group itself must be in the
    customer-visible set (active + platform + non-empty).

    Ordering is by ``name`` so SDK consumers can rely on stable
    pagination for ``group.services()``.

    Args:
        group_id (UUID):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        search (None | str | Unset): Case-insensitive substring match on display_name,
            description, provider_name, or seller_name.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerServicesResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            group_id=group_id,
            client=client,
            skip=skip,
            limit=limit,
            search=search,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
