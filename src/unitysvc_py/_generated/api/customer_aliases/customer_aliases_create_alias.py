from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.service_alias_create import ServiceAliasCreate
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union



def _get_kwargs(
    *,
    body: ServiceAliasCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/aliases/",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[HTTPValidationError]:
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ServiceAliasCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[HTTPValidationError]:
    """ Create Alias

     Create a new URL alias for the current customer.

    If ``is_routing`` is True (the default) and another alias is already
    routing the same (name, request_routing_key), this one is created as
    non-routing instead. Users can later switch routing via the
    ``/aliases/{id}/route`` endpoint.

    Args:
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (ServiceAliasCreate): Schema for creating a ServiceAlias.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError]
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
    client: Union[AuthenticatedClient, Client],
    body: ServiceAliasCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[HTTPValidationError]:
    """ Create Alias

     Create a new URL alias for the current customer.

    If ``is_routing`` is True (the default) and another alias is already
    routing the same (name, request_routing_key), this one is created as
    non-routing instead. Users can later switch routing via the
    ``/aliases/{id}/route`` endpoint.

    Args:
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (ServiceAliasCreate): Schema for creating a ServiceAlias.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError
     """


    return sync_detailed(
        client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ServiceAliasCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[HTTPValidationError]:
    """ Create Alias

     Create a new URL alias for the current customer.

    If ``is_routing`` is True (the default) and another alias is already
    routing the same (name, request_routing_key), this one is created as
    non-routing instead. Users can later switch routing via the
    ``/aliases/{id}/route`` endpoint.

    Args:
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (ServiceAliasCreate): Schema for creating a ServiceAlias.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError]
     """


    kwargs = _get_kwargs(
        body=body,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ServiceAliasCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[HTTPValidationError]:
    """ Create Alias

     Create a new URL alias for the current customer.

    If ``is_routing`` is True (the default) and another alias is already
    routing the same (name, request_routing_key), this one is created as
    non-routing instead. Users can later switch routing via the
    ``/aliases/{id}/route`` endpoint.

    Args:
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (ServiceAliasCreate): Schema for creating a ServiceAlias.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError
     """


    return (await asyncio_detailed(
        client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
