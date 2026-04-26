from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceSummary")


@_attrs_define
class ServiceSummary:
    """Minimal service info used when listing services inside a group.

    Intentionally narrow: enough to render a picker and drill in,
    nothing that customers don't need at browse time. Fetch
    ``ServiceDetail`` for the full schema.

    ``status`` is intentionally not exposed — customers only ever
    see ``active`` services (the visibility filter guarantees it),
    so a field whose only valid value is ``"active"`` carries no
    information. Same reasoning for ``is_active`` on
    ``AccessInterface``.

    """

    id: UUID
    name: str
    display_name: None | str | Unset = UNSET
    service_type: None | str | Unset = UNSET
    gateway_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        service_type: None | str | Unset
        if isinstance(self.service_type, Unset):
            service_type = UNSET
        else:
            service_type = self.service_type

        gateway_type: None | str | Unset
        if isinstance(self.gateway_type, Unset):
            gateway_type = UNSET
        else:
            gateway_type = self.gateway_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if service_type is not UNSET:
            field_dict["service_type"] = service_type
        if gateway_type is not UNSET:
            field_dict["gateway_type"] = gateway_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_service_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_type = _parse_service_type(d.pop("service_type", UNSET))

        def _parse_gateway_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        gateway_type = _parse_gateway_type(d.pop("gateway_type", UNSET))

        service_summary = cls(
            id=id,
            name=name,
            display_name=display_name,
            service_type=service_type,
            gateway_type=gateway_type,
        )

        service_summary.additional_properties = d
        return service_summary

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
