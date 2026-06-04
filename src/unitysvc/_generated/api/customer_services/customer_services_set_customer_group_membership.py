from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_group_membership_response import CustomerGroupMembershipResponse
from ...models.customer_group_membership_update import CustomerGroupMembershipUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_id: UUID,
    *,
    body: CustomerGroupMembershipUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/services/{service_id}/groups".format(
            service_id=quote(str(service_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerGroupMembershipResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CustomerGroupMembershipResponse.from_dict(response.json())

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
) -> Response[CustomerGroupMembershipResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: CustomerGroupMembershipUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerGroupMembershipResponse | HTTPValidationError]:
    """Set Customer Group Membership

     Set which of the customer's editable collections contain the
    service (toggle/diff). ``include_default`` ensures the Favorites
    collection exists then adds; unchecking removes. Rejects services the
    customer can't dispatch and enforces the per-collection member cap.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (CustomerGroupMembershipUpdate): PUT body: the collections that should contain the
            service after
            save. ``group_ids`` are the customer's editable collections;
            ``include_default`` toggles the Favorites collection (created on
            first use).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerGroupMembershipResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: CustomerGroupMembershipUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerGroupMembershipResponse | HTTPValidationError | None:
    """Set Customer Group Membership

     Set which of the customer's editable collections contain the
    service (toggle/diff). ``include_default`` ensures the Favorites
    collection exists then adds; unchecking removes. Rejects services the
    customer can't dispatch and enforces the per-collection member cap.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (CustomerGroupMembershipUpdate): PUT body: the collections that should contain the
            service after
            save. ``group_ids`` are the customer's editable collections;
            ``include_default`` toggles the Favorites collection (created on
            first use).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerGroupMembershipResponse | HTTPValidationError
    """

    return sync_detailed(
        service_id=service_id,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: CustomerGroupMembershipUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerGroupMembershipResponse | HTTPValidationError]:
    """Set Customer Group Membership

     Set which of the customer's editable collections contain the
    service (toggle/diff). ``include_default`` ensures the Favorites
    collection exists then adds; unchecking removes. Rejects services the
    customer can't dispatch and enforces the per-collection member cap.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (CustomerGroupMembershipUpdate): PUT body: the collections that should contain the
            service after
            save. ``group_ids`` are the customer's editable collections;
            ``include_default`` toggles the Favorites collection (created on
            first use).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerGroupMembershipResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: CustomerGroupMembershipUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerGroupMembershipResponse | HTTPValidationError | None:
    """Set Customer Group Membership

     Set which of the customer's editable collections contain the
    service (toggle/diff). ``include_default`` ensures the Favorites
    collection exists then adds; unchecking removes. Rejects services the
    customer can't dispatch and enforces the per-collection member cap.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (CustomerGroupMembershipUpdate): PUT body: the collections that should contain the
            service after
            save. ``group_ids`` are the customer's editable collections;
            ``include_default`` toggles the Favorites collection (created on
            first use).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerGroupMembershipResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
