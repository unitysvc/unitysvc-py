"""Async mirror of :mod:`unitysvc.services`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap
from ._streaming import AsyncStreamingResponse, build_stream_kwargs
from .agroups import _http_dispatch_async

if TYPE_CHECKING:
    import httpx

    from ._generated.client import AuthenticatedClient
    from ._generated.models.access_interface import AccessInterface
    from ._generated.models.recurrent_request_public import RecurrentRequestPublic
    from ._generated.models.service_detail import ServiceDetail
    from ._generated.models.service_summary import ServiceSummary
    from .aclient import AsyncClient
    from .aenrollments import AsyncEnrollment


class AsyncService:
    """Async active-record wrapper. See :class:`unitysvc.services.Service`."""

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: ServiceDetail | ServiceSummary, parent: AsyncClient) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        return f"<AsyncService id={raw.id!r} name={raw.name!r}>"

    async def interfaces(self) -> list[AccessInterface]:
        return await self._parent.services.interfaces(self._raw.id)

    async def dispatch(
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
        return await self._parent.services.dispatch(
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

    async def stream(
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
    ) -> AsyncStreamingResponse:
        """See :meth:`AsyncServices.stream`."""
        return await self._parent.services.stream(
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

    async def schedule(
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
        return await self._parent.services.schedule(
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

    async def enroll(
        self, *, parameters: dict[str, Any] | None = None
    ) -> AsyncEnrollment:
        """Enroll in this service. See :meth:`unitysvc.services.Service.enroll`."""
        return await self._parent.enrollments.create(
            service_id=self._raw.id, parameters=parameters
        )

    async def required_secrets(
        self, *, interface: str | UUID | None = None
    ) -> list[str]:
        """See :meth:`unitysvc.services.Service.required_secrets`."""
        iface = await self._parent.services._pick_interface(
            self._raw.id, interface=interface, enrollment=None
        )
        return list(iface.customer_secrets_needed or [])

    async def optional_secrets(
        self, *, interface: str | UUID | None = None
    ) -> list[Any]:
        """See :meth:`unitysvc.services.Service.optional_secrets`."""
        iface = await self._parent.services._pick_interface(
            self._raw.id, interface=interface, enrollment=None
        )
        return list(iface.customer_secrets_optional or [])


class AsyncServices:
    """Async operations on customer-visible services."""

    def __init__(self, client: AuthenticatedClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def get(self, service_id: str | UUID) -> AsyncService:
        from ._generated.api.customer_services import customer_services_get_service

        raw = unwrap(
            await customer_services_get_service.asyncio_detailed(
                service_id=UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id,
                client=self._client,
            )
        )
        return AsyncService(raw, parent=self._parent)

    async def interfaces(self, service_id: str | UUID) -> list[AccessInterface]:
        from ._generated.api.customer_services import (
            customer_services_list_service_interfaces,
        )

        return unwrap(
            await customer_services_list_service_interfaces.asyncio_detailed(
                service_id=UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id,
                client=self._client,
            )
        )

    async def dispatch(
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
        iface = await self._pick_interface(service_id, interface=interface, enrollment=enrollment)
        base_url = iface.base_url if isinstance(iface.base_url, str) else None
        return await _http_dispatch_async(
            self._client,
            base_url=base_url,
            path=path,
            method=method,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    async def stream(
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
    ) -> AsyncStreamingResponse:
        """Async sibling of :meth:`unitysvc.services.Services.stream`.

        Usage::

            async with await aclient.services.stream(sid, json={...}) as r:
                async for event in r.iter_events():
                    ...
        """
        iface = await self._pick_interface(service_id, interface=interface, enrollment=enrollment)
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
        return AsyncStreamingResponse(self._client.get_async_httpx_client(), method, url, kwargs)

    async def schedule(
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
        from ._generated.api.customer_recurrent_requests import (
            customer_recurrent_requests_create_recurrent_request,
            customer_recurrent_requests_update_recurrent_request,
        )
        from ._generated.models.recurrent_request_create import RecurrentRequestCreate
        from ._generated.models.recurrent_request_create_body_template_type_0 import (
            RecurrentRequestCreateBodyTemplateType0,
        )
        from ._generated.models.recurrent_request_create_request_headers_type_0 import (
            RecurrentRequestCreateRequestHeadersType0,
        )
        from ._generated.models.recurrent_request_update import RecurrentRequestUpdate
        from ._generated.models.recurrent_request_update_schedule_type_0 import (
            RecurrentRequestUpdateScheduleType0,
        )
        from ._generated.types import UNSET

        iface = await self._pick_interface(service_id, interface=interface, enrollment=enrollment)
        iface_base_url = iface.base_url if isinstance(iface.base_url, str) else None
        if not iface_base_url:
            raise ValueError("Interface has no resolved base_url; cannot schedule.")
        request_path = iface_base_url.rstrip("/")
        if path:
            request_path = f"{request_path}/{path.lstrip('/')}"

        body_template = RecurrentRequestCreateBodyTemplateType0.from_dict(json) if isinstance(json, dict) else UNSET
        header_dict = RecurrentRequestCreateRequestHeadersType0.from_dict(headers) if headers else UNSET
        svc_uuid = UUID(str(service_id)) if not isinstance(service_id, UUID) else service_id
        enr_uuid = UUID(str(enrollment)) if enrollment is not None and not isinstance(enrollment, UUID) else enrollment
        created = unwrap(
            await customer_recurrent_requests_create_recurrent_request.asyncio_detailed(
                client=self._client,
                body=RecurrentRequestCreate(
                    request_path=request_path,
                    http_method=method,
                    service_id=svc_uuid,
                    enrollment_id=enr_uuid if enrollment is not None else UNSET,
                    body_template=body_template,  # type: ignore[arg-type]
                    request_headers=header_dict,  # type: ignore[arg-type]
                    name=name if name is not None else UNSET,
                ),
            )
        )
        schedule_obj = RecurrentRequestUpdateScheduleType0.from_dict(recurrence)
        return unwrap(
            await customer_recurrent_requests_update_recurrent_request.asyncio_detailed(
                request_id=created.id,
                client=self._client,
                body=RecurrentRequestUpdate(schedule=schedule_obj),  # type: ignore[arg-type]
            )
        )

    async def _pick_interface(
        self,
        service_id: str | UUID,
        *,
        interface: str | UUID | None,
        enrollment: str | UUID | None,
    ) -> AccessInterface:
        ifaces = await self.interfaces(service_id)
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
