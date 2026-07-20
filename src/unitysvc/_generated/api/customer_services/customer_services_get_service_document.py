from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.service_documents_response import ServiceDocumentsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_id: UUID,
    document_id: UUID,
    *,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_interface: None | str | Unset
    if isinstance(interface, Unset):
        json_interface = UNSET
    else:
        json_interface = interface
    params["interface"] = json_interface

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/services/{service_id}/documents/{document_id}".format(
            service_id=quote(str(service_id), safe=""),
            document_id=quote(str(document_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ServiceDocumentsResponse | None:
    if response.status_code == 200:
        response_200 = ServiceDocumentsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ServiceDocumentsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    service_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceDocumentsResponse]:
    """Get Service Document

     Fetch one public document for a service, with its content.

    ``content`` is returned for text-ish documents; URL-backed and binary
    documents return None and the caller follows ``external_url``.

    Code examples and connectivity tests are **rendered before returning**,
    against one user access interface — so the caller gets a runnable snippet
    with the real gateway base URL rather than a Jinja template. Pass
    ``interface`` to pick a specific key; without it the service's default is
    used, and ``available_interfaces`` lists the alternatives so the caller
    can re-request another.

    Returns the same envelope as the listing endpoint, with the single
    requested document, so both share one response shape.

    Rendering reuses ``render_document_for_test`` — the same code path behind
    the frontend's rendered examples — so the two cannot drift.

    Args:
        service_id (UUID):
        document_id (UUID):
        interface (None | str | Unset): Render against this interface, named by its key (e.g.
            canonical, latest). Omit to use the service's default interface; the other keys come back
            in available_interfaces.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceDocumentsResponse]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        document_id=document_id,
        interface=interface,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    service_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceDocumentsResponse | None:
    """Get Service Document

     Fetch one public document for a service, with its content.

    ``content`` is returned for text-ish documents; URL-backed and binary
    documents return None and the caller follows ``external_url``.

    Code examples and connectivity tests are **rendered before returning**,
    against one user access interface — so the caller gets a runnable snippet
    with the real gateway base URL rather than a Jinja template. Pass
    ``interface`` to pick a specific key; without it the service's default is
    used, and ``available_interfaces`` lists the alternatives so the caller
    can re-request another.

    Returns the same envelope as the listing endpoint, with the single
    requested document, so both share one response shape.

    Rendering reuses ``render_document_for_test`` — the same code path behind
    the frontend's rendered examples — so the two cannot drift.

    Args:
        service_id (UUID):
        document_id (UUID):
        interface (None | str | Unset): Render against this interface, named by its key (e.g.
            canonical, latest). Omit to use the service's default interface; the other keys come back
            in available_interfaces.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceDocumentsResponse
    """

    return sync_detailed(
        service_id=service_id,
        document_id=document_id,
        client=client,
        interface=interface,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    service_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceDocumentsResponse]:
    """Get Service Document

     Fetch one public document for a service, with its content.

    ``content`` is returned for text-ish documents; URL-backed and binary
    documents return None and the caller follows ``external_url``.

    Code examples and connectivity tests are **rendered before returning**,
    against one user access interface — so the caller gets a runnable snippet
    with the real gateway base URL rather than a Jinja template. Pass
    ``interface`` to pick a specific key; without it the service's default is
    used, and ``available_interfaces`` lists the alternatives so the caller
    can re-request another.

    Returns the same envelope as the listing endpoint, with the single
    requested document, so both share one response shape.

    Rendering reuses ``render_document_for_test`` — the same code path behind
    the frontend's rendered examples — so the two cannot drift.

    Args:
        service_id (UUID):
        document_id (UUID):
        interface (None | str | Unset): Render against this interface, named by its key (e.g.
            canonical, latest). Omit to use the service's default interface; the other keys come back
            in available_interfaces.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceDocumentsResponse]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        document_id=document_id,
        interface=interface,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceDocumentsResponse | None:
    """Get Service Document

     Fetch one public document for a service, with its content.

    ``content`` is returned for text-ish documents; URL-backed and binary
    documents return None and the caller follows ``external_url``.

    Code examples and connectivity tests are **rendered before returning**,
    against one user access interface — so the caller gets a runnable snippet
    with the real gateway base URL rather than a Jinja template. Pass
    ``interface`` to pick a specific key; without it the service's default is
    used, and ``available_interfaces`` lists the alternatives so the caller
    can re-request another.

    Returns the same envelope as the listing endpoint, with the single
    requested document, so both share one response shape.

    Rendering reuses ``render_document_for_test`` — the same code path behind
    the frontend's rendered examples — so the two cannot drift.

    Args:
        service_id (UUID):
        document_id (UUID):
        interface (None | str | Unset): Render against this interface, named by its key (e.g.
            canonical, latest). Omit to use the service's default interface; the other keys come back
            in available_interfaces.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceDocumentsResponse
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            document_id=document_id,
            client=client,
            interface=interface,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
