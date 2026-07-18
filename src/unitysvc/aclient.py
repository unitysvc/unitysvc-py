"""Asynchronous customer SDK client.

Mirror of :class:`unitysvc.Client` that uses the generated
``asyncio_detailed`` entry points instead of ``sync_detailed``. Every
resource method on :class:`AsyncClient` is an ``async def`` returning
the same typed model the sync version returns.

Example::

    import asyncio
    from unitysvc import AsyncClient

    async def main():
        async with AsyncClient(api_key="svcpass_...") as client:
            secrets = await client.secrets.list()
            for s in secrets.data:
                print(s.name)

    asyncio.run(main())
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import httpx

from ._generated.client import AuthenticatedClient as _LowLevelClient
from ._generated.client import Client as _AnonymousLowLevelClient
from ._http import LowLevelClient
from .client import (
    DEFAULT_API_URL,
    ENV_API_BASE_URL,
    ENV_API_KEY,
    ENV_API_URL,
    ENV_S3_BASE_URL,
    ENV_SMTP_BASE_URL,
)
from .exceptions import AuthenticationError

if TYPE_CHECKING:
    from ._generated.models.resolve_response import ResolveResponse
    from .aaliases import AsyncAliases
    from .abroadcasts import AsyncBroadcasts
    from .achains import AsyncChains
    from .aenrollments import AsyncEnrollments
    from .afiles import AsyncFiles
    from .agroups import AsyncGroups
    from .arecurrent_requests import AsyncRecurrentRequests
    from .arequest_logs import AsyncRequestLogs
    from .asecrets import AsyncSecrets
    from .aservices import AsyncServices


class AsyncClient:
    """Asynchronous customer SDK client.

    Args:
        api_key: A customer API key (``svcpass_...``). Omit it (or pass
        base_url: Override the control-plane URL. Falls back to
            ``UNITYSVC_API_URL``, then to :data:`DEFAULT_API_URL`.
        api_base_url, s3_base_url, smtp_base_url: Optional gateway
            base URLs, matching the sync :class:`Client`.
        timeout: Per-request timeout in seconds. Default 30s.
        verify_ssl: Whether to verify TLS certificates. Default ``True``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        api_base_url: str | None = None,
        s3_base_url: str | None = None,
        smtp_base_url: str | None = None,
        timeout: float | httpx.Timeout | None = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        # `None` (or omitted) means "browse anonymously". An empty string
        # almost always means a missing env var got passed through, so it
        # stays an error rather than silently downgrading the caller to
        # anonymous and returning a confusingly narrow catalog.
        if api_key is not None and not api_key:
            raise ValueError(
                "api_key is required. Pass api_key=None (or omit it) to "
                "browse the public catalog anonymously."
            )

        resolved_base_url = base_url or os.environ.get(ENV_API_URL) or DEFAULT_API_URL

        if isinstance(timeout, (int, float)):
            timeout_obj = httpx.Timeout(float(timeout))
        else:
            timeout_obj = timeout  # type: ignore[assignment]

        # Without a key, use the generated unauthenticated client: it sends
        # no Authorization header at all, which is what the customer API
        # reads as "anonymous" (unitysvc#1610). An empty-token
        # AuthenticatedClient would send a malformed `Bearer ` header and
        # earn a 401 instead.
        self._client: LowLevelClient
        if api_key:
            self._client = _LowLevelClient(
                base_url=resolved_base_url,
                token=api_key,
                timeout=timeout_obj,
                verify_ssl=verify_ssl,
                raise_on_unexpected_status=False,
            )
        else:
            self._client = _AnonymousLowLevelClient(
                base_url=resolved_base_url,
                timeout=timeout_obj,
                verify_ssl=verify_ssl,
                raise_on_unexpected_status=False,
            )
        self._api_key = api_key
        self._base_url = resolved_base_url

        self.api_base_url = api_base_url or os.environ.get(ENV_API_BASE_URL)
        self.s3_base_url = s3_base_url or os.environ.get(ENV_S3_BASE_URL)
        self.smtp_base_url = smtp_base_url or os.environ.get(ENV_SMTP_BASE_URL)

        self._aliases: AsyncAliases | None = None
        self._broadcasts: AsyncBroadcasts | None = None
        self._chains: AsyncChains | None = None
        self._enrollments: AsyncEnrollments | None = None
        self._files: AsyncFiles | None = None
        self._groups: AsyncGroups | None = None
        self._recurrent_requests: AsyncRecurrentRequests | None = None
        self._request_logs: AsyncRequestLogs | None = None
        self._secrets: AsyncSecrets | None = None
        self._services: AsyncServices | None = None

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls, **kwargs: object) -> AsyncClient:
        """Construct an :class:`AsyncClient` from environment variables."""
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
    def _authenticated(self) -> _LowLevelClient:
        """Return the low-level client, or explain that a key is needed.

        Only reached from resources whose every operation requires
        credentials. Catalog reads stay reachable anonymously, and mixed
        resources (``groups`` exposes both public reads and authenticated
        writes) let the server decide with a 401 — gating those at the
        resource level would wrongly block the public half.
        """
        if not isinstance(self._client, _LowLevelClient):
            raise AuthenticationError(
                "This operation requires an api_key. Construct the client "
                "with api_key=... — the no-key client can only browse the "
                "public catalog.",
                status_code=401,
            )
        return self._client

    @property
    def aliases(self) -> AsyncAliases:
        if self._aliases is None:
            from .aaliases import AsyncAliases

            self._aliases = AsyncAliases(self._client)
        return self._aliases

    @property
    def broadcasts(self) -> AsyncBroadcasts:
        if self._broadcasts is None:
            from .abroadcasts import AsyncBroadcasts

            self._broadcasts = AsyncBroadcasts(self._client, parent=self)
        return self._broadcasts

    @property
    def chains(self) -> AsyncChains:
        if self._chains is None:
            from .achains import AsyncChains

            self._chains = AsyncChains(self._client, parent=self)
        return self._chains

    @property
    def enrollments(self) -> AsyncEnrollments:
        if self._enrollments is None:
            from .aenrollments import AsyncEnrollments

            self._enrollments = AsyncEnrollments(self._client, parent=self)
        return self._enrollments

    @property
    def files(self) -> AsyncFiles:
        if self._files is None:
            from .afiles import AsyncFiles

            self._files = AsyncFiles(self._authenticated())
        return self._files

    @property
    def groups(self) -> AsyncGroups:
        if self._groups is None:
            from .agroups import AsyncGroups

            self._groups = AsyncGroups(self._client, parent=self)
        return self._groups

    @property
    def services(self) -> AsyncServices:
        if self._services is None:
            from .aservices import AsyncServices

            self._services = AsyncServices(self._client, parent=self)
        return self._services

    # ------------------------------------------------------------------
    # Dispatch (lower-level escape hatch)
    # ------------------------------------------------------------------
    async def dispatch(
        self,
        path: str,
        *,
        method: str = "POST",
        json: object = None,
        data: object = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send a request to a gateway-relative path (async).

        Async mirror of :meth:`unitysvc.Client.dispatch`. ``path`` must
        be gateway-relative (no scheme, no leading slash) — e.g.
        ``"c/<chain>"``, ``"b/<broadcast>"``, ``"l/p/<service-id>"``.
        Resolves the gateway base URL from ``api_base_url`` (falling
        back to the control-plane base with the trailing ``/v1``
        stripped). Raises ``ValueError`` when neither is resolvable.
        """
        from .agroups import _http_dispatch_async

        gateway_root = self.api_base_url
        if not gateway_root:
            stripped = self._base_url.rstrip("/")
            if stripped.endswith("/v1"):
                stripped = stripped[: -len("/v1")]
            gateway_root = stripped
        if not gateway_root:
            raise ValueError(
                "Cannot resolve gateway base URL. Set api_base_url= on "
                "the AsyncClient constructor or UNITYSVC_API_BASE_URL in "
                "the environment."
            )

        return await _http_dispatch_async(
            self._client,
            base_url=gateway_root,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Resolve (one-shot primitive)
    # ------------------------------------------------------------------
    async def resolve(
        self,
        *,
        path: str,
        routing_key: dict | None = None,
        gateway: str = "api",
        strategy: str | None = None,
    ) -> ResolveResponse:
        """Async dry-run resolve. See :func:`unitysvc.resolve.resolve`."""
        from .aresolve import resolve as _resolve

        return await _resolve(
            self._client,
            path=path,
            routing_key=routing_key,
            gateway=gateway,
            strategy=strategy,
        )

    @property
    def recurrent_requests(self) -> AsyncRecurrentRequests:
        if self._recurrent_requests is None:
            from .arecurrent_requests import AsyncRecurrentRequests

            self._recurrent_requests = AsyncRecurrentRequests(self._client)
        return self._recurrent_requests

    @property
    def request_logs(self) -> AsyncRequestLogs:
        if self._request_logs is None:
            from .arequest_logs import AsyncRequestLogs

            self._request_logs = AsyncRequestLogs(self._client)
        return self._request_logs

    @property
    def secrets(self) -> AsyncSecrets:
        if self._secrets is None:
            from .asecrets import AsyncSecrets

            self._secrets = AsyncSecrets(self._client)
        return self._secrets

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def aclose(self) -> None:
        """Close the underlying async httpx client."""
        try:
            await self._client.get_async_httpx_client().aclose()
        except Exception:
            pass

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
