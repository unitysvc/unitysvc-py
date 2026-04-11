"""``client.secrets`` — customer secret management.

Wraps the customer-tagged ``/v1/customer/secrets/*`` operations from
the generated low-level client. Each method calls ``sync_detailed``
and passes the result through :func:`unitysvc_py._http.unwrap`, so
callers always get a populated typed model or a
:class:`~unitysvc_py.exceptions.UnitysvcSDKError`.
"""

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


class SecretsResource:
    """Operations on the customer's secret store (``/v1/customer/secrets``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> SecretsPublic:
        """List all secrets owned by the authenticated customer."""
        from .._generated.api.customer_secrets import customer_secrets_list_secrets

        return unwrap(
            customer_secrets_list_secrets.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
            )
        )

    def get(self, secret_id: str | UUID) -> SecretPublic:
        """Get a single secret by id."""
        from .._generated.api.customer_secrets import customer_secrets_get_secret

        return unwrap(
            customer_secrets_get_secret.sync_detailed(
                secret_id=UUID(str(secret_id)) if not isinstance(secret_id, UUID) else secret_id,
                client=self._client,
            )
        )

    def check_exists(self, name: str) -> SecretExistsResponse:
        """Check whether a secret with the given name exists."""
        from .._generated.api.customer_secrets import customer_secrets_check_secret_exists

        return unwrap(
            customer_secrets_check_secret_exists.sync_detailed(
                name=name,
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def create(self, body: SecretCreate | dict[str, Any]) -> SecretPublic:
        """Create a new secret."""
        from .._generated.api.customer_secrets import customer_secrets_create_secret
        from .._generated.models.secret_create import SecretCreate

        if isinstance(body, dict):
            body = SecretCreate.from_dict(body)

        return unwrap(
            customer_secrets_create_secret.sync_detailed(
                client=self._client,
                body=body,
            )
        )

    def update(
        self,
        secret_id: str | UUID,
        body: SecretUpdate | dict[str, Any],
    ) -> SecretPublic:
        """Update an existing secret."""
        from .._generated.api.customer_secrets import customer_secrets_update_secret
        from .._generated.models.secret_update import SecretUpdate

        if isinstance(body, dict):
            body = SecretUpdate.from_dict(body)

        return unwrap(
            customer_secrets_update_secret.sync_detailed(
                secret_id=UUID(str(secret_id)) if not isinstance(secret_id, UUID) else secret_id,
                client=self._client,
                body=body,
            )
        )

    def delete(self, secret_id: str | UUID) -> Message:
        """Delete a secret by id."""
        from .._generated.api.customer_secrets import customer_secrets_delete_secret

        return unwrap(
            customer_secrets_delete_secret.sync_detailed(
                secret_id=UUID(str(secret_id)) if not isinstance(secret_id, UUID) else secret_id,
                client=self._client,
            )
        )
