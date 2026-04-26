from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_type_enum import GroupTypeEnum, check_group_type_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_interface import AccessInterface
    from ..models.service_group_detail_routing_policy_type_0 import ServiceGroupDetailRoutingPolicyType0


T = TypeVar("T", bound="ServiceGroupDetail")


@_attrs_define
class ServiceGroupDetail:
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

    ``routing_policy`` is exposed in full (not just the strategy
    name) because customers can configure it themselves via issue
    #857 — they need to read back the exact config they set.

    """

    name: str
    display_name: str
    group_type: GroupTypeEnum
    """ Type of service group — derived from configuration, not set directly.

    Derivation rules:
    - No rules, no access interfaces → category (organizes descendants)
    - Rules, no access interfaces → collection (curated set for browsing)
    - Rules + access interfaces → group (has own API endpoint + routing)
    - System-generated catch-all → misc """
    service_count: int
    description: None | str | Unset = UNSET
    interface: AccessInterface | None | Unset = UNSET
    routing_policy: None | ServiceGroupDetailRoutingPolicyType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_interface import AccessInterface
        from ..models.service_group_detail_routing_policy_type_0 import ServiceGroupDetailRoutingPolicyType0

        name = self.name

        display_name = self.display_name

        group_type: str = self.group_type

        service_count = self.service_count

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

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
        elif isinstance(self.routing_policy, ServiceGroupDetailRoutingPolicyType0):
            routing_policy = self.routing_policy.to_dict()
        else:
            routing_policy = self.routing_policy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "display_name": display_name,
                "group_type": group_type,
                "service_count": service_count,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if interface is not UNSET:
            field_dict["interface"] = interface
        if routing_policy is not UNSET:
            field_dict["routing_policy"] = routing_policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_interface import AccessInterface
        from ..models.service_group_detail_routing_policy_type_0 import ServiceGroupDetailRoutingPolicyType0

        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        group_type = check_group_type_enum(d.pop("group_type"))

        service_count = d.pop("service_count")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

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

        def _parse_routing_policy(data: object) -> None | ServiceGroupDetailRoutingPolicyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_policy_type_0 = ServiceGroupDetailRoutingPolicyType0.from_dict(data)

                return routing_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupDetailRoutingPolicyType0 | Unset, data)

        routing_policy = _parse_routing_policy(d.pop("routing_policy", UNSET))

        service_group_detail = cls(
            name=name,
            display_name=display_name,
            group_type=group_type,
            service_count=service_count,
            description=description,
            interface=interface,
            routing_policy=routing_policy,
        )

        service_group_detail.additional_properties = d
        return service_group_detail

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
