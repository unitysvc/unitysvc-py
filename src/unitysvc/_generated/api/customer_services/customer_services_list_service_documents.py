from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_category_enum import DocumentCategoryEnum, check_document_category_enum
from ...models.http_validation_error import HTTPValidationError
from ...models.service_documents_response import ServiceDocumentsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_id: UUID,
    *,
    category: DocumentCategoryEnum | None | Unset = UNSET,
    mime_type: None | str | Unset = UNSET,
    include_content: bool | Unset = False,
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

    json_category: None | str | Unset
    if isinstance(category, Unset):
        json_category = UNSET
    elif isinstance(category, str):
        json_category = category
    else:
        json_category = category
    params["category"] = json_category

    json_mime_type: None | str | Unset
    if isinstance(mime_type, Unset):
        json_mime_type = UNSET
    else:
        json_mime_type = mime_type
    params["mime_type"] = json_mime_type

    params["include_content"] = include_content

    json_interface: None | str | Unset
    if isinstance(interface, Unset):
        json_interface = UNSET
    else:
        json_interface = interface
    params["interface"] = json_interface

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/services/{service_id}/documents".format(
            service_id=quote(str(service_id), safe=""),
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
    *,
    client: AuthenticatedClient | Client,
    category: DocumentCategoryEnum | None | Unset = UNSET,
    mime_type: None | str | Unset = UNSET,
    include_content: bool | Unset = False,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceDocumentsResponse]:
    r"""List Service Documents

     List the seller-authored documents for a service.

    Readable without an API key (unitysvc#1616), for the same visible set as
    the rest of this surface: the service must be active and public. Only
    documents explicitly marked ``is_public`` are returned — that flag defaults
    to false, so a seller's internal notes stay internal without extra work.

    This is how a caller answers \"how do I use this service\". With
    ``include_content=true`` the whole answer arrives in one request — an agent
    wanting a tutorial *and* a Python example should not need three round
    trips, and filters keep the payload to what was actually asked for:

        ?category=code_example&mime_type=python&include_content=true
        ?category=getting_started&include_content=true

    Content is off by default because rendering costs a Jinja pass and a
    context load per document, and every language's example at once is a lot
    of an agent's context to spend without being asked.

    Args:
        service_id (UUID):
        category (DocumentCategoryEnum | None | Unset): Filter by category, e.g. code_example,
            getting_started, tutorial.
        mime_type (None | str | Unset): Filter by mime type, which is the language for code
            examples: python, javascript, bash.
        include_content (bool | Unset): Return each document's content inline, rendered where
            applicable. Combine with the filters to fetch exactly what you need in one call. Default:
            False.
        interface (None | str | Unset): Render examples against this interface, named by its key
            (e.g. canonical, latest). Omit to use the service's default interface; the other keys come
            back in available_interfaces.
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
        category=category,
        mime_type=mime_type,
        include_content=include_content,
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
    *,
    client: AuthenticatedClient | Client,
    category: DocumentCategoryEnum | None | Unset = UNSET,
    mime_type: None | str | Unset = UNSET,
    include_content: bool | Unset = False,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceDocumentsResponse | None:
    r"""List Service Documents

     List the seller-authored documents for a service.

    Readable without an API key (unitysvc#1616), for the same visible set as
    the rest of this surface: the service must be active and public. Only
    documents explicitly marked ``is_public`` are returned — that flag defaults
    to false, so a seller's internal notes stay internal without extra work.

    This is how a caller answers \"how do I use this service\". With
    ``include_content=true`` the whole answer arrives in one request — an agent
    wanting a tutorial *and* a Python example should not need three round
    trips, and filters keep the payload to what was actually asked for:

        ?category=code_example&mime_type=python&include_content=true
        ?category=getting_started&include_content=true

    Content is off by default because rendering costs a Jinja pass and a
    context load per document, and every language's example at once is a lot
    of an agent's context to spend without being asked.

    Args:
        service_id (UUID):
        category (DocumentCategoryEnum | None | Unset): Filter by category, e.g. code_example,
            getting_started, tutorial.
        mime_type (None | str | Unset): Filter by mime type, which is the language for code
            examples: python, javascript, bash.
        include_content (bool | Unset): Return each document's content inline, rendered where
            applicable. Combine with the filters to fetch exactly what you need in one call. Default:
            False.
        interface (None | str | Unset): Render examples against this interface, named by its key
            (e.g. canonical, latest). Omit to use the service's default interface; the other keys come
            back in available_interfaces.
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
        client=client,
        category=category,
        mime_type=mime_type,
        include_content=include_content,
        interface=interface,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    category: DocumentCategoryEnum | None | Unset = UNSET,
    mime_type: None | str | Unset = UNSET,
    include_content: bool | Unset = False,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceDocumentsResponse]:
    r"""List Service Documents

     List the seller-authored documents for a service.

    Readable without an API key (unitysvc#1616), for the same visible set as
    the rest of this surface: the service must be active and public. Only
    documents explicitly marked ``is_public`` are returned — that flag defaults
    to false, so a seller's internal notes stay internal without extra work.

    This is how a caller answers \"how do I use this service\". With
    ``include_content=true`` the whole answer arrives in one request — an agent
    wanting a tutorial *and* a Python example should not need three round
    trips, and filters keep the payload to what was actually asked for:

        ?category=code_example&mime_type=python&include_content=true
        ?category=getting_started&include_content=true

    Content is off by default because rendering costs a Jinja pass and a
    context load per document, and every language's example at once is a lot
    of an agent's context to spend without being asked.

    Args:
        service_id (UUID):
        category (DocumentCategoryEnum | None | Unset): Filter by category, e.g. code_example,
            getting_started, tutorial.
        mime_type (None | str | Unset): Filter by mime type, which is the language for code
            examples: python, javascript, bash.
        include_content (bool | Unset): Return each document's content inline, rendered where
            applicable. Combine with the filters to fetch exactly what you need in one call. Default:
            False.
        interface (None | str | Unset): Render examples against this interface, named by its key
            (e.g. canonical, latest). Omit to use the service's default interface; the other keys come
            back in available_interfaces.
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
        category=category,
        mime_type=mime_type,
        include_content=include_content,
        interface=interface,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    category: DocumentCategoryEnum | None | Unset = UNSET,
    mime_type: None | str | Unset = UNSET,
    include_content: bool | Unset = False,
    interface: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceDocumentsResponse | None:
    r"""List Service Documents

     List the seller-authored documents for a service.

    Readable without an API key (unitysvc#1616), for the same visible set as
    the rest of this surface: the service must be active and public. Only
    documents explicitly marked ``is_public`` are returned — that flag defaults
    to false, so a seller's internal notes stay internal without extra work.

    This is how a caller answers \"how do I use this service\". With
    ``include_content=true`` the whole answer arrives in one request — an agent
    wanting a tutorial *and* a Python example should not need three round
    trips, and filters keep the payload to what was actually asked for:

        ?category=code_example&mime_type=python&include_content=true
        ?category=getting_started&include_content=true

    Content is off by default because rendering costs a Jinja pass and a
    context load per document, and every language's example at once is a lot
    of an agent's context to spend without being asked.

    Args:
        service_id (UUID):
        category (DocumentCategoryEnum | None | Unset): Filter by category, e.g. code_example,
            getting_started, tutorial.
        mime_type (None | str | Unset): Filter by mime type, which is the language for code
            examples: python, javascript, bash.
        include_content (bool | Unset): Return each document's content inline, rendered where
            applicable. Combine with the filters to fetch exactly what you need in one call. Default:
            False.
        interface (None | str | Unset): Render examples against this interface, named by its key
            (e.g. canonical, latest). Omit to use the service's default interface; the other keys come
            back in available_interfaces.
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
            client=client,
            category=category,
            mime_type=mime_type,
            include_content=include_content,
            interface=interface,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
