"""Unit tests for the gateway-native wrapper primitives (#1129, #1135).

Two layers under test:

1. The string helpers in :mod:`unitysvc._wrappers` — ``build_wrapped_path``
   and ``_check_relative``. Pure functions, easy to exercise in isolation.

2. The fluent API — ``_Wrappable`` mixin methods (``logged``,
   ``cached``, ``with_failover``, ``with_tee``, ``delayed``,
   ``recurrent``) chained on resources and on :class:`WrappedTarget`.
   We instantiate WrappedTarget directly with a hand-built Client to
   avoid hitting the network; the resource-class mixin behaviour
   (Service / Group) is exercised through the same code path via a
   minimal _Wrappable stand-in.
"""

from __future__ import annotations

import pytest

from unitysvc import Client
from unitysvc._wrappers import (
    WrappedTarget,
    _check_relative,
    _Wrappable,
    build_wrapped_path,
)

# ----------------------------------------------------------------------
# build_wrapped_path
# ----------------------------------------------------------------------


class TestBuildWrappedPath:
    def test_no_wrappers_returns_path_unchanged(self) -> None:
        assert build_wrapped_path("p/svc") == "p/svc"
        assert build_wrapped_path("p/svc/v1/chat") == "p/svc/v1/chat"

    def test_leading_slash_stripped(self) -> None:
        assert build_wrapped_path("/p/svc") == "p/svc"

    def test_log_true_adds_l_prefix(self) -> None:
        assert build_wrapped_path("p/svc", log=True) == "l/p/svc"

    def test_log_complete_adds_complete_query(self) -> None:
        assert build_wrapped_path("p/svc", log="complete") == "l/p/svc?_complete="

    def test_cache_with_ttl(self) -> None:
        assert build_wrapped_path("p/svc", cache_ttl="1h") == "m/p/svc?_ttl=1h"

    def test_cache_without_ttl(self) -> None:
        # ``cache=True`` alone fires /m/ with no TTL query (gateway uses default).
        assert build_wrapped_path("p/svc", cache=True) == "m/p/svc"

    def test_cache_renew_implies_m_prefix(self) -> None:
        # ``cache_renew`` alone is enough to fire /m/ even without ttl.
        out = build_wrapped_path("p/svc", cache_renew=True)
        assert out == "m/p/svc?_renew="

    def test_failover_to_adds_f_prefix(self) -> None:
        assert build_wrapped_path("p/svc", failover_to="p/secondary") == "f/p/svc?_else=p%2Fsecondary"

    def test_tee_to_adds_t_prefix(self) -> None:
        assert build_wrapped_path("p/svc", tee_to="p/audit") == "t/p/svc?_to=p%2Faudit"

    def test_failover_rejects_external_url(self) -> None:
        with pytest.raises(ValueError, match="must be a gateway-relative path"):
            build_wrapped_path("p/svc", failover_to="https://evil.example.com/")

    def test_tee_rejects_external_url(self) -> None:
        with pytest.raises(ValueError, match="must be a gateway-relative path"):
            build_wrapped_path("p/svc", tee_to="http://attacker.test/")

    def test_check_relative_rejects_scheme(self) -> None:
        with pytest.raises(ValueError):
            _check_relative("ftp://x/y", "field")
        with pytest.raises(ValueError):
            _check_relative("file:///etc/passwd", "field")

    def test_all_four_compose_in_canonical_order(self) -> None:
        out = build_wrapped_path(
            "p/svc",
            log=True,
            cache_ttl="10m",
            failover_to="p/secondary",
            tee_to="p/audit",
        )
        # ``l m f t`` is the canonical SDK order — same on-wire behaviour
        # regardless because the gateway treats URL order as cosmetic.
        assert out.startswith("l/m/f/t/p/svc?")
        assert "_ttl=10m" in out
        assert "_else=p%2Fsecondary" in out
        assert "_to=p%2Faudit" in out

    def test_complete_plus_renew_plus_failover_plus_tee(self) -> None:
        out = build_wrapped_path(
            "p/svc",
            log="complete",
            cache_ttl="1h",
            cache_renew=True,
            failover_to="p/anthropic",
            tee_to="p/audit",
        )
        assert out.startswith("l/m/f/t/p/svc?")
        assert "_complete=" in out
        assert "_renew=" in out

    def test_stacking_on_already_wrapped_path(self) -> None:
        # Customer hands in a path that already has primitives baked in.
        # New kwargs prepend on top — gateway flattens the stack at
        # request time.
        out = build_wrapped_path("l/p/svc", cache_ttl="5m")
        assert out == "m/l/p/svc?_ttl=5m"


