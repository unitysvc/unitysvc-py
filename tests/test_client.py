"""Smoke tests for the public :class:`unitysvc_py.Client` facade.

These exercise construction, env-var resolution, and resource lookup
without hitting the network. HTTP calls are covered by mocked tests
against ``httpx`` (see ``test_secrets.py``).
"""

from __future__ import annotations

import pytest

from unitysvc_py import (
    DEFAULT_API_URL,
    AsyncClient,
    AuthenticationError,
    Client,
    UnitysvcSDKError,
    ValidationError,
)


def test_client_requires_api_key() -> None:
    with pytest.raises(ValueError, match="api_key is required"):
        Client(api_key="")


def test_client_defaults_to_staging() -> None:
    with Client(api_key="svcpass_test") as client:
        assert client._base_url == DEFAULT_API_URL


def test_client_base_url_override() -> None:
    with Client(api_key="svcpass_test", base_url="https://example.test/v1") as client:
        assert client._base_url == "https://example.test/v1"


def test_client_env_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_API_URL", "https://from-env.test/v1")
    monkeypatch.setenv("UNITYSVC_API_BASE_URL", "https://gateway.test")
    monkeypatch.setenv("UNITYSVC_S3_BASE_URL", "https://s3.test")
    monkeypatch.setenv("UNITYSVC_SMTP_BASE_URL", "https://smtp.test")

    with Client(api_key="svcpass_test") as client:
        assert client._base_url == "https://from-env.test/v1"
        assert client.api_base_url == "https://gateway.test"
        assert client.s3_base_url == "https://s3.test"
        assert client.smtp_base_url == "https://smtp.test"


def test_client_from_env_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UNITYSVC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="UNITYSVC_API_KEY is not set"):
        Client.from_env()


def test_client_from_env_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_API_KEY", "svcpass_test")
    with Client.from_env() as client:
        assert client._api_key == "svcpass_test"


def test_client_resources_are_lazy_and_cached() -> None:
    with Client(api_key="svcpass_test") as client:
        first = client.secrets
        second = client.secrets
        assert first is second

        # All resource namespaces should be reachable.
        assert client.aliases is not None
        assert client.recurrent_requests is not None


def test_async_client_defaults_to_staging() -> None:
    client = AsyncClient(api_key="svcpass_test")
    assert client._base_url == DEFAULT_API_URL
    # Resource lookups should work synchronously (only the actual HTTP
    # calls are async).
    assert client.secrets is not None
    assert client.aliases is not None
    assert client.recurrent_requests is not None


def test_exception_hierarchy() -> None:
    """AuthenticationError and ValidationError should share the APIError root."""
    assert issubclass(AuthenticationError, UnitysvcSDKError)
    assert issubclass(ValidationError, UnitysvcSDKError)
