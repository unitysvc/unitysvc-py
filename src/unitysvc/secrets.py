"""``client.secrets`` — customer secret management.

Wraps the customer-tagged ``/v1/customer/secrets/*`` operations from
the generated low-level client. Each method calls ``sync_detailed``
and passes the result through :func:`unitysvc._http.unwrap`, so
callers always get a populated typed model or a
:class:`~unitysvc.exceptions.UnitysvcSDKError`.

API shape mirrors GitHub's secrets API (see unitysvc#798):

* :meth:`list`   — ``GET /``
* :meth:`get`    — ``GET /{name}``      (metadata only)
* :meth:`set`    — ``PUT /{name}``      (idempotent create-or-replace)
* :meth:`delete` — ``DELETE /{name}``

There is no separate ``create`` method — :meth:`set` does both create
and rotate in one idempotent call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.message import Message
    from ._generated.models.secret_public import SecretPublic
    from ._generated.models.secrets_public import SecretsPublic


class Secrets:
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
        from ._generated.api.customer_secrets import customer_secrets_list_secrets

        return unwrap(
            customer_secrets_list_secrets.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
            )
        )

    def get(self, name: str) -> SecretPublic:
        """Get a single secret by name (metadata only — value is never returned)."""
        from ._generated.api.customer_secrets import customer_secrets_get_secret

        return unwrap(
            customer_secrets_get_secret.sync_detailed(
                name=name,
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def set(self, name: str, value: str) -> SecretPublic:
        """Set ``name`` to ``value`` (idempotent — creates or replaces).

        Maps to ``PUT /v1/customer/secrets/{name}``. Returns the secret's
        public metadata; the value itself is never echoed back. The
        encryption is handled server-side.

        Args:
            name: Secret name (must match ``^[A-Z_][A-Z0-9_]*$``).
            value: Secret value. May be empty.

        Returns:
            ``SecretPublic`` metadata for the stored secret.
        """
        from ._generated.api.customer_secrets import customer_secrets_set_secret
        from ._generated.models.secret_update import SecretUpdate

        return unwrap(
            customer_secrets_set_secret.sync_detailed(
                name=name,
                client=self._client,
                body=SecretUpdate(value=value),
            )
        )

    def delete(self, name: str) -> Message:
        """Delete a secret by name. This action cannot be undone."""
        from ._generated.api.customer_secrets import customer_secrets_delete_secret

        return unwrap(
            customer_secrets_delete_secret.sync_detailed(
                name=name,
                client=self._client,
            )
        )
