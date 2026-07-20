from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.service_usage_response import ServiceUsageResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_id: UUID,
    *,
    links: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["links"] = links

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/services/{service_id}/usage".format(
            service_id=quote(str(service_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ServiceUsageResponse | None:
    if response.status_code == 200:
        response_200 = ServiceUsageResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ServiceUsageResponse]:
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
    links: bool | Unset = False,
) -> Response[HTTPValidationError | ServiceUsageResponse]:
    r"""Get Service Usage

     Return a derived, markdown \"how to use this service\" guide.

    Readable without an API key, for the same visible set as the rest of this
    surface (active + public). It composes existing metadata: the per-channel
    facts from ``derive_channels`` (type, secrets), the listing's pricing and
    ``parameters_schema``, the secret acquisition guidance surfaced on the
    interfaces response (#1618), and the default user interface (#1617). It
    owns no new data — see ``app.core.service_usage``.

    **Generic and anonymous by design (#1622).** The guide describes how
    *anyone* signs up for and calls the service, per channel; it is identical
    for every caller, so it is ``public``-cacheable (the hosted MCP and the CDN
    cache it). Per-customer state (\"you already set this / you're enrolled\") is
    deliberately not here — a consumer applies it from the customer context it
    already holds (e.g. the frontend hydrates the secret links from
    ``secretExistence``), rather than the endpoint doing a per-caller,
    per-service lookup.

    Args:
        service_id (UUID):
        links (bool | Unset): Emit markdown links for secrets (/secrets?name=…) and code examples
            — the browser flavor, where the frontend hydrates the secret links into live status pills.
            Default false renders plain text, which is what MCP / CLI consumers want. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceUsageResponse]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        links=links,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    links: bool | Unset = False,
) -> HTTPValidationError | ServiceUsageResponse | None:
    r"""Get Service Usage

     Return a derived, markdown \"how to use this service\" guide.

    Readable without an API key, for the same visible set as the rest of this
    surface (active + public). It composes existing metadata: the per-channel
    facts from ``derive_channels`` (type, secrets), the listing's pricing and
    ``parameters_schema``, the secret acquisition guidance surfaced on the
    interfaces response (#1618), and the default user interface (#1617). It
    owns no new data — see ``app.core.service_usage``.

    **Generic and anonymous by design (#1622).** The guide describes how
    *anyone* signs up for and calls the service, per channel; it is identical
    for every caller, so it is ``public``-cacheable (the hosted MCP and the CDN
    cache it). Per-customer state (\"you already set this / you're enrolled\") is
    deliberately not here — a consumer applies it from the customer context it
    already holds (e.g. the frontend hydrates the secret links from
    ``secretExistence``), rather than the endpoint doing a per-caller,
    per-service lookup.

    Args:
        service_id (UUID):
        links (bool | Unset): Emit markdown links for secrets (/secrets?name=…) and code examples
            — the browser flavor, where the frontend hydrates the secret links into live status pills.
            Default false renders plain text, which is what MCP / CLI consumers want. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceUsageResponse
    """

    return sync_detailed(
        service_id=service_id,
        client=client,
        links=links,
    ).parsed


async def asyncio_detailed(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    links: bool | Unset = False,
) -> Response[HTTPValidationError | ServiceUsageResponse]:
    r"""Get Service Usage

     Return a derived, markdown \"how to use this service\" guide.

    Readable without an API key, for the same visible set as the rest of this
    surface (active + public). It composes existing metadata: the per-channel
    facts from ``derive_channels`` (type, secrets), the listing's pricing and
    ``parameters_schema``, the secret acquisition guidance surfaced on the
    interfaces response (#1618), and the default user interface (#1617). It
    owns no new data — see ``app.core.service_usage``.

    **Generic and anonymous by design (#1622).** The guide describes how
    *anyone* signs up for and calls the service, per channel; it is identical
    for every caller, so it is ``public``-cacheable (the hosted MCP and the CDN
    cache it). Per-customer state (\"you already set this / you're enrolled\") is
    deliberately not here — a consumer applies it from the customer context it
    already holds (e.g. the frontend hydrates the secret links from
    ``secretExistence``), rather than the endpoint doing a per-caller,
    per-service lookup.

    Args:
        service_id (UUID):
        links (bool | Unset): Emit markdown links for secrets (/secrets?name=…) and code examples
            — the browser flavor, where the frontend hydrates the secret links into live status pills.
            Default false renders plain text, which is what MCP / CLI consumers want. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceUsageResponse]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        links=links,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    links: bool | Unset = False,
) -> HTTPValidationError | ServiceUsageResponse | None:
    r"""Get Service Usage

     Return a derived, markdown \"how to use this service\" guide.

    Readable without an API key, for the same visible set as the rest of this
    surface (active + public). It composes existing metadata: the per-channel
    facts from ``derive_channels`` (type, secrets), the listing's pricing and
    ``parameters_schema``, the secret acquisition guidance surfaced on the
    interfaces response (#1618), and the default user interface (#1617). It
    owns no new data — see ``app.core.service_usage``.

    **Generic and anonymous by design (#1622).** The guide describes how
    *anyone* signs up for and calls the service, per channel; it is identical
    for every caller, so it is ``public``-cacheable (the hosted MCP and the CDN
    cache it). Per-customer state (\"you already set this / you're enrolled\") is
    deliberately not here — a consumer applies it from the customer context it
    already holds (e.g. the frontend hydrates the secret links from
    ``secretExistence``), rather than the endpoint doing a per-caller,
    per-service lookup.

    Args:
        service_id (UUID):
        links (bool | Unset): Emit markdown links for secrets (/secrets?name=…) and code examples
            — the browser flavor, where the frontend hydrates the secret links into live status pills.
            Default false renders plain text, which is what MCP / CLI consumers want. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceUsageResponse
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
            links=links,
        )
    ).parsed
