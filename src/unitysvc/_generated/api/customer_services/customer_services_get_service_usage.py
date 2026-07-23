from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.access_plan import AccessPlan
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
        "url": "/services/{service_id}/usage".format(
            service_id=quote(str(service_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccessPlan | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AccessPlan.from_dict(response.json())

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
) -> Response[AccessPlan | HTTPValidationError]:
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
) -> Response[AccessPlan | HTTPValidationError]:
    r"""Get Service Usage

     Return the generic, structured \"how to use this service\" access plan (#1638).

    Readable without an API key, for the same visible set as the rest of this
    surface (active + public). It composes existing metadata: the per-channel
    facts from ``derive_channels`` (type, secrets), the listing's pricing and
    ``parameters_schema``, the secret acquisition guidance from #1618, and the
    ``user_access_interfaces`` templates (which decide ``enrollment_mode``). It
    owns no new data — see ``app.core.service_usage``.

    **Generic and context-free by design (#1638).** The plan describes how
    *anyone* signs up for and calls the service; it is identical for every
    caller, so it is ``public``-cacheable. Per-customer state (\"you already set
    this / you're enrolled\") is deliberately not here — each consumer renders the
    plan and joins its own customer context (the frontend hydrates secret status
    and live enrollment codes; the MCP server renders text). The backend renders
    nothing.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccessPlan | HTTPValidationError]
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
) -> AccessPlan | HTTPValidationError | None:
    r"""Get Service Usage

     Return the generic, structured \"how to use this service\" access plan (#1638).

    Readable without an API key, for the same visible set as the rest of this
    surface (active + public). It composes existing metadata: the per-channel
    facts from ``derive_channels`` (type, secrets), the listing's pricing and
    ``parameters_schema``, the secret acquisition guidance from #1618, and the
    ``user_access_interfaces`` templates (which decide ``enrollment_mode``). It
    owns no new data — see ``app.core.service_usage``.

    **Generic and context-free by design (#1638).** The plan describes how
    *anyone* signs up for and calls the service; it is identical for every
    caller, so it is ``public``-cacheable. Per-customer state (\"you already set
    this / you're enrolled\") is deliberately not here — each consumer renders the
    plan and joins its own customer context (the frontend hydrates secret status
    and live enrollment codes; the MCP server renders text). The backend renders
    nothing.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccessPlan | HTTPValidationError
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
) -> Response[AccessPlan | HTTPValidationError]:
    r"""Get Service Usage

     Return the generic, structured \"how to use this service\" access plan (#1638).

    Readable without an API key, for the same visible set as the rest of this
    surface (active + public). It composes existing metadata: the per-channel
    facts from ``derive_channels`` (type, secrets), the listing's pricing and
    ``parameters_schema``, the secret acquisition guidance from #1618, and the
    ``user_access_interfaces`` templates (which decide ``enrollment_mode``). It
    owns no new data — see ``app.core.service_usage``.

    **Generic and context-free by design (#1638).** The plan describes how
    *anyone* signs up for and calls the service; it is identical for every
    caller, so it is ``public``-cacheable. Per-customer state (\"you already set
    this / you're enrolled\") is deliberately not here — each consumer renders the
    plan and joins its own customer context (the frontend hydrates secret status
    and live enrollment codes; the MCP server renders text). The backend renders
    nothing.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccessPlan | HTTPValidationError]
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
) -> AccessPlan | HTTPValidationError | None:
    r"""Get Service Usage

     Return the generic, structured \"how to use this service\" access plan (#1638).

    Readable without an API key, for the same visible set as the rest of this
    surface (active + public). It composes existing metadata: the per-channel
    facts from ``derive_channels`` (type, secrets), the listing's pricing and
    ``parameters_schema``, the secret acquisition guidance from #1618, and the
    ``user_access_interfaces`` templates (which decide ``enrollment_mode``). It
    owns no new data — see ``app.core.service_usage``.

    **Generic and context-free by design (#1638).** The plan describes how
    *anyone* signs up for and calls the service; it is identical for every
    caller, so it is ``public``-cacheable. Per-customer state (\"you already set
    this / you're enrolled\") is deliberately not here — each consumer renders the
    plan and joins its own customer context (the frontend hydrates secret status
    and live enrollment codes; the MCP server renders text). The backend renders
    nothing.

    Args:
        service_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccessPlan | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
