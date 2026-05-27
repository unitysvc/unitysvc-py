"""Helpers for the gateway-native wrapper primitives (#1129, #1135).

Four URL-prefix wrappers compose freely at the front of any gateway path:

``/l/`` log
    Per-call request-log capture. ``log=True`` → ``/l/``;
    ``log="complete"`` → ``/l/?_complete`` (full request/response with
    S3 overflow for bodies > 8 KB).

``/m/`` memoize
    Customer-scoped Redis cache. ``cache_ttl="1h"`` → ``/m/?_ttl=1h``;
    ``cache_renew=True`` adds ``?_renew`` to force a fresh upstream
    call. Default TTL 1h; max 7d.

``/f/`` failover
    On primary 5xx / 429 / timeout, retry the secondary.
    ``failover_to="p/<id>"`` → ``/f/?_else=p/<id>``. Secondary MUST be
    a gateway-relative path; external URLs raise ``ValueError``.

``/t/`` tee
    Fire-and-forget copy to a secondary listing. ``tee_to="p/<id>"`` →
    ``/t/?_to=p/<id>``. Same relative-path constraint as ``/f/``.

URL order has no semantic effect — the gateway applies wrappers at
fixed pipeline phases. Stacking is unlimited; we always emit them in
``l m f t`` order for predictable URLs but the customer's order in the
URL doesn't change behavior either.

This module exposes two helpers:

- :func:`build_wrapped_path` — pure string transformation; takes a
  base gateway path and the wrapper kwargs, returns the wrapped path
  (prefix + query). No URL parsing.
- :func:`apply_wrappers` — convenience for SDK call sites that hold a
  full URL (``https://api.unitysvc.com/p/<id>``) and want to inject
  wrapper segments between the host and the path. Returns
  ``(gateway_root, wrapped_path)`` ready to feed to ``_http_dispatch``.
"""

from __future__ import annotations

from typing import Any, Literal
from urllib.parse import urlencode, urlparse

# Type alias for the ``log`` kwarg's domain.
LogValue = bool | Literal["complete"]


def _check_relative(value: str, kwarg_name: str) -> None:
    """Reject external URLs in ``failover_to`` / ``tee_to`` at SDK call time.

    Same constraint the gateway enforces — secondaries must be
    gateway-relative paths so billing, auth, and composition all work.
    External destinations wrap in an http-relay listing. Surfacing the
    error here means customers see ``ValueError`` before the request
    ships, not a 400 from the gateway after.
    """
    if "://" in value:
        raise ValueError(
            f"{kwarg_name}={value!r} must be a gateway-relative path "
            f"(e.g. 'p/<service-id>'), not an external URL. Wrap external "
            f"URLs in an http-relay listing."
        )


def build_wrapped_path(
    base_path: str,
    *,
    log: LogValue = False,
    cache_ttl: str | None = None,
    cache_renew: bool = False,
    failover_to: str | None = None,
    tee_to: str | None = None,
) -> str:
    """Prepend wrapper segments + append wrapper-controlled query params.

    Returns the input unchanged when no wrapper kwargs are set, so
    callers can blindly pass through without checking. Wrappers are
    emitted in ``l m f t`` order — but URL order has no semantic
    effect at the gateway, so callers stacking their own primitives
    on top (``base_path="l/p/foo"``) just get more layers prepended.
    """
    prefix_parts: list[str] = []
    query: dict[str, str] = {}
    if log:
        prefix_parts.append("l")
        if log == "complete":
            # Presence-only convention: ``?_complete`` with empty value.
            query["_complete"] = ""
    if cache_ttl is not None:
        prefix_parts.append("m")
        query["_ttl"] = cache_ttl
        if cache_renew:
            query["_renew"] = ""
    if failover_to is not None:
        _check_relative(failover_to, "failover_to")
        prefix_parts.append("f")
        query["_else"] = failover_to
    if tee_to is not None:
        _check_relative(tee_to, "tee_to")
        prefix_parts.append("t")
        query["_to"] = tee_to

    path = base_path.lstrip("/")
    if prefix_parts:
        path = "/".join(prefix_parts) + ("/" + path if path else "/")
    if query:
        # urlencode("_complete=") produces "_complete=" which the
        # gateway treats as presence (any non-nil value is enough).
        path = f"{path}?{urlencode(query)}"
    return path


