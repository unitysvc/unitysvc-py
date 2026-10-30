from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.switch_routing_response import SwitchRoutingResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    identifier: str,
    *,
    on: bool | Unset = True,
    target: None | str | Unset = UNSET,
    routing_key: None | str | Unset = UNSET,
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

    json_target: None | str | Unset
    if isinstance(target, Unset):
        json_target = UNSET
    else:
        json_target = target
    params["target"] = json_target

    json_routing_key: None | str | Unset
    if isinstance(routing_key, Unset):
        json_routing_key = UNSET
    else:
        json_routing_key = routing_key
    params["routing_key"] = json_routing_key

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/aliases/{identifier}/switch".format(
            identifier=quote(str(identifier), safe=""),
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
    identifier: str,
    *,
    client: AuthenticatedClient | Client,
    on: bool | Unset = True,
    target: None | str | Unset = UNSET,
    routing_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SwitchRoutingResponse]:
    """Switch Alias Routing

     Switch routing for an alias, selected flexibly — the one-call provider
    switch, no UUID lookup and no JSON typing.

    ``identifier`` is a full UUID, a partial UUID (>= 8 hex chars), or an alias
    **name** (strict — a name identifies the alias object). For a name,
    ``target`` (target-path substring) and ``routing_key`` (routing-key-value
    substring) are ``%LIKE%`` filters over the name's targets; both may be
    omitted to match them all. Over the match set: one → switch it; several with
    none active → the first; several with one active → the next after it,
    wrapping — so a bare ``switch <name>`` cycles the provider. ``on=False``
    turns the current one off instead.

    When ``on=True`` the sibling currently routing the same (name, routing_key)
    is atomically demoted; its id comes back as ``demoted_alias_id``. When
    ``on=False`` the alias stops routing and no sibling is auto-promoted.

    Billing is unaffected — all non-deactivated aliases accrue duration
    regardless of routing state.

    Args:
        identifier (str):
        on (bool | Unset):  Default: True.
        target (None | str | Unset): Substring %LIKE% filter on the target path (e.g. 'anth' for
            '.../anthropic-llm/...'). Omit target and routing_key to match every target of the name
            and cycle to the next.
        routing_key (None | str | Unset): Substring %LIKE% filter on any routing-key value (e.g.
            'opus').
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SwitchRoutingResponse]
    """

    kwargs = _get_kwargs(
        identifier=identifier,
        on=on,
        target=target,
        routing_key=routing_key,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    identifier: str,
    *,
    client: AuthenticatedClient | Client,
    on: bool | Unset = True,
    target: None | str | Unset = UNSET,
    routing_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SwitchRoutingResponse | None:
    """Switch Alias Routing

     Switch routing for an alias, selected flexibly — the one-call provider
    switch, no UUID lookup and no JSON typing.

    ``identifier`` is a full UUID, a partial UUID (>= 8 hex chars), or an alias
    **name** (strict — a name identifies the alias object). For a name,
    ``target`` (target-path substring) and ``routing_key`` (routing-key-value
    substring) are ``%LIKE%`` filters over the name's targets; both may be
    omitted to match them all. Over the match set: one → switch it; several with
    none active → the first; several with one active → the next after it,
    wrapping — so a bare ``switch <name>`` cycles the provider. ``on=False``
    turns the current one off instead.

    When ``on=True`` the sibling currently routing the same (name, routing_key)
    is atomically demoted; its id comes back as ``demoted_alias_id``. When
    ``on=False`` the alias stops routing and no sibling is auto-promoted.

    Billing is unaffected — all non-deactivated aliases accrue duration
    regardless of routing state.

    Args:
        identifier (str):
        on (bool | Unset):  Default: True.
        target (None | str | Unset): Substring %LIKE% filter on the target path (e.g. 'anth' for
            '.../anthropic-llm/...'). Omit target and routing_key to match every target of the name
            and cycle to the next.
        routing_key (None | str | Unset): Substring %LIKE% filter on any routing-key value (e.g.
            'opus').
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SwitchRoutingResponse
    """

    return sync_detailed(
        identifier=identifier,
        client=client,
        on=on,
        target=target,
        routing_key=routing_key,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    identifier: str,
    *,
    client: AuthenticatedClient | Client,
    on: bool | Unset = True,
    target: None | str | Unset = UNSET,
    routing_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SwitchRoutingResponse]:
    """Switch Alias Routing

     Switch routing for an alias, selected flexibly — the one-call provider
    switch, no UUID lookup and no JSON typing.

    ``identifier`` is a full UUID, a partial UUID (>= 8 hex chars), or an alias
    **name** (strict — a name identifies the alias object). For a name,
    ``target`` (target-path substring) and ``routing_key`` (routing-key-value
    substring) are ``%LIKE%`` filters over the name's targets; both may be
    omitted to match them all. Over the match set: one → switch it; several with
    none active → the first; several with one active → the next after it,
    wrapping — so a bare ``switch <name>`` cycles the provider. ``on=False``
    turns the current one off instead.

    When ``on=True`` the sibling currently routing the same (name, routing_key)
    is atomically demoted; its id comes back as ``demoted_alias_id``. When
    ``on=False`` the alias stops routing and no sibling is auto-promoted.

    Billing is unaffected — all non-deactivated aliases accrue duration
    regardless of routing state.

    Args:
        identifier (str):
        on (bool | Unset):  Default: True.
        target (None | str | Unset): Substring %LIKE% filter on the target path (e.g. 'anth' for
            '.../anthropic-llm/...'). Omit target and routing_key to match every target of the name
            and cycle to the next.
        routing_key (None | str | Unset): Substring %LIKE% filter on any routing-key value (e.g.
            'opus').
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SwitchRoutingResponse]
    """

    kwargs = _get_kwargs(
        identifier=identifier,
        on=on,
        target=target,
        routing_key=routing_key,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    identifier: str,
    *,
    client: AuthenticatedClient | Client,
    on: bool | Unset = True,
    target: None | str | Unset = UNSET,
    routing_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SwitchRoutingResponse | None:
    """Switch Alias Routing

     Switch routing for an alias, selected flexibly — the one-call provider
    switch, no UUID lookup and no JSON typing.

    ``identifier`` is a full UUID, a partial UUID (>= 8 hex chars), or an alias
    **name** (strict — a name identifies the alias object). For a name,
    ``target`` (target-path substring) and ``routing_key`` (routing-key-value
    substring) are ``%LIKE%`` filters over the name's targets; both may be
    omitted to match them all. Over the match set: one → switch it; several with
    none active → the first; several with one active → the next after it,
    wrapping — so a bare ``switch <name>`` cycles the provider. ``on=False``
    turns the current one off instead.

    When ``on=True`` the sibling currently routing the same (name, routing_key)
    is atomically demoted; its id comes back as ``demoted_alias_id``. When
    ``on=False`` the alias stops routing and no sibling is auto-promoted.

    Billing is unaffected — all non-deactivated aliases accrue duration
    regardless of routing state.

    Args:
        identifier (str):
        on (bool | Unset):  Default: True.
        target (None | str | Unset): Substring %LIKE% filter on the target path (e.g. 'anth' for
            '.../anthropic-llm/...'). Omit target and routing_key to match every target of the name
            and cycle to the next.
        routing_key (None | str | Unset): Substring %LIKE% filter on any routing-key value (e.g.
            'opus').
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
            identifier=identifier,
            client=client,
            on=on,
            target=target,
            routing_key=routing_key,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
