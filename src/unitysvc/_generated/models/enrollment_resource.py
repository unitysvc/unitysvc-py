from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.details import Details


T = TypeVar("T", bound="EnrollmentResource")


@_attrs_define
class EnrollmentResource:
    """A resource the platform provisioned for the enrollment from its approved
    policy (#2830). ``object`` says which: ``resource:room`` (a room of ``kind``;
    an enrollment may have several: the customer's own, the seller's it admits
    the customer to, one the service's customers share, #2969) or
    ``resource:container`` (the enrollment's compute instance). What is
    particular to the kind is in ``details``.

    """

    object_: str
    resource_id: UUID
    kind: str
    name: str | Unset = ""
    open_: bool | Unset = True
    url: str | Unset = ""
    details: Details | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        object_ = self.object_

        resource_id = str(self.resource_id)

        kind = self.kind

        name = self.name

        open_ = self.open_

        url = self.url

        details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "resource_id": resource_id,
                "kind": kind,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if open_ is not UNSET:
            field_dict["open"] = open_
        if url is not UNSET:
            field_dict["url"] = url
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.details import Details

        d = dict(src_dict)
        object_ = d.pop("object")

        resource_id = UUID(d.pop("resource_id"))

        kind = d.pop("kind")

        name = d.pop("name", UNSET)

        open_ = d.pop("open", UNSET)

        url = d.pop("url", UNSET)

        _details = d.pop("details", UNSET)
        details: Details | Unset
        if isinstance(_details, Unset):
            details = UNSET
        else:
            details = Details.from_dict(_details)

        enrollment_resource = cls(
            object_=object_,
            resource_id=resource_id,
            kind=kind,
            name=name,
            open_=open_,
            url=url,
            details=details,
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
