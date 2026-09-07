from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.broadcast_target_create_routing_key_override_type_0 import (
        BroadcastTargetCreateRoutingKeyOverrideType0,
    )


T = TypeVar("T", bound="BroadcastTargetCreate")


@_attrs_define
class BroadcastTargetCreate:
    name: str
    target_path: str
    routing_key_override: BroadcastTargetCreateRoutingKeyOverrideType0 | None | Unset = UNSET
    sort_order: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.broadcast_target_create_routing_key_override_type_0 import (
            BroadcastTargetCreateRoutingKeyOverrideType0,
        )

        name = self.name

        target_path = self.target_path

        routing_key_override: dict[str, Any] | None | Unset
        if isinstance(self.routing_key_override, Unset):
            routing_key_override = UNSET
        elif isinstance(self.routing_key_override, BroadcastTargetCreateRoutingKeyOverrideType0):
            routing_key_override = self.routing_key_override.to_dict()
        else:
            routing_key_override = self.routing_key_override

        sort_order = self.sort_order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "target_path": target_path,
            }
        )
        if routing_key_override is not UNSET:
            field_dict["routing_key_override"] = routing_key_override
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.broadcast_target_create_routing_key_override_type_0 import (
            BroadcastTargetCreateRoutingKeyOverrideType0,
        )

        d = dict(src_dict)
        name = d.pop("name")

        target_path = d.pop("target_path")

        def _parse_routing_key_override(data: object) -> BroadcastTargetCreateRoutingKeyOverrideType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_override_type_0 = BroadcastTargetCreateRoutingKeyOverrideType0.from_dict(data)

                return routing_key_override_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BroadcastTargetCreateRoutingKeyOverrideType0 | None | Unset, data)

        routing_key_override = _parse_routing_key_override(d.pop("routing_key_override", UNSET))

        sort_order = d.pop("sort_order", UNSET)

        broadcast_target_create = cls(
            name=name,
            target_path=target_path,
            routing_key_override=routing_key_override,
            sort_order=sort_order,
        )

        broadcast_target_create.additional_properties = d
        return broadcast_target_create

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
