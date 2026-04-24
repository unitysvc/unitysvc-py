from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.service_enrollment_status_enum import ServiceEnrollmentStatusEnum, check_service_enrollment_status_enum
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerEnrollmentCreateResponse")


@_attrs_define
class CustomerEnrollmentCreateResponse:
    """Async enrollment ack. Poll the ``task_id`` via ``/tasks/{id}``
    to observe activation progress, or fetch the enrollment later
    to check its ``status``.

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
    task_id: str
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        service_id = str(self.service_id)

        status: str = self.status

        task_id = self.task_id

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "service_id": service_id,
                "status": status,
                "task_id": task_id,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        service_id = UUID(d.pop("service_id"))

        status = check_service_enrollment_status_enum(d.pop("status"))

        task_id = d.pop("task_id")

        message = d.pop("message")

        customer_enrollment_create_response = cls(
            id=id,
            service_id=service_id,
            status=status,
            task_id=task_id,
            message=message,
        )

        customer_enrollment_create_response.additional_properties = d
        return customer_enrollment_create_response

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
