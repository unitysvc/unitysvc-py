"""Async mirror of :mod:`unitysvc_py.resources.secrets`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.message import Message
    from .._generated.models.secret_create import SecretCreate
    from .._generated.models.secret_exists_response import SecretExistsResponse
    from .._generated.models.secret_public import SecretPublic
    from .._generated.models.secret_update import SecretUpdate
    from .._generated.models.secrets_public import SecretsPublic


class AsyncSecretsResource:
    """Async operations on the customer's secret store."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> SecretsPublic:
        from .._generated.api.customer_secrets import customer_secrets_list_secrets

        return unwrap(
            await customer_secrets_list_secrets.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
            )
        )

    async def get(self, secret_id: str | UUID) -> SecretPublic:
        from .._generated.api.customer_secrets import customer_secrets_get_secret

        return unwrap(
            await customer_secrets_get_secret.asyncio_detailed(
                secret_id=UUID(str(secret_id)) if not isinstance(secret_id, UUID) else secret_id,
                client=self._client,
            )
        )

    async def check_exists(self, name: str) -> SecretExistsResponse:
        from .._generated.api.customer_secrets import customer_secrets_check_secret_exists

        return unwrap(
            await customer_secrets_check_secret_exists.asyncio_detailed(
                name=name,
                client=self._client,
            )
        )

    async def create(self, body: SecretCreate | dict[str, Any]) -> SecretPublic:
        from .._generated.api.customer_secrets import customer_secrets_create_secret
        from .._generated.models.secret_create import SecretCreate

        if isinstance(body, dict):
            body = SecretCreate.from_dict(body)

        return unwrap(
            await customer_secrets_create_secret.asyncio_detailed(
                client=self._client,
                body=body,
            )
        )

    async def update(
        self,
        secret_id: str | UUID,
        body: SecretUpdate | dict[str, Any],
    ) -> SecretPublic:
        from .._generated.api.customer_secrets import customer_secrets_update_secret
        from .._generated.models.secret_update import SecretUpdate

        if isinstance(body, dict):
            body = SecretUpdate.from_dict(body)

        return unwrap(
            await customer_secrets_update_secret.asyncio_detailed(
                secret_id=UUID(str(secret_id)) if not isinstance(secret_id, UUID) else secret_id,
                client=self._client,
                body=body,
            )
        )

    async def delete(self, secret_id: str | UUID) -> Message:
        from .._generated.api.customer_secrets import customer_secrets_delete_secret

        return unwrap(
            await customer_secrets_delete_secret.asyncio_detailed(
                secret_id=UUID(str(secret_id)) if not isinstance(secret_id, UUID) else secret_id,
                client=self._client,
            )
        )