def has_wrappers(
    *,
    log: LogValue,
    cache_ttl: str | None,
    cache_renew: bool,
    failover_to: str | None,
    tee_to: str | None,
) -> bool:
    """``True`` iff any wrapper kwarg is set to a non-default value."""
    return bool(log) or cache_ttl is not None or cache_renew or failover_to is not None or tee_to is not None


def apply_wrappers(
    base_url: str,
    path: str,
    *,
    log: LogValue = False,
    cache_ttl: str | None = None,
    cache_renew: bool = False,
    failover_to: str | None = None,
    tee_to: str | None = None,
) -> tuple[str, str]:
    """Split a full gateway URL + optional sub-path; apply wrappers.

    Used by ``services.dispatch`` / ``groups.dispatch`` where
    ``base_url`` is the resolved interface URL (e.g.,
    ``https://api.unitysvc.com/p/<id>``) and ``path`` is an optional
    sub-path. Wrapper segments need to land between the host and the
    ``p/<id>`` portion; this helper does the parse, applies the
    transformation, and returns ``(gateway_root, wrapped_path)`` ready
    to feed back through ``_http_dispatch``.

    Fast path: when no wrapper kwargs are set, returns
    ``(base_url, path)`` unchanged so the call site doesn't pay for a
    URL parse on every dispatch.
    """
    if not has_wrappers(
        log=log,
        cache_ttl=cache_ttl,
        cache_renew=cache_renew,
        failover_to=failover_to,
        tee_to=tee_to,
    ):
        return base_url, path

    parsed = urlparse(base_url)
    gateway_root = f"{parsed.scheme}://{parsed.netloc}"
    base_path = parsed.path.lstrip("/")
    if path:
        if base_path:
            base_path = f"{base_path.rstrip('/')}/{path.lstrip('/')}"
        else:
            base_path = path.lstrip("/")
    wrapped = build_wrapped_path(
        base_path,
        log=log,
        cache_ttl=cache_ttl,
        cache_renew=cache_renew,
        failover_to=failover_to,
        tee_to=tee_to,
    )
    return gateway_root, wrapped


# Common kwarg signature exported so callers can re-type their
# dispatch methods without duplicating annotations.
_WRAPPER_KWARGS_DOC = """\
log: Per-call request-log opt-in. ``True`` → ``/l/`` (force-log this
    request); ``"complete"`` → ``/l/?_complete`` (full body capture
    with S3 overflow for bodies > 8 KB). Default ``False`` (no wrap).
cache_ttl: TTL for the ``/m/`` memoize wrapper, e.g. ``"60s"``,
    ``"5m"``, ``"1h"``, ``"1d"``. ``None`` (default) disables caching.
    Max 7d enforced by the gateway.
cache_renew: When ``True``, ``/m/`` forces a fresh upstream call and
    overwrites any cached entry. No effect when ``cache_ttl`` is not
    set.
failover_to: Gateway-relative secondary path (e.g.
    ``"p/<service-id>"``) for the ``/f/`` failover wrapper. On
    primary 5xx / 429 / timeout the gateway retries this path and
    returns its response. External URLs raise ``ValueError``.
tee_to: Gateway-relative secondary path for ``/t/`` fire-and-forget
    tee. The primary's response is returned transparently; the
    secondary fires asynchronously via ngx.timer.at. External URLs
    raise ``ValueError``.
"""


# Helper for type-stub generation / introspection; not part of the
# public API.
def _wrapper_kwargs_for(_obj: Any) -> dict[str, Any]:
    return {
        "log": False,
        "cache_ttl": None,
        "cache_renew": False,
        "failover_to": None,
        "tee_to": None,
    }
