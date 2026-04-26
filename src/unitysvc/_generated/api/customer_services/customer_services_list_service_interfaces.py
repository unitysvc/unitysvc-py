from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.access_interface import AccessInterface
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_id: UUID,
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
        "url": "/services/{service_id}/interfaces".format(
            service_id=quote(str(service_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[AccessInterface] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AccessInterface.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[AccessInterface]]:
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[AccessInterface]]:
    """List Service Interfaces

     List access interfaces dispatchable by the calling customer.

    Returns two kinds of interfaces, unified so the SDK can present
    them as a single ``service.interfaces()`` list:

    1. **Shared** interfaces (``enrollment_id IS NULL``) — usable by
       any customer, matches the public playground behaviour.
    2. **Enrollment-bound** interfaces whose ``enrollment_id`` belongs
       to an enrollment owned by the authenticated customer. BYOK /
       BYOE services create these on enrollment activation so the
       gateway can substitute customer-supplied secrets at runtime.

    Interfaces bound to *other* customers' enrollments are filtered
    out — existence is not leaked. ``base_url`` is resolved with
    ``settings.resolve_gateway_urls`` so SDK consumers can dispatch
    directly without knowing gateway substitution rules.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[AccessInterface]]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | list[AccessInterface] | None:
    """List Service Interfaces

     List access interfaces dispatchable by the calling customer.

    Returns two kinds of interfaces, unified so the SDK can present
    them as a single ``service.interfaces()`` list:

    1. **Shared** interfaces (``enrollment_id IS NULL``) — usable by
       any customer, matches the public playground behaviour.
    2. **Enrollment-bound** interfaces whose ``enrollment_id`` belongs
       to an enrollment owned by the authenticated customer. BYOK /
       BYOE services create these on enrollment activation so the
       gateway can substitute customer-supplied secrets at runtime.

    Interfaces bound to *other* customers' enrollments are filtered
    out — existence is not leaked. ``base_url`` is resolved with
    ``settings.resolve_gateway_urls`` so SDK consumers can dispatch
    directly without knowing gateway substitution rules.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[AccessInterface]
    """

    return sync_detailed(
        service_id=service_id,
        client=client,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[AccessInterface]]:
    """List Service Interfaces

     List access interfaces dispatchable by the calling customer.

    Returns two kinds of interfaces, unified so the SDK can present
    them as a single ``service.interfaces()`` list:

    1. **Shared** interfaces (``enrollment_id IS NULL``) — usable by
       any customer, matches the public playground behaviour.
    2. **Enrollment-bound** interfaces whose ``enrollment_id`` belongs
       to an enrollment owned by the authenticated customer. BYOK /
       BYOE services create these on enrollment activation so the
       gateway can substitute customer-supplied secrets at runtime.

    Interfaces bound to *other* customers' enrollments are filtered
    out — existence is not leaked. ``base_url`` is resolved with
    ``settings.resolve_gateway_urls`` so SDK consumers can dispatch
    directly without knowing gateway substitution rules.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[AccessInterface]]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | list[AccessInterface] | None:
    """List Service Interfaces

     List access interfaces dispatchable by the calling customer.

    Returns two kinds of interfaces, unified so the SDK can present
    them as a single ``service.interfaces()`` list:

    1. **Shared** interfaces (``enrollment_id IS NULL``) — usable by
       any customer, matches the public playground behaviour.
    2. **Enrollment-bound** interfaces whose ``enrollment_id`` belongs
       to an enrollment owned by the authenticated customer. BYOK /
       BYOE services create these on enrollment activation so the
       gateway can substitute customer-supplied secrets at runtime.

    Interfaces bound to *other* customers' enrollments are filtered
    out — existence is not leaked. ``base_url`` is resolved with
    ``settings.resolve_gateway_urls`` so SDK consumers can dispatch
    directly without knowing gateway substitution rules.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[AccessInterface]
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
