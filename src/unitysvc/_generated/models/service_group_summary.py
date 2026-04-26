from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_type_enum import GroupTypeEnum, check_group_type_enum
from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceGroupSummary")


@_attrs_define
class ServiceGroupSummary:
    """Customer-visible service group summary.

    Identified by ``name`` rather than UUID — group UUIDs change when
    admins recreate a group, so SDK scripts that hardcode UUIDs break
    silently after a recreation. Names survive because admins reuse
    the same slug.

    Excludes internal platform configuration (``membership_rules``,
    ``routing_policy``, ``user_access_interfaces``) — customers only
    need the resolved ``base_url`` for gateway dispatch, not the raw
    interface config.

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
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        display_name = self.display_name

        group_type: str = self.group_type

        service_count = self.service_count

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        service_group_summary = cls(
            name=name,
            display_name=display_name,
            group_type=group_type,
            service_count=service_count,
            description=description,
        )

        service_group_summary.additional_properties = d
        return service_group_summary

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
