from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_group_detail import CustomerGroupDetail
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    name: str,
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
        "url": "/groups/{name}".format(
            name=quote(str(name), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerGroupDetail | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CustomerGroupDetail.from_dict(response.json())

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
) -> Response[CustomerGroupDetail | HTTPValidationError]:
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerGroupDetail | HTTPValidationError]:
    r"""Get Group

     Get a single group from the unified surface, by name or UUID.

    Both kinds resolve to one unified ``CustomerGroupDetail`` shape:

    1. If ``name`` parses as a UUID that maps to one of the customer's
       own collections, return the collection
       (``owner_type=\"customer\"``, ``editable=True``, ``enabled`` set,
       ``group_type=\"collection\"``; interface / routing_policy null).
    2. Otherwise resolve a visible platform group by ``id`` or ``name``
       and return it (``owner_type=\"platform\"``, ``editable=False``,
       with embedded interface / routing policy; ``enabled`` null).
       Both ``id`` and ``name`` are returned in the shape, so platform
       groups are addressable by either; ``name`` is the stable handle
       that survives admin recreations.

    Collections are UUID-keyed (their slug is reserved for the future
    ``/g/<name>`` dispatch path). Returns 404 for anything outside the
    customer-visible set — existence is not leaked.

    Args:
        name (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerGroupDetail | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerGroupDetail | HTTPValidationError | None:
    r"""Get Group

     Get a single group from the unified surface, by name or UUID.

    Both kinds resolve to one unified ``CustomerGroupDetail`` shape:

    1. If ``name`` parses as a UUID that maps to one of the customer's
       own collections, return the collection
       (``owner_type=\"customer\"``, ``editable=True``, ``enabled`` set,
       ``group_type=\"collection\"``; interface / routing_policy null).
    2. Otherwise resolve a visible platform group by ``id`` or ``name``
       and return it (``owner_type=\"platform\"``, ``editable=False``,
       with embedded interface / routing policy; ``enabled`` null).
       Both ``id`` and ``name`` are returned in the shape, so platform
       groups are addressable by either; ``name`` is the stable handle
       that survives admin recreations.

    Collections are UUID-keyed (their slug is reserved for the future
    ``/g/<name>`` dispatch path). Returns 404 for anything outside the
    customer-visible set — existence is not leaked.

    Args:
        name (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerGroupDetail | HTTPValidationError
    """

    return sync_detailed(
        name=name,
        client=client,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CustomerGroupDetail | HTTPValidationError]:
    r"""Get Group

     Get a single group from the unified surface, by name or UUID.

    Both kinds resolve to one unified ``CustomerGroupDetail`` shape:

    1. If ``name`` parses as a UUID that maps to one of the customer's
       own collections, return the collection
       (``owner_type=\"customer\"``, ``editable=True``, ``enabled`` set,
       ``group_type=\"collection\"``; interface / routing_policy null).
    2. Otherwise resolve a visible platform group by ``id`` or ``name``
       and return it (``owner_type=\"platform\"``, ``editable=False``,
       with embedded interface / routing policy; ``enabled`` null).
       Both ``id`` and ``name`` are returned in the shape, so platform
       groups are addressable by either; ``name`` is the stable handle
       that survives admin recreations.

    Collections are UUID-keyed (their slug is reserved for the future
    ``/g/<name>`` dispatch path). Returns 404 for anything outside the
    customer-visible set — existence is not leaked.

    Args:
        name (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerGroupDetail | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CustomerGroupDetail | HTTPValidationError | None:
    r"""Get Group

     Get a single group from the unified surface, by name or UUID.

    Both kinds resolve to one unified ``CustomerGroupDetail`` shape:

    1. If ``name`` parses as a UUID that maps to one of the customer's
       own collections, return the collection
       (``owner_type=\"customer\"``, ``editable=True``, ``enabled`` set,
       ``group_type=\"collection\"``; interface / routing_policy null).
    2. Otherwise resolve a visible platform group by ``id`` or ``name``
       and return it (``owner_type=\"platform\"``, ``editable=False``,
       with embedded interface / routing policy; ``enabled`` null).
       Both ``id`` and ``name`` are returned in the shape, so platform
       groups are addressable by either; ``name`` is the stable handle
       that survives admin recreations.

    Collections are UUID-keyed (their slug is reserved for the future
    ``/g/<name>`` dispatch path). Returns 404 for anything outside the
    customer-visible set — existence is not leaked.

    Args:
        name (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerGroupDetail | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
