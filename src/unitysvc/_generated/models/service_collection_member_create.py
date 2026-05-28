from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_collection_member_create_routing_key_type_0 import (
        ServiceCollectionMemberCreateRoutingKeyType0,
    )


T = TypeVar("T", bound="ServiceCollectionMemberCreate")


@_attrs_define
class ServiceCollectionMemberCreate:
    """Schema for adding a member to a ServiceCollection."""

    service_id: UUID
    routing_key: None | ServiceCollectionMemberCreateRoutingKeyType0 | Unset = UNSET
    sort_order: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_collection_member_create_routing_key_type_0 import (
            ServiceCollectionMemberCreateRoutingKeyType0,
        )

        service_id = str(self.service_id)

        routing_key: dict[str, Any] | None | Unset
        if isinstance(self.routing_key, Unset):
            routing_key = UNSET
        elif isinstance(self.routing_key, ServiceCollectionMemberCreateRoutingKeyType0):
            routing_key = self.routing_key.to_dict()
        else:
            routing_key = self.routing_key

        sort_order = self.sort_order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_id": service_id,
            }
        )
        if routing_key is not UNSET:
            field_dict["routing_key"] = routing_key
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_collection_member_create_routing_key_type_0 import (
            ServiceCollectionMemberCreateRoutingKeyType0,
        )

        d = dict(src_dict)
        service_id = UUID(d.pop("service_id"))

        def _parse_routing_key(data: object) -> None | ServiceCollectionMemberCreateRoutingKeyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_type_0 = ServiceCollectionMemberCreateRoutingKeyType0.from_dict(data)

                return routing_key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceCollectionMemberCreateRoutingKeyType0 | Unset, data)

        routing_key = _parse_routing_key(d.pop("routing_key", UNSET))

        sort_order = d.pop("sort_order", UNSET)

        service_collection_member_create = cls(
            service_id=service_id,
            routing_key=routing_key,
            sort_order=sort_order,
        )

        service_collection_member_create.additional_properties = d
        return service_collection_member_create

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
