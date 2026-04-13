from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.recurrent_request_status_enum import check_recurrent_request_status_enum
from ...models.recurrent_request_status_enum import RecurrentRequestStatusEnum
from ...models.recurrent_requests_public import RecurrentRequestsPublic
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID



def _get_kwargs(
    *,
    service_id: Union[None, UUID, Unset] = UNSET,
    enrollment_id: Union[None, UUID, Unset] = UNSET,
    status: Union[None, RecurrentRequestStatusEnum, Unset] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    params: dict[str, Any] = {}

    json_service_id: Union[None, Unset, str]
    if isinstance(service_id, Unset):
        json_service_id = UNSET
    elif isinstance(service_id, UUID):
        json_service_id = str(service_id)
    else:
        json_service_id = service_id
    params["service_id"] = json_service_id

    json_enrollment_id: Union[None, Unset, str]
    if isinstance(enrollment_id, Unset):
        json_enrollment_id = UNSET
    elif isinstance(enrollment_id, UUID):
        json_enrollment_id = str(enrollment_id)
    else:
        json_enrollment_id = enrollment_id
    params["enrollment_id"] = json_enrollment_id

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, str):
        json_status = status
    else:
        json_status = status
    params["status"] = json_status

    params["skip"] = skip

    params["limit"] = limit


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/recurrent-requests/",
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[HTTPValidationError, RecurrentRequestsPublic]]:
    if response.status_code == 200:
        response_200 = RecurrentRequestsPublic.from_dict(response.json())



        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[HTTPValidationError, RecurrentRequestsPublic]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    service_id: Union[None, UUID, Unset] = UNSET,
    enrollment_id: Union[None, UUID, Unset] = UNSET,
    status: Union[None, RecurrentRequestStatusEnum, Unset] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[HTTPValidationError, RecurrentRequestsPublic]]:
    """ List Recurrent Requests

     List recurrent requests for the current customer.

    Args:
        service_id (Union[None, UUID, Unset]):
        enrollment_id (Union[None, UUID, Unset]):
        status (Union[None, RecurrentRequestStatusEnum, Unset]):
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RecurrentRequestsPublic]]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
enrollment_id=enrollment_id,
status=status,
skip=skip,
limit=limit,
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
    service_id: Union[None, UUID, Unset] = UNSET,
    enrollment_id: Union[None, UUID, Unset] = UNSET,
    status: Union[None, RecurrentRequestStatusEnum, Unset] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[HTTPValidationError, RecurrentRequestsPublic]]:
    """ List Recurrent Requests

     List recurrent requests for the current customer.

    Args:
        service_id (Union[None, UUID, Unset]):
        enrollment_id (Union[None, UUID, Unset]):
        status (Union[None, RecurrentRequestStatusEnum, Unset]):
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RecurrentRequestsPublic]
     """


    return sync_detailed(
        client=client,
service_id=service_id,
enrollment_id=enrollment_id,
status=status,
skip=skip,
limit=limit,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    service_id: Union[None, UUID, Unset] = UNSET,
    enrollment_id: Union[None, UUID, Unset] = UNSET,
    status: Union[None, RecurrentRequestStatusEnum, Unset] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[HTTPValidationError, RecurrentRequestsPublic]]:
    """ List Recurrent Requests

     List recurrent requests for the current customer.

    Args:
        service_id (Union[None, UUID, Unset]):
        enrollment_id (Union[None, UUID, Unset]):
        status (Union[None, RecurrentRequestStatusEnum, Unset]):
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RecurrentRequestsPublic]]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
enrollment_id=enrollment_id,
status=status,
skip=skip,
limit=limit,
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
    service_id: Union[None, UUID, Unset] = UNSET,
    enrollment_id: Union[None, UUID, Unset] = UNSET,
    status: Union[None, RecurrentRequestStatusEnum, Unset] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[HTTPValidationError, RecurrentRequestsPublic]]:
    """ List Recurrent Requests

     List recurrent requests for the current customer.

    Args:
        service_id (Union[None, UUID, Unset]):
        enrollment_id (Union[None, UUID, Unset]):
        status (Union[None, RecurrentRequestStatusEnum, Unset]):
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RecurrentRequestsPublic]
     """


    return (await asyncio_detailed(
        client=client,
service_id=service_id,
enrollment_id=enrollment_id,
status=status,
skip=skip,
limit=limit,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
