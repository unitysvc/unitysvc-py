from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.logging_status_response import LoggingStatusResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    truncate_long_message: bool | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_truncate_long_message: bool | None | Unset
    if isinstance(truncate_long_message, Unset):
        json_truncate_long_message = UNSET
    else:
        json_truncate_long_message = truncate_long_message
    params["truncate_long_message"] = json_truncate_long_message

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/request-logs/start",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | LoggingStatusResponse | None:
    if response.status_code == 200:
        response_200 = LoggingStatusResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | LoggingStatusResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    truncate_long_message: bool | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | LoggingStatusResponse]:
    """Start request logging

     Enable request logging for the authenticated user.

    Args:
        truncate_long_message (bool | None | Unset): Picks the mode. ``True`` → ``truncated`` (8
            KB inline preview, no S3). ``False`` → ``complete`` (full body uploaded to S3 for
            retrieval via the detail endpoint). ``None`` (default) → preserve the user's existing
            ``preference.logging.enabled`` if it's already ``truncated`` or ``complete``; fall back to
            ``truncated`` otherwise.

            Two intended caller shapes:

            - **Frontend**: sets ``preference.logging`` via   ``PATCH /users/me`` (composing with
            ``expire_at`` etc.),   then calls /start with no param to flip the gateway on   using the
            just-stored mode.
            - **SDK / scripts**: pass ``True`` or ``False``   explicitly — the SDK has no concept of
            the customer's   stored preference, so it picks the mode per call.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LoggingStatusResponse]
    """

    kwargs = _get_kwargs(
        truncate_long_message=truncate_long_message,
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
    truncate_long_message: bool | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | LoggingStatusResponse | None:
    """Start request logging

     Enable request logging for the authenticated user.

    Args:
        truncate_long_message (bool | None | Unset): Picks the mode. ``True`` → ``truncated`` (8
            KB inline preview, no S3). ``False`` → ``complete`` (full body uploaded to S3 for
            retrieval via the detail endpoint). ``None`` (default) → preserve the user's existing
            ``preference.logging.enabled`` if it's already ``truncated`` or ``complete``; fall back to
            ``truncated`` otherwise.

            Two intended caller shapes:

            - **Frontend**: sets ``preference.logging`` via   ``PATCH /users/me`` (composing with
            ``expire_at`` etc.),   then calls /start with no param to flip the gateway on   using the
            just-stored mode.
            - **SDK / scripts**: pass ``True`` or ``False``   explicitly — the SDK has no concept of
            the customer's   stored preference, so it picks the mode per call.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LoggingStatusResponse
    """

    return sync_detailed(
        client=client,
        truncate_long_message=truncate_long_message,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    truncate_long_message: bool | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | LoggingStatusResponse]:
    """Start request logging

     Enable request logging for the authenticated user.

    Args:
        truncate_long_message (bool | None | Unset): Picks the mode. ``True`` → ``truncated`` (8
            KB inline preview, no S3). ``False`` → ``complete`` (full body uploaded to S3 for
            retrieval via the detail endpoint). ``None`` (default) → preserve the user's existing
            ``preference.logging.enabled`` if it's already ``truncated`` or ``complete``; fall back to
            ``truncated`` otherwise.

            Two intended caller shapes:

            - **Frontend**: sets ``preference.logging`` via   ``PATCH /users/me`` (composing with
            ``expire_at`` etc.),   then calls /start with no param to flip the gateway on   using the
            just-stored mode.
            - **SDK / scripts**: pass ``True`` or ``False``   explicitly — the SDK has no concept of
            the customer's   stored preference, so it picks the mode per call.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LoggingStatusResponse]
    """

    kwargs = _get_kwargs(
        truncate_long_message=truncate_long_message,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    truncate_long_message: bool | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | LoggingStatusResponse | None:
    """Start request logging

     Enable request logging for the authenticated user.

    Args:
        truncate_long_message (bool | None | Unset): Picks the mode. ``True`` → ``truncated`` (8
            KB inline preview, no S3). ``False`` → ``complete`` (full body uploaded to S3 for
            retrieval via the detail endpoint). ``None`` (default) → preserve the user's existing
            ``preference.logging.enabled`` if it's already ``truncated`` or ``complete``; fall back to
            ``truncated`` otherwise.

            Two intended caller shapes:

            - **Frontend**: sets ``preference.logging`` via   ``PATCH /users/me`` (composing with
            ``expire_at`` etc.),   then calls /start with no param to flip the gateway on   using the
            just-stored mode.
            - **SDK / scripts**: pass ``True`` or ``False``   explicitly — the SDK has no concept of
            the customer's   stored preference, so it picks the mode per call.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LoggingStatusResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            truncate_long_message=truncate_long_message,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
