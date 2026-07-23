from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_interface_plan_routing_key_type_0 import AccessInterfacePlanRoutingKeyType0


T = TypeVar("T", bound="AccessInterfacePlan")


@_attrs_define
class AccessInterfacePlan:
    """A user-access interface — the endpoint a customer calls (#1638).

    Generic (same for every caller): the resolved ``base_url`` and any
    ``routing_key`` fields. Populated only for services that expose a **shared**
    (non-enrollment) interface; an enrollment service's interface is materialized
    per enrollment, so its concrete URL is the caller's ``/e/<CODE>`` — formed by
    the consumer from its own enrollment context, qualified by ``enrollment_mode``.

    """

    name: str
    base_url: None | str | Unset = UNSET
    routing_key: AccessInterfacePlanRoutingKeyType0 | None | Unset = UNSET
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_interface_plan_routing_key_type_0 import AccessInterfacePlanRoutingKeyType0

        name = self.name

        base_url: None | str | Unset
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        routing_key: dict[str, Any] | None | Unset
        if isinstance(self.routing_key, Unset):
            routing_key = UNSET
        elif isinstance(self.routing_key, AccessInterfacePlanRoutingKeyType0):
            routing_key = self.routing_key.to_dict()
        else:
            routing_key = self.routing_key

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
            }
        )
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if routing_key is not UNSET:
            field_dict["routing_key"] = routing_key
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_interface_plan_routing_key_type_0 import AccessInterfacePlanRoutingKeyType0

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_base_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        def _parse_routing_key(data: object) -> AccessInterfacePlanRoutingKeyType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_type_0 = AccessInterfacePlanRoutingKeyType0.from_dict(data)

                return routing_key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AccessInterfacePlanRoutingKeyType0 | None | Unset, data)

        routing_key = _parse_routing_key(d.pop("routing_key", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        access_interface_plan = cls(
            name=name,
            base_url=base_url,
            routing_key=routing_key,
            description=description,
        )

        access_interface_plan.additional_properties = d
        return access_interface_plan

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
