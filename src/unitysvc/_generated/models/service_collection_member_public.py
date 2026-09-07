from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_collection_member_public_routing_key_type_0 import (
        ServiceCollectionMemberPublicRoutingKeyType0,
    )


T = TypeVar("T", bound="ServiceCollectionMemberPublic")


@_attrs_define
class ServiceCollectionMemberPublic:
    """Public response model for a collection member."""

    id: UUID
    service_id: UUID
    routing_key: None | ServiceCollectionMemberPublicRoutingKeyType0
    sort_order: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_collection_member_public_routing_key_type_0 import (
            ServiceCollectionMemberPublicRoutingKeyType0,
        )

        id = str(self.id)

        service_id = str(self.service_id)

        routing_key: dict[str, Any] | None
        if isinstance(self.routing_key, ServiceCollectionMemberPublicRoutingKeyType0):
            routing_key = self.routing_key.to_dict()
        else:
            routing_key = self.routing_key

        sort_order = self.sort_order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "service_id": service_id,
                "routing_key": routing_key,
                "sort_order": sort_order,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_collection_member_public_routing_key_type_0 import (
            ServiceCollectionMemberPublicRoutingKeyType0,
        )

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        service_id = UUID(d.pop("service_id"))

        def _parse_routing_key(data: object) -> None | ServiceCollectionMemberPublicRoutingKeyType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_type_0 = ServiceCollectionMemberPublicRoutingKeyType0.from_dict(data)

                return routing_key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceCollectionMemberPublicRoutingKeyType0, data)

        routing_key = _parse_routing_key(d.pop("routing_key"))

        sort_order = d.pop("sort_order")

        service_collection_member_public = cls(
            id=id,
            service_id=service_id,
            routing_key=routing_key,
            sort_order=sort_order,
        )

        service_collection_member_public.additional_properties = d
        return service_collection_member_public

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
