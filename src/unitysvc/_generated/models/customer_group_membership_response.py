from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_group_membership_entry import CustomerGroupMembershipEntry


T = TypeVar("T", bound="CustomerGroupMembershipResponse")


@_attrs_define
class CustomerGroupMembershipResponse:
    """GET /customer/services/{service_id}/groups — the dropdown state."""

    service_id: UUID
    eligible: bool
    groups: list[CustomerGroupMembershipEntry]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_group_membership_entry import CustomerGroupMembershipEntry

        service_id = str(self.service_id)

        eligible = self.eligible

        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_id": service_id,
                "eligible": eligible,
                "groups": groups,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_group_membership_entry import CustomerGroupMembershipEntry

        d = dict(src_dict)
        service_id = UUID(d.pop("service_id"))

        eligible = d.pop("eligible")

        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = CustomerGroupMembershipEntry.from_dict(groups_item_data)

            groups.append(groups_item)

        customer_group_membership_response = cls(
            service_id=service_id,
            eligible=eligible,
            groups=groups,
        )

        customer_group_membership_response.additional_properties = d
        return customer_group_membership_response

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
