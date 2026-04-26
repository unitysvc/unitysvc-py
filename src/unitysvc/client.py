"""Public customer SDK client.

The :class:`Client` is a thin facade over the auto-generated low-level
client in :mod:`unitysvc._generated`. It exposes resource namespaces
(``aliases``, ``recurrent_requests``, ``secrets``) that map 1:1 to the
customer-tagged backend routes.

Example::

    from unitysvc import Client

    client = Client(api_key="svcpass_...")
    secrets = client.secrets.list()
    for s in secrets.data:
        print(s.name)

    # Or read credentials from the environment
    client = Client.from_env()

The customer context is encoded entirely in the API key, so no
explicit ``customer_id`` is required. The default base URL points at
the production API::

    https://api.unitysvc.com/v1

Override via the ``base_url`` constructor argument or the
``UNITYSVC_API_URL`` environment variable.

Beyond the control-plane API URL, the customer SDK also recognizes a
set of per-gateway base URLs that downstream inference SDKs
(``unitysvc-services-*``) pick up through the environment:

- ``UNITYSVC_API_BASE_URL`` — HTTP API gateway (e.g. OpenAI-compatible)
- ``UNITYSVC_S3_BASE_URL``  — S3-compatible gateway
- ``UNITYSVC_SMTP_BASE_URL`` — SMTP gateway

These are exposed on :class:`Client` for convenience (``client.api_base_url``,
``client.s3_base_url``, ``client.smtp_base_url``) but are not required
for any ``unitysvc`` call — the control-plane client only needs the
API URL and API key.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import httpx

from ._generated.client import AuthenticatedClient as _LowLevelClient

if TYPE_CHECKING:
    from ._generated.models.resolve_response import ResolveResponse
    from .aliases import Aliases
    from .enrollments import Enrollments
    from .groups import Groups
    from .recurrent_requests import RecurrentRequests
    from .secrets import Secrets
    from .services import Services

DEFAULT_API_URL = "https://api.unitysvc.com/v1"

ENV_API_KEY = "UNITYSVC_API_KEY"
ENV_API_URL = "UNITYSVC_API_URL"
ENV_API_BASE_URL = "UNITYSVC_API_BASE_URL"
ENV_S3_BASE_URL = "UNITYSVC_S3_BASE_URL"
ENV_SMTP_BASE_URL = "UNITYSVC_SMTP_BASE_URL"


class Client:
    """Synchronous customer SDK client.

    Args:
        api_key: A customer API key (``svcpass_...``). Encodes the
            customer context, so no separate ``customer_id`` is
            required.
        base_url: Override the default control-plane URL. Falls back to
            ``UNITYSVC_API_URL``, then to :data:`DEFAULT_API_URL`.
        api_base_url: HTTP API gateway base URL. Falls back to
            ``UNITYSVC_API_BASE_URL``. Exposed for downstream SDK use.
        s3_base_url: S3 gateway base URL. Falls back to
            ``UNITYSVC_S3_BASE_URL``.
        smtp_base_url: SMTP gateway base URL. Falls back to
            ``UNITYSVC_SMTP_BASE_URL``.
        timeout: Per-request timeout in seconds. Default 30s.
        verify_ssl: Whether to verify TLS certificates. Default ``True``.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        api_base_url: str | None = None,
        s3_base_url: str | None = None,
        smtp_base_url: str | None = None,
        timeout: float | httpx.Timeout | None = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        resolved_base_url = base_url or os.environ.get(ENV_API_URL) or DEFAULT_API_URL

        if isinstance(timeout, (int, float)):
            timeout_obj = httpx.Timeout(float(timeout))
        else:
            timeout_obj = timeout  # type: ignore[assignment]

        self._client = _LowLevelClient(
            base_url=resolved_base_url,
            token=api_key,
            timeout=timeout_obj,
            verify_ssl=verify_ssl,
            raise_on_unexpected_status=False,
        )
        self._api_key = api_key
        self._base_url = resolved_base_url

        # Gateway URLs — configuration only, not used by the SDK itself.
        self.api_base_url = api_base_url or os.environ.get(ENV_API_BASE_URL)
        self.s3_base_url = s3_base_url or os.environ.get(ENV_S3_BASE_URL)
        self.smtp_base_url = smtp_base_url or os.environ.get(ENV_SMTP_BASE_URL)

        # Lazy resource initialization.
        self._aliases: Aliases | None = None
        self._enrollments: Enrollments | None = None
        self._groups: Groups | None = None
        self._recurrent_requests: RecurrentRequests | None = None
        self._secrets: Secrets | None = None
        self._services: Services | None = None

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls, **kwargs: object) -> Client:
        """Construct a client from environment variables.

        Reads :data:`ENV_API_KEY` (required) and :data:`ENV_API_URL`
        (optional). Any extra keyword arguments are forwarded to the
        :class:`Client` constructor.
        """
        api_key = os.environ.get(ENV_API_KEY)
        if not api_key:
            raise RuntimeError(
                f"Environment variable {ENV_API_KEY} is not set. "
                f"Set it to a customer API key (svcpass_...) or pass api_key= explicitly."
            )
        return cls(api_key=api_key, **kwargs)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Resource namespaces (lazy)
    # ------------------------------------------------------------------
    @property
    def aliases(self) -> Aliases:
        if self._aliases is None:
            from .aliases import Aliases

            self._aliases = Aliases(self._client)
        return self._aliases

    @property
    def enrollments(self) -> Enrollments:
        if self._enrollments is None:
            from .enrollments import Enrollments

            self._enrollments = Enrollments(self._client)
        return self._enrollments

    @property
    def groups(self) -> Groups:
        if self._groups is None:
            from .groups import Groups

            self._groups = Groups(self._client, parent=self)
        return self._groups

    @property
    def services(self) -> Services:
        if self._services is None:
            from .services import Services

            self._services = Services(self._client, parent=self)
        return self._services

    # ------------------------------------------------------------------
    # Resolve (one-shot primitive, not a resource namespace)
    # ------------------------------------------------------------------
    def resolve(
        self,
        *,
        path: str,
        routing_key: dict | None = None,
        gateway: str = "api",
        strategy: str | None = None,
    ) -> ResolveResponse:
        """Dry-run resolve a gateway path + routing key.

        Mirrors the gateway's selection decision without executing
        the upstream call — useful for debugging routing or
        picking a specific service/interface ahead of dispatch.
        See :mod:`unitysvc.resolve` for details.
        """
        from .resolve import resolve as _resolve

        return _resolve(
            self._client,
            path=path,
            routing_key=routing_key,
            gateway=gateway,
            strategy=strategy,
        )

    @property
    def recurrent_requests(self) -> RecurrentRequests:
        if self._recurrent_requests is None:
            from .recurrent_requests import RecurrentRequests

            self._recurrent_requests = RecurrentRequests(self._client)
        return self._recurrent_requests

    @property
    def secrets(self) -> Secrets:
        if self._secrets is None:
            from .secrets import Secrets

            self._secrets = Secrets(self._client)
        return self._secrets

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Close the underlying httpx client and release its connection pool."""
        try:
            self._client.get_httpx_client().close()
        except Exception:
            pass

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
