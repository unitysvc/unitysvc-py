from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cursor_page_service_summary import CursorPageServiceSummary
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    name: str,
    *,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
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

    json_cursor: None | str | Unset
    if isinstance(cursor, Unset):
        json_cursor = UNSET
    else:
        json_cursor = cursor
    params["cursor"] = json_cursor

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
        "url": "/groups/{name}/services".format(
            name=quote(str(name), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CursorPageServiceSummary | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CursorPageServiceSummary.from_dict(response.json())

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
) -> Response[CursorPageServiceSummary | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    search: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CursorPageServiceSummary | HTTPValidationError]:
    """List Group Services

     List customer-visible services that belong to a group.

    The group is identified by its name (not UUID) so SDK scripts
    keep working if an admin recreates the group with the same slug.
    Mirrors the visibility rule used by the GraphQL
    ``resolve_group_services`` resolver for non-admin / non-seller
    callers: service must be ``status='active'`` and
    ``visibility='public'``. The group itself must be in the
    customer-visible set (active + platform + non-empty).

    Uses keyset pagination on ``(created_at DESC, service_id DESC)``
    to match the seller ``services_list`` endpoint — clients echo
    ``next_cursor`` back unchanged to fetch subsequent pages.

    Args:
        name (str):
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        search (None | str | Unset): Case-insensitive substring match on name, display_name, or
            provider_name.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CursorPageServiceSummary | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        cursor=cursor,
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
    name: str,
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    search: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CursorPageServiceSummary | HTTPValidationError | None:
    """List Group Services

     List customer-visible services that belong to a group.

    The group is identified by its name (not UUID) so SDK scripts
    keep working if an admin recreates the group with the same slug.
    Mirrors the visibility rule used by the GraphQL
    ``resolve_group_services`` resolver for non-admin / non-seller
    callers: service must be ``status='active'`` and
    ``visibility='public'``. The group itself must be in the
    customer-visible set (active + platform + non-empty).

    Uses keyset pagination on ``(created_at DESC, service_id DESC)``
    to match the seller ``services_list`` endpoint — clients echo
    ``next_cursor`` back unchanged to fetch subsequent pages.

    Args:
        name (str):
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        search (None | str | Unset): Case-insensitive substring match on name, display_name, or
            provider_name.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CursorPageServiceSummary | HTTPValidationError
    """

    return sync_detailed(
        name=name,
        client=client,
        cursor=cursor,
        limit=limit,
        search=search,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    search: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CursorPageServiceSummary | HTTPValidationError]:
    """List Group Services

     List customer-visible services that belong to a group.

    The group is identified by its name (not UUID) so SDK scripts
    keep working if an admin recreates the group with the same slug.
    Mirrors the visibility rule used by the GraphQL
    ``resolve_group_services`` resolver for non-admin / non-seller
    callers: service must be ``status='active'`` and
    ``visibility='public'``. The group itself must be in the
    customer-visible set (active + platform + non-empty).

    Uses keyset pagination on ``(created_at DESC, service_id DESC)``
    to match the seller ``services_list`` endpoint — clients echo
    ``next_cursor`` back unchanged to fetch subsequent pages.

    Args:
        name (str):
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        search (None | str | Unset): Case-insensitive substring match on name, display_name, or
            provider_name.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CursorPageServiceSummary | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        cursor=cursor,
        limit=limit,
        search=search,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    search: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CursorPageServiceSummary | HTTPValidationError | None:
    """List Group Services

     List customer-visible services that belong to a group.

    The group is identified by its name (not UUID) so SDK scripts
    keep working if an admin recreates the group with the same slug.
    Mirrors the visibility rule used by the GraphQL
    ``resolve_group_services`` resolver for non-admin / non-seller
    callers: service must be ``status='active'`` and
    ``visibility='public'``. The group itself must be in the
    customer-visible set (active + platform + non-empty).

    Uses keyset pagination on ``(created_at DESC, service_id DESC)``
    to match the seller ``services_list`` endpoint — clients echo
    ``next_cursor`` back unchanged to fetch subsequent pages.

    Args:
        name (str):
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        search (None | str | Unset): Case-insensitive substring match on name, display_name, or
            provider_name.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CursorPageServiceSummary | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            cursor=cursor,
            limit=limit,
            search=search,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
