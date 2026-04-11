"""Asynchronous customer SDK client.

Mirror of :class:`unitysvc_py.Client` that uses the generated
``asyncio_detailed`` entry points instead of ``sync_detailed``. Every
resource method on :class:`AsyncClient` is an ``async def`` returning
the same typed model the sync version returns.

Example::

    import asyncio
    from unitysvc_py import AsyncClient

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
from .client import (
    DEFAULT_API_URL,
    ENV_API_BASE_URL,
    ENV_API_KEY,
    ENV_API_URL,
    ENV_S3_BASE_URL,
    ENV_SMTP_BASE_URL,
)

if TYPE_CHECKING:
    from .resources.aaliases import AsyncAliasesResource
    from .resources.arecurrent_requests import AsyncRecurrentRequestsResource
    from .resources.asecrets import AsyncSecretsResource


class AsyncClient:
    """Asynchronous customer SDK client.

    Args:
        api_key: A customer API key (``svcpass_...``).
        base_url: Override the control-plane URL. Falls back to
            ``UNITYSVC_API_URL``, then to :data:`DEFAULT_API_URL`.
        api_base_url, s3_base_url, smtp_base_url: Optional gateway
            base URLs, matching the sync :class:`Client`.
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

        self.api_base_url = api_base_url or os.environ.get(ENV_API_BASE_URL)
        self.s3_base_url = s3_base_url or os.environ.get(ENV_S3_BASE_URL)
        self.smtp_base_url = smtp_base_url or os.environ.get(ENV_SMTP_BASE_URL)

        self._aliases: AsyncAliasesResource | None = None
        self._recurrent_requests: AsyncRecurrentRequestsResource | None = None
        self._secrets: AsyncSecretsResource | None = None

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
    @property
    def aliases(self) -> AsyncAliasesResource:
        if self._aliases is None:
            from .resources.aaliases import AsyncAliasesResource

            self._aliases = AsyncAliasesResource(self._client)
        return self._aliases

    @property
    def recurrent_requests(self) -> AsyncRecurrentRequestsResource:
        if self._recurrent_requests is None:
            from .resources.arecurrent_requests import AsyncRecurrentRequestsResource

            self._recurrent_requests = AsyncRecurrentRequestsResource(self._client)
        return self._recurrent_requests

    @property
    def secrets(self) -> AsyncSecretsResource:
        if self._secrets is None:
            from .resources.asecrets import AsyncSecretsResource

            self._secrets = AsyncSecretsResource(self._client)
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
