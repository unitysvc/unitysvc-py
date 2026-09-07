from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.preference_set_request import PreferenceSetRequest
from ...models.user_public import UserPublic
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: PreferenceSetRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/preferences/set",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | UserPublic | None:
    if response.status_code == 200:
        response_200 = UserPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | UserPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PreferenceSetRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | UserPublic]:
    """Set Preference

     Set (or clear, with ``value: null``) one named preference.

    Same write path the JWT-authenticated frontend endpoints use for each
    preference — this is a second door onto them, reachable with a
    ``svcpass_...`` API key, not a parallel implementation.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (PreferenceSetRequest): One preference write. ``value: None`` clears it.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UserPublic]
    """

    kwargs = _get_kwargs(
        body=body,
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
    body: PreferenceSetRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | UserPublic | None:
    """Set Preference

     Set (or clear, with ``value: null``) one named preference.

    Same write path the JWT-authenticated frontend endpoints use for each
    preference — this is a second door onto them, reachable with a
    ``svcpass_...`` API key, not a parallel implementation.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (PreferenceSetRequest): One preference write. ``value: None`` clears it.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UserPublic
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PreferenceSetRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | UserPublic]:
    """Set Preference

     Set (or clear, with ``value: null``) one named preference.

    Same write path the JWT-authenticated frontend endpoints use for each
    preference — this is a second door onto them, reachable with a
    ``svcpass_...`` API key, not a parallel implementation.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (PreferenceSetRequest): One preference write. ``value: None`` clears it.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UserPublic]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PreferenceSetRequest,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | UserPublic | None:
    """Set Preference

     Set (or clear, with ``value: null``) one named preference.

    Same write path the JWT-authenticated frontend endpoints use for each
    preference — this is a second door onto them, reachable with a
    ``svcpass_...`` API key, not a parallel implementation.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (PreferenceSetRequest): One preference write. ``value: None`` clears it.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UserPublic
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
