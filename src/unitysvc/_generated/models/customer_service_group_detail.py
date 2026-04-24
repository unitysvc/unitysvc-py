from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_type_enum import GroupTypeEnum, check_group_type_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_access_interface import CustomerAccessInterface


T = TypeVar("T", bound="CustomerServiceGroupDetail")


@_attrs_define
class CustomerServiceGroupDetail:
    """Service group metadata with the (single) group-level interface.

    Groups declare at most one ``user_access_interfaces`` entry, so
    ``interface`` is embedded here directly rather than returned via a
    separate endpoint. The SDK reads ``grp.interface.base_url`` for
    ``group.dispatch(json=...)`` — an HTTP call to that base URL where
    the gateway's ``routing_policy`` picks a member service via
    weighted / content-dependent / price-based strategies. ``None`` if
    the group has no user-facing interface configured.

    Member services are fetched separately via
    ``GET /customer/groups/{id}/services`` so this response stays
    small for groups with many members.

    """

    id: UUID
    name: str
    display_name: str
    group_type: GroupTypeEnum
    """ Type of service group — derived from configuration, not set directly.

    Derivation rules:
    - No rules, no access interfaces → category (organizes descendants)
    - Rules, no access interfaces → collection (curated set for browsing)
    - Rules + access interfaces → group (has own API endpoint + routing)
    - System-generated catch-all → misc """
    ancestor_path: str
    sort_order: int
    service_count: int
    description: None | str | Unset = UNSET
    interface: CustomerAccessInterface | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_access_interface import CustomerAccessInterface

        id = str(self.id)

        name = self.name

        display_name = self.display_name

        group_type: str = self.group_type

        ancestor_path = self.ancestor_path

        sort_order = self.sort_order

        service_count = self.service_count

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        interface: dict[str, Any] | None | Unset
        if isinstance(self.interface, Unset):
            interface = UNSET
        elif isinstance(self.interface, CustomerAccessInterface):
            interface = self.interface.to_dict()
        else:
            interface = self.interface

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "display_name": display_name,
                "group_type": group_type,
                "ancestor_path": ancestor_path,
                "sort_order": sort_order,
                "service_count": service_count,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if interface is not UNSET:
            field_dict["interface"] = interface

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_access_interface import CustomerAccessInterface

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        display_name = d.pop("display_name")

        group_type = check_group_type_enum(d.pop("group_type"))

        ancestor_path = d.pop("ancestor_path")

        sort_order = d.pop("sort_order")

        service_count = d.pop("service_count")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_interface(data: object) -> CustomerAccessInterface | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                interface_type_0 = CustomerAccessInterface.from_dict(data)

                return interface_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerAccessInterface | None | Unset, data)

        interface = _parse_interface(d.pop("interface", UNSET))

        customer_service_group_detail = cls(
            id=id,
            name=name,
            display_name=display_name,
            group_type=group_type,
            ancestor_path=ancestor_path,
            sort_order=sort_order,
            service_count=service_count,
            description=description,
            interface=interface,
        )

        customer_service_group_detail.additional_properties = d
        return customer_service_group_detail

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
