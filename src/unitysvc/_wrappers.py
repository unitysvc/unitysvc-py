"""Helpers for the gateway-native wrapper primitives (#1129, #1135).

Six URL-prefix wrappers compose freely at the front of any gateway path:

``/l/`` log
    Per-call request-log capture. ``log=True`` → ``/l/``;
    ``log="complete"`` → ``/l/?_complete`` (full request/response with
    S3 overflow for bodies > 8 KB).

``/m/`` memoize
    Customer-scoped Redis cache. ``cached(ttl="1h")`` → ``/m/?_ttl=1h``;
    ``renew=True`` adds ``?_renew`` to force a fresh upstream call.
    Default TTL 1h; max 7d.

``/f/`` failover
    On primary 5xx / 429 / timeout, retry the secondary.
    ``with_failover(secondary)`` → ``/f/?_else=<secondary.path>``.

``/t/`` tee
    Fire-and-forget copy to a secondary listing.
    ``with_tee(secondary)`` → ``/t/?_to=<secondary.path>``.

``/d/`` delayed *(gateway-side pending)*
    Schedule a one-shot future firing.

``/r/`` recurrent *(gateway-side pending)*
    Schedule a recurring firing.

This module exposes the fluent API and the underlying string helpers
that both build it and the customer escape hatch (`client.dispatch`).

Fluent API entry points:

- :class:`_Wrappable` — mixin providing the wrapper builder methods.
  Mixed into Service, Group, and (via inheritance) WrappedTarget.
  Any class with a ``path`` property + ``_get_client()`` becomes
  composable.
- :class:`WrappedTarget` — the return type of every wrapper builder
  method. Holds a gateway path with one or more wrappers applied;
  supports chaining (same wrapper methods on it) and direct dispatch.

Underlying string helpers (used by the fluent API and exposed for
power users who want to construct paths themselves):

- :func:`build_wrapped_path` — pure string transformation: take a
  base path and wrapper config, return the wrapped path.
- :func:`_check_relative` — validator rejecting external URLs in
  secondary-path values.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import urlencode

if TYPE_CHECKING:
    import httpx

    from .client import Client

LogValue = bool | Literal["complete"]


def _check_relative(value: str, kwarg_name: str) -> None:
    """Reject external URLs in secondary-path kwargs at SDK call time.

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
    cache: bool = False,
    cache_ttl: str | None = None,
    cache_renew: bool = False,
    failover_to: str | None = None,
    tee_to: str | None = None,
) -> str:
    """Prepend wrapper segments + append wrapper-controlled query params.

    Returns the input unchanged when no wrapper config is set, so
    callers can blindly pass through without checking. Wrappers are
    emitted in ``l m f t`` order — but the gateway treats URL order
    as cosmetic, so a customer chaining ``svc.cached().logged()``
    sees the SAME on-wire behaviour as ``svc.logged().cached()``.
    The internal canonical form is deterministic, which makes path
    comparison stable across the SDK.

    ``cache=True`` triggers the ``/m/`` prefix even when no TTL is
    set (gateway uses its default). ``cache_ttl`` / ``cache_renew``
    also imply the prefix.
    """
    prefix_parts: list[str] = []
    query: dict[str, str] = {}
    if log:
        prefix_parts.append("l")
        if log == "complete":
            # Presence-only convention: ``?_complete`` with empty value.
            query["_complete"] = ""
    if cache or cache_ttl is not None or cache_renew:
        prefix_parts.append("m")
        if cache_ttl is not None:
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
        path = f"{path}?{urlencode(query)}"
    return path


