from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.broadcast_target_public_routing_key_override_type_0 import (
        BroadcastTargetPublicRoutingKeyOverrideType0,
    )


T = TypeVar("T", bound="BroadcastTargetPublic")


@_attrs_define
class BroadcastTargetPublic:
    id: UUID
    broadcast_id: UUID
    name: str
    target_path: str
    sort_order: int
    routing_key_override: BroadcastTargetPublicRoutingKeyOverrideType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.broadcast_target_public_routing_key_override_type_0 import (
            BroadcastTargetPublicRoutingKeyOverrideType0,
        )

        id = str(self.id)

        broadcast_id = str(self.broadcast_id)

        name = self.name

        target_path = self.target_path

        sort_order = self.sort_order

        routing_key_override: dict[str, Any] | None | Unset
        if isinstance(self.routing_key_override, Unset):
            routing_key_override = UNSET
        elif isinstance(self.routing_key_override, BroadcastTargetPublicRoutingKeyOverrideType0):
            routing_key_override = self.routing_key_override.to_dict()
        else:
            routing_key_override = self.routing_key_override

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "broadcast_id": broadcast_id,
                "name": name,
                "target_path": target_path,
                "sort_order": sort_order,
            }
        )
        if routing_key_override is not UNSET:
            field_dict["routing_key_override"] = routing_key_override

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.broadcast_target_public_routing_key_override_type_0 import (
            BroadcastTargetPublicRoutingKeyOverrideType0,
        )

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        broadcast_id = UUID(d.pop("broadcast_id"))

        name = d.pop("name")

        target_path = d.pop("target_path")

        sort_order = d.pop("sort_order")

        def _parse_routing_key_override(data: object) -> BroadcastTargetPublicRoutingKeyOverrideType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_override_type_0 = BroadcastTargetPublicRoutingKeyOverrideType0.from_dict(data)

                return routing_key_override_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BroadcastTargetPublicRoutingKeyOverrideType0 | None | Unset, data)

        routing_key_override = _parse_routing_key_override(d.pop("routing_key_override", UNSET))

        broadcast_target_public = cls(
            id=id,
            broadcast_id=broadcast_id,
            name=name,
            target_path=target_path,
            sort_order=sort_order,
            routing_key_override=routing_key_override,
        )

        broadcast_target_public.additional_properties = d
        return broadcast_target_public

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
