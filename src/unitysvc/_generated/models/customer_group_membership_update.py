from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerGroupMembershipUpdate")


@_attrs_define
class CustomerGroupMembershipUpdate:
    """PUT body: the collections that should contain the service after
    save. ``group_ids`` are the customer's editable collections;
    ``include_default`` toggles the Favorites collection (created on
    first use).

    """

    group_ids: list[UUID] | Unset = UNSET
    include_default: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_ids: list[str] | Unset = UNSET
        if not isinstance(self.group_ids, Unset):
            group_ids = []
            for group_ids_item_data in self.group_ids:
                group_ids_item = str(group_ids_item_data)
                group_ids.append(group_ids_item)

        include_default = self.include_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if group_ids is not UNSET:
            field_dict["group_ids"] = group_ids
        if include_default is not UNSET:
            field_dict["include_default"] = include_default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _group_ids = d.pop("group_ids", UNSET)
        group_ids: list[UUID] | Unset = UNSET
        if _group_ids is not UNSET:
            group_ids = []
            for group_ids_item_data in _group_ids:
                group_ids_item = UUID(group_ids_item_data)

                group_ids.append(group_ids_item)

        include_default = d.pop("include_default", UNSET)

        customer_group_membership_update = cls(
            group_ids=group_ids,
            include_default=include_default,
        )

        customer_group_membership_update.additional_properties = d
        return customer_group_membership_update

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
