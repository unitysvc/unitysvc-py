from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chains_public import ChainsPublic
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    shared: bool | Unset = False,
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

    params["shared"] = shared

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/chains/",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ChainsPublic | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ChainsPublic.from_dict(response.json())

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
) -> Response[ChainsPublic | HTTPValidationError]:
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
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ChainsPublic | HTTPValidationError]:
    """List Chains

     List customer's chains.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        shared (bool | Unset): Return only shared team chains (owner_id=NULL). Default returns the
            caller's personal chains plus shared ones. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChainsPublic | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        shared=shared,
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
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ChainsPublic | HTTPValidationError | None:
    """List Chains

     List customer's chains.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        shared (bool | Unset): Return only shared team chains (owner_id=NULL). Default returns the
            caller's personal chains plus shared ones. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChainsPublic | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        skip=skip,
        limit=limit,
        shared=shared,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ChainsPublic | HTTPValidationError]:
    """List Chains

     List customer's chains.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        shared (bool | Unset): Return only shared team chains (owner_id=NULL). Default returns the
            caller's personal chains plus shared ones. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChainsPublic | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        shared=shared,
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
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ChainsPublic | HTTPValidationError | None:
    """List Chains

     List customer's chains.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        shared (bool | Unset): Return only shared team chains (owner_id=NULL). Default returns the
            caller's personal chains plus shared ones. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChainsPublic | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            limit=limit,
            shared=shared,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
