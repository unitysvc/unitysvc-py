from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_group_view import CustomerGroupView
from ...models.http_validation_error import HTTPValidationError
from ...models.service_collection_create import ServiceCollectionCreate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ServiceCollectionCreate,
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
        "method": "post",
        "url": "/groups",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerGroupView | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = CustomerGroupView.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CustomerGroupView | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceCollectionCreate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerGroupView | HTTPValidationError]:
    """Create Customer Group

     Create a customer-owned service collection.

    Collections are the editable half of the unified ``/customer/groups``
    surface: customer-curated catalogs addressable at ``/g/<name>``.
    Platform groups remain read-only here. The ``name`` slug is unique
    per owner scope; a duplicate in the same scope returns 409. A personal
    collection may coexist with a same-named shared one (#1471).

    Args:
        shared (bool | Unset): When true, create a shared team collection visible/editable by all
            org members. When false (default), create a personal collection owned by this user.
            Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceCollectionCreate): Schema for creating a ServiceCollection.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerGroupView | HTTPValidationError]
    """

    kwargs = _get_kwargs(
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
    *,
    client: AuthenticatedClient | Client,
    body: ServiceCollectionCreate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerGroupView | HTTPValidationError | None:
    """Create Customer Group

     Create a customer-owned service collection.

    Collections are the editable half of the unified ``/customer/groups``
    surface: customer-curated catalogs addressable at ``/g/<name>``.
    Platform groups remain read-only here. The ``name`` slug is unique
    per owner scope; a duplicate in the same scope returns 409. A personal
    collection may coexist with a same-named shared one (#1471).

    Args:
        shared (bool | Unset): When true, create a shared team collection visible/editable by all
            org members. When false (default), create a personal collection owned by this user.
            Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceCollectionCreate): Schema for creating a ServiceCollection.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerGroupView | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        shared=shared,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceCollectionCreate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerGroupView | HTTPValidationError]:
    """Create Customer Group

     Create a customer-owned service collection.

    Collections are the editable half of the unified ``/customer/groups``
    surface: customer-curated catalogs addressable at ``/g/<name>``.
    Platform groups remain read-only here. The ``name`` slug is unique
    per owner scope; a duplicate in the same scope returns 409. A personal
    collection may coexist with a same-named shared one (#1471).

    Args:
        shared (bool | Unset): When true, create a shared team collection visible/editable by all
            org members. When false (default), create a personal collection owned by this user.
            Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceCollectionCreate): Schema for creating a ServiceCollection.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerGroupView | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        shared=shared,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceCollectionCreate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerGroupView | HTTPValidationError | None:
    """Create Customer Group

     Create a customer-owned service collection.

    Collections are the editable half of the unified ``/customer/groups``
    surface: customer-curated catalogs addressable at ``/g/<name>``.
    Platform groups remain read-only here. The ``name`` slug is unique
    per owner scope; a duplicate in the same scope returns 409. A personal
    collection may coexist with a same-named shared one (#1471).

    Args:
        shared (bool | Unset): When true, create a shared team collection visible/editable by all
            org members. When false (default), create a personal collection owned by this user.
            Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceCollectionCreate): Schema for creating a ServiceCollection.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerGroupView | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            shared=shared,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
