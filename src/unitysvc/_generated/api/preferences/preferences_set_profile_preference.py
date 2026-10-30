from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.profile_edit_public import ProfileEditPublic
from ...models.profile_update import ProfileUpdate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ProfileUpdate,
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
        "url": "/preferences/profile",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ProfileEditPublic | None:
    if response.status_code == 200:
        response_200 = ProfileEditPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | ProfileEditPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ProfileUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ProfileEditPublic]:
    """Set Profile Preference

     Replace the current account's profile: section values and their
    ``public`` flags together. 409 when ``version`` is stale, so a save from an
    old copy cannot republish a section made private since.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ProfileUpdate): The whole profile. ``version`` is the one you read (``0`` before the
            first save); a section without ``public`` is private.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ProfileEditPublic]
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
    body: ProfileUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ProfileEditPublic | None:
    """Set Profile Preference

     Replace the current account's profile: section values and their
    ``public`` flags together. 409 when ``version`` is stale, so a save from an
    old copy cannot republish a section made private since.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ProfileUpdate): The whole profile. ``version`` is the one you read (``0`` before the
            first save); a section without ``public`` is private.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ProfileEditPublic
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
    body: ProfileUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ProfileEditPublic]:
    """Set Profile Preference

     Replace the current account's profile: section values and their
    ``public`` flags together. 409 when ``version`` is stale, so a save from an
    old copy cannot republish a section made private since.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ProfileUpdate): The whole profile. ``version`` is the one you read (``0`` before the
            first save); a section without ``public`` is private.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ProfileEditPublic]
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
    body: ProfileUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ProfileEditPublic | None:
    """Set Profile Preference

     Replace the current account's profile: section values and their
    ``public`` flags together. 409 when ``version`` is stale, so a save from an
    old copy cannot republish a section made private since.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ProfileUpdate): The whole profile. ``version`` is the one you read (``0`` before the
            first save); a section without ``public`` is private.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ProfileEditPublic
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