# ----------------------------------------------------------------------
# Fluent API — _Wrappable / WrappedTarget
# ----------------------------------------------------------------------


class _FakeWrappable(_Wrappable):
    """Minimal _Wrappable for tests — stands in for any resource
    (Service, Alias, Group, etc.) without pulling in the real
    generated types.
    """

    def __init__(self, path: str, client: Client) -> None:
        self._path = path
        self._client = client

    @property
    def path(self) -> str:
        return self._path

    def _get_client(self) -> Client:
        return self._client


@pytest.fixture
def fake_client() -> Client:
    return Client(api_key="svcpass_test", api_base_url="http://localhost:9080")


class TestWrappedTargetChain:
    """Each wrapper builder returns a WrappedTarget whose ``path``
    matches what ``build_wrapped_path`` would produce. Chains compose.
    """

    def test_bare_resource_path(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        assert svc.path == "p/svc-id"

    def test_logged_returns_wrappedtarget_with_l_prefix(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.logged()
        assert isinstance(wrapped, WrappedTarget)
        assert wrapped.path == "l/p/svc-id"

    def test_logged_complete(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.logged(_complete=True)
        assert wrapped.path == "l/p/svc-id?_complete="

    def test_cached_default(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.cached()
        # ``cached()`` with no args → /m/ with no TTL query (gateway default).
        assert wrapped.path == "m/p/svc-id"

    def test_cached_with_ttl(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.cached(_ttl="1h")
        assert wrapped.path == "m/p/svc-id?_ttl=1h"

    def test_cached_with_renew(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.cached(_ttl="60s", _renew=True)
        assert wrapped.path.startswith("m/p/svc-id?")
        assert "_ttl=60s" in wrapped.path
        assert "_renew=" in wrapped.path

    def test_with_failover_secondary_is_wrappable(self, fake_client: Client) -> None:
        primary = _FakeWrappable("p/primary", fake_client)
        backup = _FakeWrappable("p/backup", fake_client)
        wrapped = primary.with_failover(backup)
        assert wrapped.path == "f/p/primary?_else=p%2Fbackup"

    def test_with_tee(self, fake_client: Client) -> None:
        primary = _FakeWrappable("p/x", fake_client)
        audit = _FakeWrappable("p/y", fake_client)
        wrapped = primary.with_tee(audit)
        assert wrapped.path.startswith("t/p/x?_to=")
        assert "_to=p%2Fy" in wrapped.path

    def test_chain_logged_then_cached(self, fake_client: Client) -> None:
        # Chaining produces nested WrappedTargets.
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.logged().cached(_ttl="1h")
        assert isinstance(wrapped, WrappedTarget)
        # Cached wraps the already-logged path: m/l/p/svc-id?_ttl=1h
        assert wrapped.path == "m/l/p/svc-id?_ttl=1h"

    def test_chain_cached_then_logged(self, fake_client: Client) -> None:
        # Order changes the on-wire URL but not the on-gateway behaviour.
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.cached(_ttl="1h").logged()
        assert wrapped.path == "l/m/p/svc-id?_ttl=1h"

    def test_chain_with_failover_secondary_is_wrapped(self, fake_client: Client) -> None:
        # Compose secondaries with their own wrappers.
        primary = _FakeWrappable("p/a", fake_client)
        backup = _FakeWrappable("p/b", fake_client)
        wrapped = primary.with_failover(backup.cached(_ttl="5m"))
        # The failover_to value is the inner wrapped path, urlencoded.
        assert wrapped.path.startswith("f/p/a?_else=")
        # Encoded form of "m/p/b?_ttl=5m"
        assert "m%2Fp%2Fb%3F_ttl%3D5m" in wrapped.path

    def test_delayed_requires_at_or_in(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        with pytest.raises(ValueError, match="requires exactly one"):
            svc.delayed()
        with pytest.raises(ValueError, match="requires exactly one"):
            svc.delayed(_at="2026-01-01", _in="5s")

    def test_delayed_at(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.delayed(_at="2026-06-01T10:00:00Z")
        assert wrapped.path == "d/p/svc-id?_at=2026-06-01T10%3A00%3A00Z"

    def test_delayed_in(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.delayed(_in="5s")
        assert wrapped.path == "d/p/svc-id?_in=5s"

    def test_recurrent(self, fake_client: Client) -> None:
        svc = _FakeWrappable("p/svc-id", fake_client)
        wrapped = svc.recurrent(_every="5m")
        assert wrapped.path == "r/p/svc-id?_every=5m"

    def test_wrappedtarget_repr(self, fake_client: Client) -> None:
        wrapped = WrappedTarget("l/p/svc-id", fake_client)
        assert repr(wrapped) == "<WrappedTarget path='l/p/svc-id'>"


# ----------------------------------------------------------------------
# WrappedTarget.dispatch — no-network construction via httpx.MockTransport
# ----------------------------------------------------------------------


def _capture_url_via_mock_transport(client: Client) -> dict[str, str]:
    """Install a MockTransport on the SDK's httpx client; return a
    dict where ``url`` gets populated by the first request.
    """
    import httpx

    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"ok": True})

    httpx_client = client._client.get_httpx_client()
    httpx_client._transport = httpx.MockTransport(handler)
    return captured


class TestWrappedTargetDispatch:
    """``WrappedTarget.dispatch`` should send the wrapped path through
    ``client.dispatch`` and produce the URL we expect at the gateway.
    """

    def test_dispatch_sends_to_wrapped_path(self) -> None:
        with Client(api_key="svcpass_test", api_base_url="http://localhost:9080") as client:
            captured = _capture_url_via_mock_transport(client)
            svc = _FakeWrappable("p/svc-id", client)
            wrapped = svc.cached(_ttl="1h").logged()
            wrapped.dispatch(json={"hi": "there"})
            assert captured["url"].startswith("http://localhost:9080/l/m/p/svc-id?")
            assert "_ttl=1h" in captured["url"]

    def test_dispatch_failover_composition(self) -> None:
        with Client(api_key="svcpass_test", api_base_url="http://localhost:9080") as client:
            captured = _capture_url_via_mock_transport(client)
            primary = _FakeWrappable("p/primary", client)
            backup = _FakeWrappable("p/backup", client)
            primary.with_failover(backup).dispatch(json={"x": 1})
            assert captured["url"].startswith("http://localhost:9080/f/p/primary?")
            assert "_else=" in captured["url"]


# ----------------------------------------------------------------------
# Client.dispatch — escape hatch for customer-built paths
# ----------------------------------------------------------------------


class TestClientDispatchEscapeHatch:
    def test_passes_path_through_untouched(self) -> None:
        with Client(api_key="svcpass_test", api_base_url="http://localhost:9080") as client:
            captured = _capture_url_via_mock_transport(client)
            # Customer-constructed path with primitives baked in; the
            # escape hatch sends it verbatim.
            client.dispatch("l/p/some-id?_complete=", json={"x": 1})
            assert captured["url"] == "http://localhost:9080/l/p/some-id?_complete="

    def test_derives_gateway_root_from_control_plane(self) -> None:
        with Client(api_key="svcpass_test", base_url="https://api.example.test/v1") as client:
            captured = _capture_url_via_mock_transport(client)
            client.dispatch("p/some-id", json={})
            assert captured["url"] == "https://api.example.test/p/some-id"
