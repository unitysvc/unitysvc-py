"""Unit tests for the gateway-native wrapper helpers (#1129, #1135).

Covers:

* ``build_wrapped_path`` — each wrapper individually, all-four
  composition, URL-order invariance at the gateway (since wrappers
  are emitted in fixed order regardless of customer input), external-
  URL rejection for the secondary-path kwargs, ``?_complete`` /
  ``?_renew`` presence-only semantics.
* ``apply_wrappers`` — fast path on no-wrapper kwargs; correct
  splitting of a full gateway URL into ``(gateway_root,
  wrapped_path)`` so wrapper segments insert between host and path.
* ``Client.dispatch`` — gateway-base derivation from the control-plane
  base URL, no-network path construction.
"""

from __future__ import annotations

import pytest

from unitysvc import Client
from unitysvc._wrappers import (
    apply_wrappers,
    build_wrapped_path,
    has_wrappers,
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
        # urlencode serialises empty-string values as ``_complete=``;
        # the gateway treats that as the presence flag.
        assert build_wrapped_path("p/svc", log="complete") == "l/p/svc?_complete="

    def test_cache_ttl_adds_m_prefix_and_ttl_query(self) -> None:
        out = build_wrapped_path("p/svc", cache_ttl="1h")
        assert out == "m/p/svc?_ttl=1h"

    def test_cache_renew_only_when_cache_ttl_set(self) -> None:
        out = build_wrapped_path("p/svc", cache_ttl="60s", cache_renew=True)
        assert out.startswith("m/p/svc?")
        assert "_ttl=60s" in out
        assert "_renew=" in out

    def test_failover_to_adds_f_prefix_and_else_query(self) -> None:
        out = build_wrapped_path("p/svc", failover_to="p/secondary")
        assert out == "f/p/svc?_else=p%2Fsecondary"

    def test_tee_to_adds_t_prefix_and_to_query(self) -> None:
        out = build_wrapped_path("p/svc", tee_to="p/audit")
        assert out == "t/p/svc?_to=p%2Faudit"

    def test_failover_to_rejects_external_url(self) -> None:
        with pytest.raises(ValueError, match="must be a gateway-relative path"):
            build_wrapped_path("p/svc", failover_to="https://evil.example.com/")

    def test_tee_to_rejects_external_url(self) -> None:
        with pytest.raises(ValueError, match="must be a gateway-relative path"):
            build_wrapped_path("p/svc", tee_to="http://attacker.test/")

    def test_all_four_compose(self) -> None:
        out = build_wrapped_path(
            "p/svc",
            log=True,
            cache_ttl="10m",
            failover_to="p/secondary",
            tee_to="p/audit",
        )
        # Prefix order is l → m → f → t regardless of insertion order
        # in the function. The gateway treats URL order as cosmetic,
        # so we just need ONE deterministic order from the SDK.
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
        # Customer hands in a path that already has primitives baked
        # in (e.g. from a previous helper or manual construction).
        # New kwargs prepend on top — the gateway flattens them at
        # request time.
        out = build_wrapped_path("l/p/svc", cache_ttl="5m")
        assert out == "m/l/p/svc?_ttl=5m"


# ----------------------------------------------------------------------
# has_wrappers
# ----------------------------------------------------------------------


class TestHasWrappers:
    def test_all_defaults_false(self) -> None:
        assert not has_wrappers(
            log=False,
            cache_ttl=None,
            cache_renew=False,
            failover_to=None,
            tee_to=None,
        )

    def test_any_single_wrapper_true(self) -> None:
        assert has_wrappers(log=True, cache_ttl=None, cache_renew=False, failover_to=None, tee_to=None)
        assert has_wrappers(log=False, cache_ttl="1h", cache_renew=False, failover_to=None, tee_to=None)
        assert has_wrappers(log=False, cache_ttl=None, cache_renew=True, failover_to=None, tee_to=None)
        assert has_wrappers(log=False, cache_ttl=None, cache_renew=False, failover_to="p/x", tee_to=None)
        assert has_wrappers(log=False, cache_ttl=None, cache_renew=False, failover_to=None, tee_to="p/y")


# ----------------------------------------------------------------------
# apply_wrappers
# ----------------------------------------------------------------------


class TestApplyWrappers:
    def test_fast_path_returns_unchanged_when_no_wrappers(self) -> None:
        base, path = apply_wrappers(
            "https://api.unitysvc.com/p/svc-id",
            "v1/chat",
        )
        # Returned values are byte-identical to the inputs (no parse
        # overhead on the hot path).
        assert base == "https://api.unitysvc.com/p/svc-id"
        assert path == "v1/chat"

    def test_splits_full_url_when_wrappers_present(self) -> None:
        base, path = apply_wrappers(
            "https://api.unitysvc.com/p/svc-id",
            "v1/chat/completions",
            log=True,
        )
        assert base == "https://api.unitysvc.com"
        # The host-portion of base_url becomes the gateway root; the
        # path-portion gets the wrapper segment prepended.
        assert path == "l/p/svc-id/v1/chat/completions"

    def test_handles_empty_path_argument(self) -> None:
        base, path = apply_wrappers(
            "https://api.unitysvc.com/p/svc-id",
            "",
            log=True,
        )
        assert base == "https://api.unitysvc.com"
        assert path == "l/p/svc-id"

    def test_handles_root_base_url_and_path_only(self) -> None:
        # The shape used by ``Client.dispatch`` — base_url is just the
        # gateway root, path carries the routing primitive.
        base, path = apply_wrappers(
            "https://api.unitysvc.com",
            "p/svc-id",
            log=True,
        )
        assert base == "https://api.unitysvc.com"
        assert path == "l/p/svc-id"

    def test_preserves_port_in_gateway_root(self) -> None:
        base, _ = apply_wrappers(
            "http://localhost:9080/p/svc-id",
            "",
            log=True,
        )
        assert base == "http://localhost:9080"


# ----------------------------------------------------------------------
# Client.dispatch — gateway-base derivation + no-network construction
# ----------------------------------------------------------------------


class TestClientDispatchURLBuild:
    """Construction-level tests — no network. Use httpx's transport
    hook to capture the outgoing request URL and assert on it.
    """

    @staticmethod
    def _capture_url(client: Client, path: str, **wrapper_kwargs: object) -> str:
        """Drive ``client.dispatch`` through a mock httpx transport and
        return the URL the SDK would have hit.
        """
        import httpx

        captured: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            return httpx.Response(200, json={"ok": True})

        # The dispatch path uses the low-level client's httpx instance;
        # swap its transport so no network traffic occurs.
        httpx_client = client._client.get_httpx_client()
        httpx_client._transport = httpx.MockTransport(handler)

        client.dispatch(path, json={"hello": "world"}, **wrapper_kwargs)
        return captured["url"]

    def test_dispatch_derives_gateway_root_from_control_plane(self) -> None:
        with Client(
            api_key="svcpass_test",
            base_url="https://api.example.test/v1",
        ) as client:
            url = self._capture_url(client, "p/some-service-id")
            # /v1 suffix stripped → https://api.example.test, then the
            # customer-supplied path is appended.
            assert url == "https://api.example.test/p/some-service-id"

    def test_dispatch_uses_explicit_api_base_url_when_set(self) -> None:
        with Client(
            api_key="svcpass_test",
            base_url="https://api.example.test/v1",
            api_base_url="http://localhost:9080",
        ) as client:
            url = self._capture_url(client, "p/some-service-id")
            assert url == "http://localhost:9080/p/some-service-id"

    def test_dispatch_applies_wrapper_kwargs(self) -> None:
        with Client(
            api_key="svcpass_test",
            api_base_url="http://localhost:9080",
        ) as client:
            url = self._capture_url(
                client,
                "p/some-service-id",
                log=True,
                cache_ttl="1h",
            )
            assert url.startswith("http://localhost:9080/l/m/p/some-service-id?")
            assert "_ttl=1h" in url

    def test_dispatch_passes_customer_pre_built_path_through(self) -> None:
        # Customer's path already has primitives in it; no kwargs.
        with Client(
            api_key="svcpass_test",
            api_base_url="http://localhost:9080",
        ) as client:
            url = self._capture_url(client, "l/p/some-service-id?_complete")
            # apply_wrappers fast path returns path unchanged.
            assert url == "http://localhost:9080/l/p/some-service-id?_complete"

    def test_dispatch_rejects_external_secondary(self) -> None:
        with Client(
            api_key="svcpass_test",
            api_base_url="http://localhost:9080",
        ) as client:
            with pytest.raises(ValueError, match="must be a gateway-relative path"):
                client.dispatch("p/x", json={}, failover_to="https://evil.test/")
