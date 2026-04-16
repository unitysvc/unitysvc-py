"""Async mirror of :mod:`unitysvc.secrets`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.message import Message
    from ._generated.models.secret_create import SecretCreate
    from ._generated.models.secret_public import SecretPublic
    from ._generated.models.secret_update import SecretUpdate
    from ._generated.models.secrets_public import SecretsPublic


class AsyncSecrets:
    """Async operations on the customer's secret store."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> SecretsPublic:
        from ._generated.api.customer_secrets import customer_secrets_list_secrets

        return unwrap(
            await customer_secrets_list_secrets.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
            )
        )

    async def get(self, name: str) -> SecretPublic:
        from ._generated.api.customer_secrets import customer_secrets_get_secret

        return unwrap(
            await customer_secrets_get_secret.asyncio_detailed(
                name=name,
                client=self._client,
            )
        )

    async def create(self, body: SecretCreate | dict[str, Any]) -> SecretPublic:
        from ._generated.api.customer_secrets import customer_secrets_create_secret
        from ._generated.models.secret_create import SecretCreate

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
        name: str,
        body: SecretUpdate | dict[str, Any],
    ) -> SecretPublic:
        from ._generated.api.customer_secrets import customer_secrets_update_secret
        from ._generated.models.secret_update import SecretUpdate

        if isinstance(body, dict):
            body = SecretUpdate.from_dict(body)

        return unwrap(
            await customer_secrets_update_secret.asyncio_detailed(
                name=name,
                client=self._client,
                body=body,
            )
        )

    async def delete(self, name: str) -> Message:
        from ._generated.api.customer_secrets import customer_secrets_delete_secret

        return unwrap(
            await customer_secrets_delete_secret.asyncio_detailed(
                name=name,
                client=self._client,
            )
        )
