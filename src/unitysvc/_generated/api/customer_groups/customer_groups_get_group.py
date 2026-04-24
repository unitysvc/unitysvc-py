from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_service_group_detail import CustomerServiceGroupDetail
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    group_id: UUID,
    *,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/groups/{group_id}".format(
            group_id=quote(str(group_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerServiceGroupDetail | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CustomerServiceGroupDetail.from_dict(response.json())

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
) -> Response[CustomerServiceGroupDetail | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerServiceGroupDetail | HTTPValidationError]:
    """Get Group

     Get metadata for a single visible group.

    Returns 404 for hidden groups (draft, seller-owned, empty) —
    existence is not leaked. Member services are fetched separately
    via ``GET /customer/groups/{id}/services``.

    Args:
        group_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerServiceGroupDetail | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerServiceGroupDetail | HTTPValidationError | None:
    """Get Group

     Get metadata for a single visible group.

    Returns 404 for hidden groups (draft, seller-owned, empty) —
    existence is not leaked. Member services are fetched separately
    via ``GET /customer/groups/{id}/services``.

    Args:
        group_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerServiceGroupDetail | HTTPValidationError
    """

    return sync_detailed(
        group_id=group_id,
        client=client,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerServiceGroupDetail | HTTPValidationError]:
    """Get Group

     Get metadata for a single visible group.

    Returns 404 for hidden groups (draft, seller-owned, empty) —
    existence is not leaked. Member services are fetched separately
    via ``GET /customer/groups/{id}/services``.

    Args:
        group_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerServiceGroupDetail | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerServiceGroupDetail | HTTPValidationError | None:
    """Get Group

     Get metadata for a single visible group.

    Returns 404 for hidden groups (draft, seller-owned, empty) —
    existence is not leaked. Member services are fetched separately
    via ``GET /customer/groups/{id}/services``.

    Args:
        group_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerServiceGroupDetail | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            group_id=group_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
