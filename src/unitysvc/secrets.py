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

from ._http import LowLevelClient, unwrap

if TYPE_CHECKING:
    from ._generated.models.message import Message
    from ._generated.models.secret_public import SecretPublic
    from ._generated.models.secrets_public import SecretsPublic


class Secrets:
    """Operations on the customer's secret store (``/v1/customer/secrets``)."""

    def __init__(self, client: LowLevelClient) -> None:
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
        """Get a single secret by name.

        Metadata for a **secret** (``.value`` is ``None`` — write-only); a
        **variable** additionally returns its decrypted ``.value``.
        """
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
    def set(
        self, name: str, value: str, *, sensitive: bool | None = None
    ) -> SecretPublic:
        """Set ``name`` to ``value`` (idempotent — creates or replaces).

        Maps to ``PUT /v1/customer/secrets/{name}``. The value is encrypted
        server-side.

        ``sensitive`` controls whether this is a **secret** (write-only; the
        default) or a **variable** (its value is returned to authorized callers,
        e.g. so you can confirm what you stored). It is honored only when the
        row is **created** — an existing row cannot switch between secret and
        variable (attempting to changes raises a 409 ``ApiError``). Leave it
        ``None`` to accept the default (a secret) or preserve an existing row's
        kind on update.

        Args:
            name: Secret name (must match ``^[A-Z_][A-Z0-9_]*$``).
            value: Secret value. May be empty.
            sensitive: ``False`` creates a viewable variable, ``True`` an
                explicit secret, ``None`` (default) leaves it unset.

        Returns:
            ``SecretPublic`` metadata. For a variable, ``.value`` is populated.
        """
        from ._generated.api.customer_secrets import customer_secrets_set_secret
        from ._generated.models.secret_update import SecretUpdate
        from ._generated.types import UNSET

        return unwrap(
            customer_secrets_set_secret.sync_detailed(
                name=name,
                client=self._client,
                body=SecretUpdate(
                    value=value,
                    sensitive=UNSET if sensitive is None else sensitive,
                ),
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
