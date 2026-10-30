from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_file_delete_request import AccountFileDeleteRequest
from ...models.account_file_delete_response import AccountFileDeleteResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: AccountFileDeleteRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/files/delete",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountFileDeleteResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AccountFileDeleteResponse.from_dict(response.json())

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
) -> Response[AccountFileDeleteResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AccountFileDeleteRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[AccountFileDeleteResponse | HTTPValidationError]:
    """Delete Account Files

     Delete a file, or a folder (``path`` ending in ``/``) and everything
    in it: a home folder, a service's or an enrollment's files. ``deleted``
    counts the objects removed; nothing to delete is 0. The root itself is
    not deleted in one call. A failure part way through a folder (503) may
    leave it partly deleted; deleting it again finishes the job.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (AccountFileDeleteRequest): A file, or a folder (ending in ``/``) and everything in
            it.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountFileDeleteResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
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
    body: AccountFileDeleteRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> AccountFileDeleteResponse | HTTPValidationError | None:
    """Delete Account Files

     Delete a file, or a folder (``path`` ending in ``/``) and everything
    in it: a home folder, a service's or an enrollment's files. ``deleted``
    counts the objects removed; nothing to delete is 0. The root itself is
    not deleted in one call. A failure part way through a folder (503) may
    leave it partly deleted; deleting it again finishes the job.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (AccountFileDeleteRequest): A file, or a folder (ending in ``/``) and everything in
            it.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountFileDeleteResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AccountFileDeleteRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[AccountFileDeleteResponse | HTTPValidationError]:
    """Delete Account Files

     Delete a file, or a folder (``path`` ending in ``/``) and everything
    in it: a home folder, a service's or an enrollment's files. ``deleted``
    counts the objects removed; nothing to delete is 0. The root itself is
    not deleted in one call. A failure part way through a folder (503) may
    leave it partly deleted; deleting it again finishes the job.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (AccountFileDeleteRequest): A file, or a folder (ending in ``/``) and everything in
            it.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountFileDeleteResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: AccountFileDeleteRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> AccountFileDeleteResponse | HTTPValidationError | None:
    """Delete Account Files

     Delete a file, or a folder (``path`` ending in ``/``) and everything
    in it: a home folder, a service's or an enrollment's files. ``deleted``
    counts the objects removed; nothing to delete is 0. The root itself is
    not deleted in one call. A failure part way through a folder (503) may
    leave it partly deleted; deleting it again finishes the job.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (AccountFileDeleteRequest): A file, or a folder (ending in ``/``) and everything in
            it.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountFileDeleteResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
