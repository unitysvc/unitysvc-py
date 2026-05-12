"""``client.services`` — customer service browsing and dispatch.

Wraps the customer-tagged ``/v1/customer/services/*`` operations.
Service discovery flows through a group (``client.groups.services(name)``);
this resource handles per-service details, interfaces, dispatch,
enrollment, and schedule.

Dispatch and schedule share one interface-resolution rule:

- Multiple public (``enrollment_id IS NULL``) interfaces on a service
  all map to the same upstream, so the SDK auto-picks one — no
  ``interface=`` argument is needed in the common case.
- If the customer has exactly one enrollment-bound interface on the
  service, that one is preferred over public interfaces (the customer
  enrolled to use their own key/parameters).
- ``interface=`` is only required to disambiguate when the customer
  has 2+ enrollments on the service. ``enrollment=<Enrollment|uuid>``
  is an equivalent hint that picks by ``enrollment_id``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap
from ._streaming import StreamingResponse, build_stream_kwargs
from .groups import _http_dispatch

if TYPE_CHECKING:
    import httpx

    from ._generated.client import AuthenticatedClient
    from ._generated.models.access_interface import AccessInterface
    from ._generated.models.recurrent_request_public import RecurrentRequestPublic
    from ._generated.models.service_detail import ServiceDetail
    from ._generated.models.service_summary import ServiceSummary
    from .client import Client
    from .enrollments import Enrollment


class Service:
    """Active-record wrapper around a service.

    Forwards field access (``svc.id``, ``svc.name``,
    ``svc.display_name``, …) to the underlying generated record via
    ``__getattr__`` — every attribute exposed on
    :class:`ServiceDetail` / :class:`ServiceSummary` is available
    unchanged. Adds methods that delegate to the parent
    :class:`Client`:

    - :meth:`interfaces` — list access interfaces.
    - :meth:`dispatch` — send a one-shot request through the picked
      interface.
    - :meth:`schedule` — register a recurring dispatch.

    Returned by :meth:`Services.get` and as items inside the page
    returned by :meth:`Groups.services`.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: ServiceDetail | ServiceSummary, parent: Client) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<Service id={raw.id!r} name={raw.name!r}>"

    def interfaces(self) -> list[AccessInterface]:
        """List access interfaces for this service. See :meth:`Services.interfaces`."""
        return self._parent.services.interfaces(self._raw.id)

    def dispatch(
        self,
        *,
        interface: str | UUID | None = None,
        enrollment: str | UUID | None = None,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send a one-shot request. See :meth:`Services.dispatch`."""
        return self._parent.services.dispatch(
            self._raw.id,
            interface=interface,
            enrollment=enrollment,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    def stream(
        self,
        *,
        interface: str | UUID | None = None,
        enrollment: str | UUID | None = None,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StreamingResponse:
        """Open a streaming HTTP request. See :meth:`Services.stream`."""
        return self._parent.services.stream(
            self._raw.id,
            interface=interface,
            enrollment=enrollment,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    def schedule(
        self,
        *,
        recurrence: dict[str, Any],
        interface: str | UUID | None = None,
        enrollment: str | UUID | None = None,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        headers: dict[str, str] | None = None,
        name: str | None = None,
    ) -> RecurrentRequestPublic:
        """Register a recurring dispatch. See :meth:`Services.schedule`."""
        return self._parent.services.schedule(
            self._raw.id,
            recurrence=recurrence,
            interface=interface,
            enrollment=enrollment,
            path=path,
            method=method,
            json=json,
            headers=headers,
            name=name,
        )

    # ------------------------------------------------------------------
    # Enrollment shortcut + secrets introspection
    # ------------------------------------------------------------------
    def enroll(self, *, parameters: dict[str, Any] | None = None) -> Enrollment:
        """Enroll in this service. See :meth:`Enrollments.create`.

        Convenience that pre-binds ``service_id``. Returns an
        :class:`~unitysvc.enrollments.Enrollment` ready for
        ``.refresh()`` / ``.cancel()``.
        """
        return self._parent.enrollments.create(
            service_id=self._raw.id, parameters=parameters
        )

    def required_secrets(
        self, *, interface: str | UUID | None = None
    ) -> list[str]:
        """Customer secrets the picked interface requires for dispatch.

        These are secret *names* (e.g. ``"OPENAI_API_KEY"``) that must
        exist on the customer account before the service will route.
        Set them via ``client.secrets.set(name=..., value=...)``;
        unresolved required secrets cause dispatch to fail (or, on
        BYOK enrollment, activation to stall in ``incomplete``).

        With no arguments, picks the same interface
        :meth:`dispatch` would default to (auto-pick rule). Pass
        ``interface="<name>"`` to inspect a specific kind.
        """
        iface = self._parent.services._pick_interface(
            self._raw.id, interface=interface, enrollment=None
        )
        return list(iface.customer_secrets_needed or [])

    def optional_secrets(
        self, *, interface: str | UUID | None = None
    ) -> list[Any]:
        """Customer secrets the picked interface can use but doesn't require.

        Each entry is a ``{"name": str, "default": str}`` mapping —
        the gateway falls back to ``default`` when the customer
        hasn't set ``name``. See :meth:`required_secrets` for the
        interface-resolution rule.
        """
        iface = self._parent.services._pick_interface(
            self._raw.id, interface=interface, enrollment=None
        )
        return list(iface.customer_secrets_optional or [])


class Services:
    """Operations on customer-visible services (``/v1/customer/services``).

    Example::

        svc = client.services.get(service_id)
        ifaces = svc.interfaces()                   # active-record nav
        resp = svc.dispatch(json={"messages": [...]})

    The same operations are also available on the manager directly
    (``client.services.dispatch(service_id, …)``); :class:`Service`
    is just a convenience that pre-binds the id.
    """

    def __init__(self, client: AuthenticatedClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get(self, service_id: str | UUID) -> Service:
        """Get a single service by UUID (or partial UUID prefix).

        Returns ``404`` for inactive or non-public services — the
        customer-visible set matches what
        ``client.groups.services(name)`` returns.
        """
        from ._generated.api.customer_services import customer_services_get_service

        raw = unwrap(
            customer_services_get_service.sync_detailed(
                service_id=UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id,
                client=self._client,
            )
        )
        return Service(raw, parent=self._parent)

    def interfaces(self, service_id: str | UUID) -> list[AccessInterface]:
        """List access interfaces dispatchable by this customer.

        Returns shared interfaces plus any enrollment-bound interfaces
        owned by the calling customer. Each entry carries an optional
        ``enrollment_id`` — ``None`` for shared, set for BYOK/BYOE.
        """
        from ._generated.api.customer_services import (
            customer_services_list_service_interfaces,
        )

        return unwrap(
            customer_services_list_service_interfaces.sync_detailed(
                service_id=UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id,
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------
    def dispatch(
        self,
        service_id: str | UUID,
        *,
        interface: str | UUID | None = None,
        enrollment: str | UUID | None = None,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send an HTTP request to the service through its gateway interface.

        Resolves the target interface using :meth:`_pick_interface` and
        POSTs to its ``base_url`` using the client's svcpass API key.
        Upstream 4xx/5xx responses are returned as-is; the caller is
        responsible for inspecting ``.status_code``.

        Args:
            service_id: Service UUID.
            interface: Optional interface selector — name or UUID. Required
                if the service has more than one interface and no
                ``enrollment=`` hint picks one uniquely.
            enrollment: Optional enrollment hint. If set, picks the
                interface whose ``enrollment_id`` matches. Silently
                ignored when there is exactly one interface.
            path: Optional sub-path appended to the interface base URL.
            method: HTTP method. Defaults to ``POST``.
            json / data: Request body (mutually exclusive).
            headers: Extra headers merged on top of the auth header.
            timeout: Per-request timeout in seconds.
        """
        iface = self._pick_interface(service_id, interface=interface, enrollment=enrollment)
        base_url = iface.base_url if isinstance(iface.base_url, str) else None
        return _http_dispatch(
            self._client,
            base_url=base_url,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Stream
    # ------------------------------------------------------------------
    def stream(
        self,
        service_id: str | UUID,
        *,
        interface: str | UUID | None = None,
        enrollment: str | UUID | None = None,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StreamingResponse:
        """Open a streaming HTTP request through the resolved service interface.

        Sibling to :meth:`dispatch` — same interface resolution, auth,
        and URL composition; the difference is that the response body
        is consumed lazily via :class:`StreamingResponse`. Use for
        SSE / NDJSON / chunked LLM responses where buffering the full
        body before yielding chunks would defeat the streaming UX.

        The upstream-protocol ``stream`` flag (e.g. ``json={"stream": True}``
        for OpenAI-compatible APIs) is orthogonal — set it in the body
        if the upstream requires it. ``stream()`` controls only how
        the SDK consumes the response.

        Example::

            with client.services.stream(svc_id, json={..., "stream": True}) as r:
                print(r.status_code)
                for event in r.iter_events():
                    if event.kind == "done":
                        break
                    handle(event.parsed)

        Args: same as :meth:`dispatch`.

        Returns:
            A :class:`StreamingResponse` context manager.
        """
        iface = self._pick_interface(service_id, interface=interface, enrollment=enrollment)
        base_url = iface.base_url if isinstance(iface.base_url, str) else None
        url, kwargs = build_stream_kwargs(
            token=getattr(self._client, "token", None),
            base_url=base_url,
            path=path,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )
        return StreamingResponse(self._client.get_httpx_client(), method, url, kwargs)

    # ------------------------------------------------------------------
    # Schedule (recurrent dispatch)
    # ------------------------------------------------------------------
    def schedule(
        self,
        service_id: str | UUID,
        *,
        recurrence: dict[str, Any],
        interface: str | UUID | None = None,
        enrollment: str | UUID | None = None,
        path: str = "",
        method: str = "POST",
        json: Any = None,
        headers: dict[str, str] | None = None,
        name: str | None = None,
    ) -> RecurrentRequestPublic:
        """Schedule a recurring dispatch.

        Same interface-resolution rule as :meth:`dispatch`. Creates a
        :class:`~unitysvc._generated.models.recurrent_request_public.RecurrentRequestPublic`
        via ``POST /customer/recurrent-requests``. The server then
        fires the request on the given schedule (cron or fixed
        interval) against the resolved interface's gateway path.

        Args:
            service_id: Service UUID.
            recurrence: Schedule spec. One of::

                {"schedule_type": "interval", "interval_seconds": 300}
                {"schedule_type": "cron", "cron_expression": "*/5 * * * *",
                 "timezone": "UTC"}

            interface / enrollment / path / method / json / headers:
                Same as :meth:`dispatch` — resolve the target interface
                and compose the gateway URL.
            name: Optional human label for the recurrent request.
        """
        from ._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_create_recurrent_request,
        )
        from ._generated.models.recurrent_request_create import RecurrentRequestCreate
        from ._generated.models.recurrent_request_create_body_template_type_0 import (
            RecurrentRequestCreateBodyTemplateType0,
        )
        from ._generated.models.recurrent_request_create_request_headers_type_0 import (
            RecurrentRequestCreateRequestHeadersType0,
        )
        from ._generated.types import UNSET

        iface = self._pick_interface(service_id, interface=interface, enrollment=enrollment)
        iface_base_url = iface.base_url if isinstance(iface.base_url, str) else None
        if not iface_base_url:
            raise ValueError("Interface has no resolved base_url; cannot schedule.")

        # Derive the gateway request_path from the interface base_url +
        # optional suffix. The backend stores this verbatim and uses it
        # as the gateway-relative path on each tick.
        request_path = iface_base_url.rstrip("/")
        if path:
            request_path = f"{request_path}/{path.lstrip('/')}"

        body_template = RecurrentRequestCreateBodyTemplateType0.from_dict(json) if isinstance(json, dict) else UNSET
        header_dict = RecurrentRequestCreateRequestHeadersType0.from_dict(headers) if headers else UNSET

        svc_uuid = UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id
        enr_uuid = UUID(str(enrollment)) if enrollment is not None and not isinstance(enrollment, UUID) else enrollment

        create_body = RecurrentRequestCreate(
            request_path=request_path,
            http_method=method,
            service_id=svc_uuid,
            enrollment_id=enr_uuid if enrollment is not None else UNSET,
            body_template=body_template,  # type: ignore[arg-type]
            request_headers=header_dict,  # type: ignore[arg-type]
            name=name if name is not None else UNSET,
        )
        created = unwrap(
            customer_recurrent_requests_create_recurrent_request.sync_detailed(
                client=self._client,
                body=create_body,
            )
        )
        # Attach the schedule via PATCH — the create endpoint intentionally
        # leaves status=draft until a schedule is applied.
        from ._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_update_recurrent_request,
        )
        from ._generated.models.recurrent_request_update import RecurrentRequestUpdate
        from ._generated.models.recurrent_request_update_schedule_type_0 import (
            RecurrentRequestUpdateScheduleType0,
        )

        schedule_obj = RecurrentRequestUpdateScheduleType0.from_dict(recurrence)
        return unwrap(
            customer_recurrent_requests_update_recurrent_request.sync_detailed(
                request_id=created.id,
                client=self._client,
                body=RecurrentRequestUpdate(schedule=schedule_obj),  # type: ignore[arg-type]
            )
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _pick_interface(
        self,
        service_id: str | UUID,
        *,
        interface: str | UUID | None,
        enrollment: str | UUID | None,
    ) -> AccessInterface:
        """Resolve an interface selector to a ``AccessInterface``.

        Rules (in order):

        1. If ``interface=`` is set, match by name or UUID; raise
           ``ValueError`` on no match.
        2. If ``enrollment=`` is set, match by ``enrollment_id``;
           raise ``ValueError`` on no match.
        3. If the customer has exactly one enrollment-bound interface
           on this service, use it — multiple public interfaces all
           map to the same upstream, so the enrollment binding is the
           only decision worth making.
        4. If there are no enrollment-bound interfaces, pick the first
           public (``enrollment_id IS NULL``) interface. Multiple public
           interfaces on the same service map to the same upstream, so
           any one is fine; ``interface=`` can override.
        5. If there are 2+ enrollment-bound interfaces, raise — the
           caller must specify ``enrollment=`` (or ``interface=``).
        """
        ifaces = self.interfaces(service_id)
        if not ifaces:
            raise ValueError(f"Service {service_id!r} has no dispatchable interfaces.")

        if interface is not None:
            # AccessInterface is identified by name now (no UUID
            # surfaced on the customer schema).
            key = str(interface)
            for i in ifaces:
                if i.name == key:
                    return i
            names = ", ".join(repr(i.name) for i in ifaces)
            raise ValueError(f"No interface {interface!r} on service {service_id!r}. Available: {names}")

        if enrollment is not None:
            enr_key = str(enrollment)
            matches = [i for i in ifaces if i.enrollment_id is not None and str(i.enrollment_id) == enr_key]
            if not matches:
                raise ValueError(f"No interface bound to enrollment {enrollment!r} on service {service_id!r}.")
            if len(matches) > 1:
                raise ValueError(
                    f"Ambiguous: {len(matches)} interfaces bound to enrollment "
                    f"{enrollment!r} on service {service_id!r}."
                )
            return matches[0]

        bound = [i for i in ifaces if i.enrollment_id is not None]
        if len(bound) == 1:
            return bound[0]
        if len(bound) >= 2:
            raise ValueError(
                f"Service {service_id!r} has {len(bound)} enrollment-bound interfaces; "
                f"specify enrollment= or interface= to pick one."
            )
        return ifaces[0]
