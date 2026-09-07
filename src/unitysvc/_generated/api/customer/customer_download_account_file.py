from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_file_download_response import AccountFileDownloadResponse
from ...models.customer_download_account_file_scope import (
    CustomerDownloadAccountFileScope,
    check_customer_download_account_file_scope,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    key: str,
    scope: CustomerDownloadAccountFileScope | Unset = "personal",
    expires_in: int | Unset = 900,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    params["key"] = key

    json_scope: str | Unset = UNSET
    if not isinstance(scope, Unset):
        json_scope = scope

    params["scope"] = json_scope

    params["expires_in"] = expires_in

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/files/download",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountFileDownloadResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AccountFileDownloadResponse.from_dict(response.json())

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
) -> Response[AccountFileDownloadResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    key: str,
    scope: CustomerDownloadAccountFileScope | Unset = "personal",
    expires_in: int | Unset = 900,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[AccountFileDownloadResponse | HTTPValidationError]:
    """Download Account File

     Generate a short-TTL presigned download URL for one account file.

    The object must exist (404 otherwise) and always resolves under the
    caller's own scope root — ``key`` is relative, so other members'
    folders cannot be addressed.

    Args:
        key (str): Object key relative to the scope root
        scope (CustomerDownloadAccountFileScope | Unset): Which folder tree Default: 'personal'.
        expires_in (int | Unset):  Default: 900.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountFileDownloadResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        key=key,
        scope=scope,
        expires_in=expires_in,
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
    key: str,
    scope: CustomerDownloadAccountFileScope | Unset = "personal",
    expires_in: int | Unset = 900,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> AccountFileDownloadResponse | HTTPValidationError | None:
    """Download Account File

     Generate a short-TTL presigned download URL for one account file.

    The object must exist (404 otherwise) and always resolves under the
    caller's own scope root — ``key`` is relative, so other members'
    folders cannot be addressed.

    Args:
        key (str): Object key relative to the scope root
        scope (CustomerDownloadAccountFileScope | Unset): Which folder tree Default: 'personal'.
        expires_in (int | Unset):  Default: 900.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountFileDownloadResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        key=key,
        scope=scope,
        expires_in=expires_in,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    key: str,
    scope: CustomerDownloadAccountFileScope | Unset = "personal",
    expires_in: int | Unset = 900,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[AccountFileDownloadResponse | HTTPValidationError]:
    """Download Account File

     Generate a short-TTL presigned download URL for one account file.

    The object must exist (404 otherwise) and always resolves under the
    caller's own scope root — ``key`` is relative, so other members'
    folders cannot be addressed.

    Args:
        key (str): Object key relative to the scope root
        scope (CustomerDownloadAccountFileScope | Unset): Which folder tree Default: 'personal'.
        expires_in (int | Unset):  Default: 900.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountFileDownloadResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        key=key,
        scope=scope,
        expires_in=expires_in,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    key: str,
    scope: CustomerDownloadAccountFileScope | Unset = "personal",
    expires_in: int | Unset = 900,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> AccountFileDownloadResponse | HTTPValidationError | None:
    """Download Account File

     Generate a short-TTL presigned download URL for one account file.

    The object must exist (404 otherwise) and always resolves under the
    caller's own scope root — ``key`` is relative, so other members'
    folders cannot be addressed.

    Args:
        key (str): Object key relative to the scope root
        scope (CustomerDownloadAccountFileScope | Unset): Which folder tree Default: 'personal'.
        expires_in (int | Unset):  Default: 900.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountFileDownloadResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            key=key,
            scope=scope,
            expires_in=expires_in,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
