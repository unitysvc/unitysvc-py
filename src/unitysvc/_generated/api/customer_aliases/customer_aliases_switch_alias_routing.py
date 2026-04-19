from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.switch_routing_response import SwitchRoutingResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    alias_id: UUID,
    *,
    on: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    params["on"] = on

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/aliases/{alias_id}/switch".format(
            alias_id=quote(str(alias_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SwitchRoutingResponse | None:
    if response.status_code == 200:
        response_200 = SwitchRoutingResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SwitchRoutingResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    alias_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    on: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SwitchRoutingResponse]:
    """Switch Alias Routing

     Switch routing on or off for this alias.

    When ``on=True``, any sibling alias currently routing the same
    (name, routing_key) combo is atomically demoted. The response
    includes ``demoted_alias_id`` so the caller knows what changed.

    When ``on=False``, the alias stops routing. No sibling is
    auto-promoted — the combo will have no routing alias until one
    is explicitly switched on.

    Billing is unaffected — all non-deactivated aliases accrue duration
    regardless of routing state.

    Args:
        alias_id (UUID):
        on (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SwitchRoutingResponse]
    """

    kwargs = _get_kwargs(
        alias_id=alias_id,
        on=on,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    alias_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    on: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SwitchRoutingResponse | None:
    """Switch Alias Routing

     Switch routing on or off for this alias.

    When ``on=True``, any sibling alias currently routing the same
    (name, routing_key) combo is atomically demoted. The response
    includes ``demoted_alias_id`` so the caller knows what changed.

    When ``on=False``, the alias stops routing. No sibling is
    auto-promoted — the combo will have no routing alias until one
    is explicitly switched on.

    Billing is unaffected — all non-deactivated aliases accrue duration
    regardless of routing state.

    Args:
        alias_id (UUID):
        on (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SwitchRoutingResponse
    """

    return sync_detailed(
        alias_id=alias_id,
        client=client,
        on=on,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    alias_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    on: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SwitchRoutingResponse]:
    """Switch Alias Routing

     Switch routing on or off for this alias.

    When ``on=True``, any sibling alias currently routing the same
    (name, routing_key) combo is atomically demoted. The response
    includes ``demoted_alias_id`` so the caller knows what changed.

    When ``on=False``, the alias stops routing. No sibling is
    auto-promoted — the combo will have no routing alias until one
    is explicitly switched on.

    Billing is unaffected — all non-deactivated aliases accrue duration
    regardless of routing state.

    Args:
        alias_id (UUID):
        on (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SwitchRoutingResponse]
    """

    kwargs = _get_kwargs(
        alias_id=alias_id,
        on=on,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    alias_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    on: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SwitchRoutingResponse | None:
    """Switch Alias Routing

     Switch routing on or off for this alias.

    When ``on=True``, any sibling alias currently routing the same
    (name, routing_key) combo is atomically demoted. The response
    includes ``demoted_alias_id`` so the caller knows what changed.

    When ``on=False``, the alias stops routing. No sibling is
    auto-promoted — the combo will have no routing alias until one
    is explicitly switched on.

    Billing is unaffected — all non-deactivated aliases accrue duration
    regardless of routing state.

    Args:
        alias_id (UUID):
        on (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SwitchRoutingResponse
    """

    return (
        await asyncio_detailed(
            alias_id=alias_id,
            client=client,
            on=on,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
