from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.service_enrollment_status_enum import ServiceEnrollmentStatusEnum, check_service_enrollment_status_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_enrollment_parameters_type_0 import CustomerEnrollmentParametersType0
    from ..models.customer_enrollment_service_type_0 import CustomerEnrollmentServiceType0


T = TypeVar("T", bound="CustomerEnrollment")


@_attrs_define
class CustomerEnrollment:
    """Customer-visible enrollment record.

    ``parameters`` is always sanitized — keys matching common secret
    names (``api_key``, ``password``, ...) are returned as
    ``***masked***`` so the SDK never round-trips raw secrets.
    ``service`` and ``proxy_endpoint`` are present when the list/get
    endpoint is called with ``include_service_details=True`` (the
    default).

    """

    id: UUID
    service_id: UUID
    status: ServiceEnrollmentStatusEnum
    """ Status of a customer's service enrollment.

    Workflow for services requiring parameters (user_parameters_schema exists):

        [not enrolled] → (enroll) → pending → (task completes) → incomplete → (configure) → active
                              │                                                                ↓
                              │                                  paused ← (pause) ←───────────┘
                              │
                              └─→ active  (if required secret already exists)

    Workflow for services without parameters:

        [not enrolled] → (enroll) → pending → (task completes) → active
                                                                    ↓
                                      paused ← (pause) ←──────────┘

    States:
    - pending: Celery task is processing (transient, show spinner)
    - incomplete: Needs user configuration (required parameters not provided)
    - active: Enrolled and fully configured
    - paused: Enrolled but temporarily disabled
    - cancelled: Enrollment cancelled

    Secrets do not affect enrollment status — they are resolved at routing time. """
    created_at: datetime.datetime
    parameters: CustomerEnrollmentParametersType0 | None | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    service: CustomerEnrollmentServiceType0 | None | Unset = UNSET
    proxy_endpoint: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_enrollment_parameters_type_0 import CustomerEnrollmentParametersType0
        from ..models.customer_enrollment_service_type_0 import CustomerEnrollmentServiceType0

        id = str(self.id)

        service_id = str(self.service_id)

        status: str = self.status

        created_at = self.created_at.isoformat()

        parameters: dict[str, Any] | None | Unset
        if isinstance(self.parameters, Unset):
            parameters = UNSET
        elif isinstance(self.parameters, CustomerEnrollmentParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        service: dict[str, Any] | None | Unset
        if isinstance(self.service, Unset):
            service = UNSET
        elif isinstance(self.service, CustomerEnrollmentServiceType0):
            service = self.service.to_dict()
        else:
            service = self.service

        proxy_endpoint: None | str | Unset
        if isinstance(self.proxy_endpoint, Unset):
            proxy_endpoint = UNSET
        else:
            proxy_endpoint = self.proxy_endpoint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "service_id": service_id,
                "status": status,
                "created_at": created_at,
            }
        )
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if service is not UNSET:
            field_dict["service"] = service
        if proxy_endpoint is not UNSET:
            field_dict["proxy_endpoint"] = proxy_endpoint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_enrollment_parameters_type_0 import CustomerEnrollmentParametersType0
        from ..models.customer_enrollment_service_type_0 import CustomerEnrollmentServiceType0

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        service_id = UUID(d.pop("service_id"))

        status = check_service_enrollment_status_enum(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_parameters(data: object) -> CustomerEnrollmentParametersType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = CustomerEnrollmentParametersType0.from_dict(data)

                return parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerEnrollmentParametersType0 | None | Unset, data)

        parameters = _parse_parameters(d.pop("parameters", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        def _parse_service(data: object) -> CustomerEnrollmentServiceType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                service_type_0 = CustomerEnrollmentServiceType0.from_dict(data)

                return service_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerEnrollmentServiceType0 | None | Unset, data)

        service = _parse_service(d.pop("service", UNSET))

        def _parse_proxy_endpoint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        proxy_endpoint = _parse_proxy_endpoint(d.pop("proxy_endpoint", UNSET))

        customer_enrollment = cls(
            id=id,
            service_id=service_id,
            status=status,
            created_at=created_at,
            parameters=parameters,
            updated_at=updated_at,
            service=service,
            proxy_endpoint=proxy_endpoint,
        )

        customer_enrollment.additional_properties = d
        return customer_enrollment

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
