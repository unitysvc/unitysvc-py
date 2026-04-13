from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.recurrent_request_public import RecurrentRequestPublic
from ...models.recurrent_request_update import RecurrentRequestUpdate
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID



def _get_kwargs(
    request_id: UUID,
    *,
    body: RecurrentRequestUpdate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/recurrent-requests/{request_id}".format(request_id=request_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[HTTPValidationError, RecurrentRequestPublic]]:
    if response.status_code == 200:
        response_200 = RecurrentRequestPublic.from_dict(response.json())



        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[HTTPValidationError, RecurrentRequestPublic]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    request_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RecurrentRequestUpdate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[HTTPValidationError, RecurrentRequestPublic]]:
    """ Update Recurrent Request

     Update a recurrent request (template, schedule, name, or status).

    Setting a schedule on a draft transitions it to active and creates
    a RedBeat entry for periodic execution.

    Args:
        request_id (UUID):
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (RecurrentRequestUpdate): Schema for updating a RecurrentRequest.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RecurrentRequestPublic]]
     """


    kwargs = _get_kwargs(
        request_id=request_id,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    request_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RecurrentRequestUpdate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[HTTPValidationError, RecurrentRequestPublic]]:
    """ Update Recurrent Request

     Update a recurrent request (template, schedule, name, or status).

    Setting a schedule on a draft transitions it to active and creates
    a RedBeat entry for periodic execution.

    Args:
        request_id (UUID):
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (RecurrentRequestUpdate): Schema for updating a RecurrentRequest.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RecurrentRequestPublic]
     """


    return sync_detailed(
        request_id=request_id,
client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    request_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RecurrentRequestUpdate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[HTTPValidationError, RecurrentRequestPublic]]:
    """ Update Recurrent Request

     Update a recurrent request (template, schedule, name, or status).

    Setting a schedule on a draft transitions it to active and creates
    a RedBeat entry for periodic execution.

    Args:
        request_id (UUID):
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (RecurrentRequestUpdate): Schema for updating a RecurrentRequest.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RecurrentRequestPublic]]
     """


    kwargs = _get_kwargs(
        request_id=request_id,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    request_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RecurrentRequestUpdate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[HTTPValidationError, RecurrentRequestPublic]]:
    """ Update Recurrent Request

     Update a recurrent request (template, schedule, name, or status).

    Setting a schedule on a draft transitions it to active and creates
    a RedBeat entry for periodic execution.

    Args:
        request_id (UUID):
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (RecurrentRequestUpdate): Schema for updating a RecurrentRequest.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RecurrentRequestPublic]
     """


    return (await asyncio_detailed(
        request_id=request_id,
client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