class _Wrappable:
    """Mixin that gives a resource the fluent wrapper-builder methods.

    Implementing classes (Service, Group, WrappedTarget, future
    Alias/Broadcast/Chain active records) must provide:

    - ``path`` — the gateway-relative path representing this resource
      (no leading slash, no scheme). For Service that's ``"p/<id>"``;
      for Alias ``"a/<id>"``; for WrappedTarget the stored wrapped
      string.
    - ``_get_client()`` — return the :class:`Client` instance used to
      construct WrappedTarget children and to dispatch.

    The wrapper-builder methods (:meth:`logged`, :meth:`cached`,
    :meth:`with_failover`, :meth:`with_tee`, :meth:`delayed`,
    :meth:`recurrent`) all return :class:`WrappedTarget`, so chaining
    is unbounded:

        svc.cached(ttl="1h").logged().with_failover(backup).dispatch(json=body)

    ``with_failover`` and ``with_tee`` accept any :class:`_Wrappable`
    as the secondary — Service, Alias, Group, Broadcast, Chain, or
    another WrappedTarget — so customers compose across resource
    types without thinking about URL syntax.
    """

    # Subclasses implement these two.
    @property
    def path(self) -> str:
        raise NotImplementedError

    def _get_client(self) -> Client:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Wrapper builders — each returns a new WrappedTarget
    # ------------------------------------------------------------------
    def logged(self, *, complete: bool = False) -> WrappedTarget:
        """Wrap the call in ``/l/`` request-log capture.

        ``complete=True`` escalates to full request/response capture
        with S3 overflow for bodies > 8 KB.
        """
        log_value: LogValue = "complete" if complete else True
        return WrappedTarget(
            build_wrapped_path(self.path, log=log_value),
            self._get_client(),
        )

    def cached(self, *, ttl: str | None = None, renew: bool = False) -> WrappedTarget:
        """Wrap the call in ``/m/`` Redis-backed memoization.

        ``ttl`` accepts the gateway's duration syntax (``"60s"``,
        ``"5m"``, ``"1h"``, ``"1d"``). Defaults to 1 h on the gateway
        if omitted; max 7 d.

        ``renew=True`` forces a fresh upstream call and overwrites any
        cached entry.
        """
        return WrappedTarget(
            build_wrapped_path(
                self.path,
                cache=True,
                cache_ttl=ttl,
                cache_renew=renew,
            ),
            self._get_client(),
        )

    def with_failover(self, secondary: _Wrappable) -> WrappedTarget:
        """Wrap the call in ``/f/`` failover to ``secondary``.

        On primary 5xx / 429 / timeout, the gateway retries the
        secondary's path. ``secondary`` is any :class:`_Wrappable` —
        another Service, Alias, Group, Broadcast, Chain, or
        WrappedTarget (compose secondaries with wrappers of their
        own: ``svc.with_failover(other.cached(ttl="1h"))``).
        """
        return WrappedTarget(
            build_wrapped_path(self.path, failover_to=secondary.path),
            self._get_client(),
        )

    def with_tee(self, secondary: _Wrappable) -> WrappedTarget:
        """Wrap the call in ``/t/`` fire-and-forget tee.

        The primary's response is returned transparently to the
        customer; the secondary fires asynchronously and its outcome
        is discarded (the audit row in ``request_logs`` survives).
        ``secondary`` is any :class:`_Wrappable`.
        """
        return WrappedTarget(
            build_wrapped_path(self.path, tee_to=secondary.path),
            self._get_client(),
        )

    def delayed(
        self,
        *,
        at: str | None = None,
        in_: str | None = None,
    ) -> WrappedTarget:
        """Wrap the call in ``/d/`` (delayed / scheduled firing).

        Either ``at`` (absolute ISO-8601) or ``in_`` (duration like
        ``"5s"``) — not both. The gateway returns 202 + a schedule
        id; customers manage the schedule via the schedules
        namespace (when it lands).

        **Gateway-side support pending** (see unitysvc/unitysvc#1126).
        SDK constructs the path; calls fail until the gateway lands.
        """
        if (at is None) == (in_ is None):
            raise ValueError("delayed() requires exactly one of `at=<iso-8601>` or `in_=<duration>`")
        query: dict[str, str] = {}
        if at is not None:
            query["_at"] = at
        if in_ is not None:
            query["_in"] = in_
        path = "d/" + self.path.lstrip("/")
        if query:
            path = f"{path}?{urlencode(query)}"
        return WrappedTarget(path, self._get_client())

    def recurrent(self, *, every: str) -> WrappedTarget:
        """Wrap the call in ``/r/`` (recurrent firing).

        ``every`` is a duration (``"5m"``, ``"1h"``). The gateway
        executes inline once and registers the schedule; subsequent
        firings happen via the scheduled-task worker.

        **Gateway-side support pending** (see unitysvc/unitysvc#1125).
        SDK constructs the path; calls fail until the gateway lands.
        """
        path = "r/" + self.path.lstrip("/") + f"?_every={every}"
        return WrappedTarget(path, self._get_client())

    # ------------------------------------------------------------------
    # Dispatch — implemented by ``WrappedTarget`` (generic) and by
    # individual resource classes (Service, Group) with their own
    # routing nuances (interface selection, etc.).
    # ------------------------------------------------------------------


class WrappedTarget(_Wrappable):
    """A gateway-relative path with zero or more wrappers applied.

    Returned by every :class:`_Wrappable` wrapper-builder method.
    Two things you do with one:

    1. **Dispatch directly** — ``wrapped.dispatch(json=body)`` sends
       a request through the wrapper stack.
    2. **Hand to another resource** — ``alias.add_target(wrapped)``
       stores ``wrapped.path`` as the target's address. The wrapper
       primitives in the stored path fire on every invocation of
       the alias (gateway-side support tracked in
       unitysvc/unitysvc#1137).

    Same wrapper-builder methods on it as on bare resources, so
    customers chain freely: ``svc.cached(ttl="1h").logged()`` and
    ``svc.cached(ttl="1h").logged().with_failover(backup)`` are both
    valid.
    """

    __slots__ = ("_path", "_client")

    def __init__(self, path: str, client: Client) -> None:
        self._path = path
        self._client = client

    @property
    def path(self) -> str:
        return self._path

    def _get_client(self) -> Client:
        return self._client

    def __repr__(self) -> str:
        return f"<WrappedTarget path={self._path!r}>"

    def dispatch(
        self,
        *,
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send a request through this wrapped path.

        Generic dispatch — uses :meth:`Client.dispatch` directly with
        ``self.path``. For interface-aware dispatch on a Service
        (multi-enrollment selection), call ``Service.dispatch`` on
        the underlying Service instead.
        """
        return self._client.dispatch(
            self._path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )
