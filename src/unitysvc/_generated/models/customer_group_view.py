from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerGroupView")


@_attrs_define
class CustomerGroupView:
    """Unified shape for the merged /customer/groups list — either a read-only
    platform ServiceGroup or the customer's own editable ServiceCollection.

    """

    id: UUID
    name: str
    owner_type: str
    editable: bool
    display_name: None | str | Unset = UNSET
    member_count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        owner_type = self.owner_type

        editable = self.editable

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        member_count = self.member_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "owner_type": owner_type,
                "editable": editable,
            }
        )
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if member_count is not UNSET:
            field_dict["member_count"] = member_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        owner_type = d.pop("owner_type")

        editable = d.pop("editable")

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        member_count = d.pop("member_count", UNSET)

        customer_group_view = cls(
            id=id,
            name=name,
            owner_type=owner_type,
            editable=editable,
            display_name=display_name,
            member_count=member_count,
        )

        customer_group_view.additional_properties = d
        return customer_group_view

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
