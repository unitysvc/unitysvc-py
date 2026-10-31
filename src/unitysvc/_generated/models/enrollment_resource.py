from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EnrollmentResource")


@_attrs_define
class EnrollmentResource:
    """A resource the platform provisioned for the enrollment from its approved
    policy (#2830): for ``resource:room``, the room of that kind.

    """

    object_: str
    kind: str
    room_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        object_ = self.object_

        kind = self.kind

        room_id = str(self.room_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "kind": kind,
                "room_id": room_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        object_ = d.pop("object")

        kind = d.pop("kind")

        room_id = UUID(d.pop("room_id"))

        enrollment_resource = cls(
            object_=object_,
            kind=kind,
            room_id=room_id,
        )

        enrollment_resource.additional_properties = d
        return enrollment_resource

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
