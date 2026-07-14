from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_file_upload_request import AccountFileUploadRequest
from ...models.account_file_upload_response import AccountFileUploadResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: AccountFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/files/upload",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountFileUploadResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AccountFileUploadResponse.from_dict(response.json())

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
) -> Response[AccountFileUploadResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: AccountFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> Response[AccountFileUploadResponse | HTTPValidationError]:
    """Upload Account File

     Mint a presigned-POST ticket for one direct-to-storage upload.

    Bytes never transit this API: POST the returned ``fields`` plus the
    file (last, field name ``file``) as multipart form data to ``url``.
    The key lands under the caller's scope root at ``{path}{filename}``
    (existing objects with the same key are overwritten, like a home
    directory); the size ceiling is enforced by the signed policy, not
    the declared ``size``. ``scope=shared`` requires a team/enterprise
    plan.

    Args:
        x_role_id (None | str | Unset):
        body (AccountFileUploadRequest): Mint request for one direct-to-storage upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountFileUploadResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: AccountFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> AccountFileUploadResponse | HTTPValidationError | None:
    """Upload Account File

     Mint a presigned-POST ticket for one direct-to-storage upload.

    Bytes never transit this API: POST the returned ``fields`` plus the
    file (last, field name ``file``) as multipart form data to ``url``.
    The key lands under the caller's scope root at ``{path}{filename}``
    (existing objects with the same key are overwritten, like a home
    directory); the size ceiling is enforced by the signed policy, not
    the declared ``size``. ``scope=shared`` requires a team/enterprise
    plan.

    Args:
        x_role_id (None | str | Unset):
        body (AccountFileUploadRequest): Mint request for one direct-to-storage upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountFileUploadResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: AccountFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> Response[AccountFileUploadResponse | HTTPValidationError]:
    """Upload Account File

     Mint a presigned-POST ticket for one direct-to-storage upload.

    Bytes never transit this API: POST the returned ``fields`` plus the
    file (last, field name ``file``) as multipart form data to ``url``.
    The key lands under the caller's scope root at ``{path}{filename}``
    (existing objects with the same key are overwritten, like a home
    directory); the size ceiling is enforced by the signed policy, not
    the declared ``size``. ``scope=shared`` requires a team/enterprise
    plan.

    Args:
        x_role_id (None | str | Unset):
        body (AccountFileUploadRequest): Mint request for one direct-to-storage upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountFileUploadResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: AccountFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> AccountFileUploadResponse | HTTPValidationError | None:
    """Upload Account File

     Mint a presigned-POST ticket for one direct-to-storage upload.

    Bytes never transit this API: POST the returned ``fields`` plus the
    file (last, field name ``file``) as multipart form data to ``url``.
    The key lands under the caller's scope root at ``{path}{filename}``
    (existing objects with the same key are overwritten, like a home
    directory); the size ceiling is enforced by the signed policy, not
    the declared ``size``. ``scope=shared`` requires a team/enterprise
    plan.

    Args:
        x_role_id (None | str | Unset):
        body (AccountFileUploadRequest): Mint request for one direct-to-storage upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountFileUploadResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_role_id=x_role_id,
        )
    ).parsed
