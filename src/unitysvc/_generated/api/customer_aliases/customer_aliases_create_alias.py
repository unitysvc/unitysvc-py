from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.service_alias_create import ServiceAliasCreate
from ...models.service_alias_public import ServiceAliasPublic
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ServiceAliasCreate,
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
        "url": "/aliases/",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ServiceAliasPublic | None:
    if response.status_code == 201:
        response_201 = ServiceAliasPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | ServiceAliasPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceAliasCreate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceAliasPublic]:
    """Create Alias

     Create a new URL alias for the current customer.

    If ``is_routing`` is True (the default) and another alias is already
    routing the same (name, request_routing_key), this one is created as
    non-routing instead. Users can later switch routing via the
    ``/aliases/{id}/switch`` endpoint.

    Combined routing-object cap (#1071 / #1083 / #1136): when the
    customer's active plan declares ``terms.routing_objects.max_allowed``,
    creating past that cap — counting ALL the customer's routing objects
    (aliases + collections) — returns 422 with an upgrade-prompt body.
    When ``max_allowed`` is ``None`` (unlimited), creation is always
    allowed. Routing objects are free; there is no per-object billing.
    Seat-scaling for Team subscriptions is applied by
    ``enforce_quota_for_customer``. Unsubscribed customers have no quota.

    Args:
        shared (bool | Unset): When true, create a shared team alias visible/editable by all org
            members. When false (default), create a personal alias owned by this user. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceAliasCreate): Schema for creating a ServiceAlias.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceAliasPublic]
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
    body: ServiceAliasCreate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceAliasPublic | None:
    """Create Alias

     Create a new URL alias for the current customer.

    If ``is_routing`` is True (the default) and another alias is already
    routing the same (name, request_routing_key), this one is created as
    non-routing instead. Users can later switch routing via the
    ``/aliases/{id}/switch`` endpoint.

    Combined routing-object cap (#1071 / #1083 / #1136): when the
    customer's active plan declares ``terms.routing_objects.max_allowed``,
    creating past that cap — counting ALL the customer's routing objects
    (aliases + collections) — returns 422 with an upgrade-prompt body.
    When ``max_allowed`` is ``None`` (unlimited), creation is always
    allowed. Routing objects are free; there is no per-object billing.
    Seat-scaling for Team subscriptions is applied by
    ``enforce_quota_for_customer``. Unsubscribed customers have no quota.

    Args:
        shared (bool | Unset): When true, create a shared team alias visible/editable by all org
            members. When false (default), create a personal alias owned by this user. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceAliasCreate): Schema for creating a ServiceAlias.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceAliasPublic
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
    body: ServiceAliasCreate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceAliasPublic]:
    """Create Alias

     Create a new URL alias for the current customer.

    If ``is_routing`` is True (the default) and another alias is already
    routing the same (name, request_routing_key), this one is created as
    non-routing instead. Users can later switch routing via the
    ``/aliases/{id}/switch`` endpoint.

    Combined routing-object cap (#1071 / #1083 / #1136): when the
    customer's active plan declares ``terms.routing_objects.max_allowed``,
    creating past that cap — counting ALL the customer's routing objects
    (aliases + collections) — returns 422 with an upgrade-prompt body.
    When ``max_allowed`` is ``None`` (unlimited), creation is always
    allowed. Routing objects are free; there is no per-object billing.
    Seat-scaling for Team subscriptions is applied by
    ``enforce_quota_for_customer``. Unsubscribed customers have no quota.

    Args:
        shared (bool | Unset): When true, create a shared team alias visible/editable by all org
            members. When false (default), create a personal alias owned by this user. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceAliasCreate): Schema for creating a ServiceAlias.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceAliasPublic]
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
    body: ServiceAliasCreate,
    shared: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceAliasPublic | None:
    """Create Alias

     Create a new URL alias for the current customer.

    If ``is_routing`` is True (the default) and another alias is already
    routing the same (name, request_routing_key), this one is created as
    non-routing instead. Users can later switch routing via the
    ``/aliases/{id}/switch`` endpoint.

    Combined routing-object cap (#1071 / #1083 / #1136): when the
    customer's active plan declares ``terms.routing_objects.max_allowed``,
    creating past that cap — counting ALL the customer's routing objects
    (aliases + collections) — returns 422 with an upgrade-prompt body.
    When ``max_allowed`` is ``None`` (unlimited), creation is always
    allowed. Routing objects are free; there is no per-object billing.
    Seat-scaling for Team subscriptions is applied by
    ``enforce_quota_for_customer``. Unsubscribed customers have no quota.

    Args:
        shared (bool | Unset): When true, create a shared team alias visible/editable by all org
            members. When false (default), create a personal alias owned by this user. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceAliasCreate): Schema for creating a ServiceAlias.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceAliasPublic
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
