from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.secret_public import SecretPublic
from ...models.secret_update import SecretUpdate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    name: str,
    *,
    body: SecretUpdate,
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

    params["shared"] = shared

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/secrets/{name}".format(
            name=quote(str(name), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SecretPublic | None:
    if response.status_code == 200:
        response_200 = SecretPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | SecretPublic]:
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
    body: SecretUpdate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SecretPublic]:
    """Set Secret

     Set a customer secret or variable to ``value``.

    Returns ``201 Created`` on insert and ``200 OK`` on update.
    The value is encrypted at rest. Set ``sensitive=false`` on creation to make
    the value viewable as a variable. Existing rows cannot change between
    secret and variable in place.

    The customer's context cache is invalidated so the gateway picks
    up the new value immediately.

    Args:
        name (str):
        shared (bool | Unset): When true, set the shared team secret visible to all org members.
            When false (default), set a personal secret visible only to this user. Personal secrets
            shadow same-named shared secrets for your requests. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SecretUpdate): Request body for variable-capable ``PUT /secrets/{name}`` endpoints.

            ``sensitive`` is only honored when creating rows; an existing row cannot be
            changed between secret and variable in place.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SecretPublic]
    """

    kwargs = _get_kwargs(
        name=name,
        body=body,
        shared=shared,
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
    body: SecretUpdate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SecretPublic | None:
    """Set Secret

     Set a customer secret or variable to ``value``.

    Returns ``201 Created`` on insert and ``200 OK`` on update.
    The value is encrypted at rest. Set ``sensitive=false`` on creation to make
    the value viewable as a variable. Existing rows cannot change between
    secret and variable in place.

    The customer's context cache is invalidated so the gateway picks
    up the new value immediately.

    Args:
        name (str):
        shared (bool | Unset): When true, set the shared team secret visible to all org members.
            When false (default), set a personal secret visible only to this user. Personal secrets
            shadow same-named shared secrets for your requests. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SecretUpdate): Request body for variable-capable ``PUT /secrets/{name}`` endpoints.

            ``sensitive`` is only honored when creating rows; an existing row cannot be
            changed between secret and variable in place.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SecretPublic
    """

    return sync_detailed(
        name=name,
        client=client,
        body=body,
        shared=shared,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: SecretUpdate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SecretPublic]:
    """Set Secret

     Set a customer secret or variable to ``value``.

    Returns ``201 Created`` on insert and ``200 OK`` on update.
    The value is encrypted at rest. Set ``sensitive=false`` on creation to make
    the value viewable as a variable. Existing rows cannot change between
    secret and variable in place.

    The customer's context cache is invalidated so the gateway picks
    up the new value immediately.

    Args:
        name (str):
        shared (bool | Unset): When true, set the shared team secret visible to all org members.
            When false (default), set a personal secret visible only to this user. Personal secrets
            shadow same-named shared secrets for your requests. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SecretUpdate): Request body for variable-capable ``PUT /secrets/{name}`` endpoints.

            ``sensitive`` is only honored when creating rows; an existing row cannot be
            changed between secret and variable in place.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SecretPublic]
    """

    kwargs = _get_kwargs(
        name=name,
        body=body,
        shared=shared,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: SecretUpdate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SecretPublic | None:
    """Set Secret

     Set a customer secret or variable to ``value``.

    Returns ``201 Created`` on insert and ``200 OK`` on update.
    The value is encrypted at rest. Set ``sensitive=false`` on creation to make
    the value viewable as a variable. Existing rows cannot change between
    secret and variable in place.

    The customer's context cache is invalidated so the gateway picks
    up the new value immediately.

    Args:
        name (str):
        shared (bool | Unset): When true, set the shared team secret visible to all org members.
            When false (default), set a personal secret visible only to this user. Personal secrets
            shadow same-named shared secrets for your requests. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SecretUpdate): Request body for variable-capable ``PUT /secrets/{name}`` endpoints.

            ``sensitive`` is only honored when creating rows; an existing row cannot be
            changed between secret and variable in place.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SecretPublic
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            body=body,
            shared=shared,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
