from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_type_enum import GroupTypeEnum, check_group_type_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_interface import AccessInterface
    from ..models.customer_group_detail_routing_policy_type_0 import CustomerGroupDetailRoutingPolicyType0


T = TypeVar("T", bound="CustomerGroupDetail")


@_attrs_define
class CustomerGroupDetail:
    """Unified detail shape for a single group from /customer/groups — a
    read-only platform group or the customer's own editable collection.
    Same fields for both; type-specific fields are null for the other type.

    """

    id: UUID
    name: str
    owner_type: str
    editable: bool
    display_name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    member_count: int | Unset = 0
    group_type: GroupTypeEnum | None | Unset = UNSET
    interface: AccessInterface | None | Unset = UNSET
    routing_policy: CustomerGroupDetailRoutingPolicyType0 | None | Unset = UNSET
    enabled: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_interface import AccessInterface
        from ..models.customer_group_detail_routing_policy_type_0 import CustomerGroupDetailRoutingPolicyType0

        id = str(self.id)

        name = self.name

        owner_type = self.owner_type

        editable = self.editable

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        member_count = self.member_count

        group_type: None | str | Unset
        if isinstance(self.group_type, Unset):
            group_type = UNSET
        elif isinstance(self.group_type, str):
            group_type = self.group_type
        else:
            group_type = self.group_type

        interface: dict[str, Any] | None | Unset
        if isinstance(self.interface, Unset):
            interface = UNSET
        elif isinstance(self.interface, AccessInterface):
            interface = self.interface.to_dict()
        else:
            interface = self.interface

        routing_policy: dict[str, Any] | None | Unset
        if isinstance(self.routing_policy, Unset):
            routing_policy = UNSET
        elif isinstance(self.routing_policy, CustomerGroupDetailRoutingPolicyType0):
            routing_policy = self.routing_policy.to_dict()
        else:
            routing_policy = self.routing_policy

        enabled: bool | None | Unset
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

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
        if description is not UNSET:
            field_dict["description"] = description
        if member_count is not UNSET:
            field_dict["member_count"] = member_count
        if group_type is not UNSET:
            field_dict["group_type"] = group_type
        if interface is not UNSET:
            field_dict["interface"] = interface
        if routing_policy is not UNSET:
            field_dict["routing_policy"] = routing_policy
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_interface import AccessInterface
        from ..models.customer_group_detail_routing_policy_type_0 import CustomerGroupDetailRoutingPolicyType0

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

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        member_count = d.pop("member_count", UNSET)

        def _parse_group_type(data: object) -> GroupTypeEnum | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                group_type_type_0 = check_group_type_enum(data)

                return group_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GroupTypeEnum | None | Unset, data)

        group_type = _parse_group_type(d.pop("group_type", UNSET))

        def _parse_interface(data: object) -> AccessInterface | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                interface_type_0 = AccessInterface.from_dict(data)

                return interface_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AccessInterface | None | Unset, data)

        interface = _parse_interface(d.pop("interface", UNSET))

        def _parse_routing_policy(data: object) -> CustomerGroupDetailRoutingPolicyType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_policy_type_0 = CustomerGroupDetailRoutingPolicyType0.from_dict(data)

                return routing_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerGroupDetailRoutingPolicyType0 | None | Unset, data)

        routing_policy = _parse_routing_policy(d.pop("routing_policy", UNSET))

        def _parse_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        customer_group_detail = cls(
            id=id,
            name=name,
            owner_type=owner_type,
            editable=editable,
            display_name=display_name,
            description=description,
            member_count=member_count,
            group_type=group_type,
            interface=interface,
            routing_policy=routing_policy,
            enabled=enabled,
        )

        customer_group_detail.additional_properties = d
        return customer_group_detail

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
