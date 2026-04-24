from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.service_enrollment_status_enum import ServiceEnrollmentStatusEnum, check_service_enrollment_status_enum
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerEnrollmentCancelResponse")


@_attrs_define
class CustomerEnrollmentCancelResponse:
    """Response after cancelling (unenrolling from) an enrollment."""

    enrollment_id: UUID
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
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enrollment_id = str(self.enrollment_id)

        status: str = self.status

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enrollment_id": enrollment_id,
                "status": status,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enrollment_id = UUID(d.pop("enrollment_id"))

        status = check_service_enrollment_status_enum(d.pop("status"))

        message = d.pop("message")

        customer_enrollment_cancel_response = cls(
            enrollment_id=enrollment_id,
            status=status,
            message=message,
        )

        customer_enrollment_cancel_response.additional_properties = d
        return customer_enrollment_cancel_response

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
