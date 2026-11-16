from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnrollmentResource")


@_attrs_define
class EnrollmentResource:
    """A resource the platform provisioned for the enrollment from its approved
    policy (#2830): for ``resource:room``, a room of that kind. An enrollment
    may have several: the customer's own room, the seller's room it admits
    the customer to, a room the service's customers share (#2969).

    """

    object_: str
    kind: str
    room_id: UUID
    name: str | Unset = ""
    role: str | Unset = "owner"
    scope: str | Unset = "enrollment"
    open_: bool | Unset = True
    url: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        object_ = self.object_

        kind = self.kind

        room_id = str(self.room_id)

        name = self.name

        role = self.role

        scope = self.scope

        open_ = self.open_

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "kind": kind,
                "room_id": room_id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if role is not UNSET:
            field_dict["role"] = role
        if scope is not UNSET:
            field_dict["scope"] = scope
        if open_ is not UNSET:
            field_dict["open"] = open_
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        object_ = d.pop("object")

        kind = d.pop("kind")

        room_id = UUID(d.pop("room_id"))

        name = d.pop("name", UNSET)

        role = d.pop("role", UNSET)

        scope = d.pop("scope", UNSET)

        open_ = d.pop("open", UNSET)

        url = d.pop("url", UNSET)

        enrollment_resource = cls(
            object_=object_,
            kind=kind,
            room_id=room_id,
            name=name,
            role=role,
            scope=scope,
            open_=open_,
            url=url,
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
