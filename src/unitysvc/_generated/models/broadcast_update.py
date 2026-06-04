from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.broadcast_update_mode_type_0 import BroadcastUpdateModeType0, check_broadcast_update_mode_type_0
from ..types import UNSET, Unset

T = TypeVar("T", bound="BroadcastUpdate")


@_attrs_define
class BroadcastUpdate:
    description: None | str | Unset = UNSET
    mode: BroadcastUpdateModeType0 | None | Unset = UNSET
    target_timeout_ms: int | None | Unset = UNSET
    enabled: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        mode: None | str | Unset
        if isinstance(self.mode, Unset):
            mode = UNSET
        elif isinstance(self.mode, str):
            mode = self.mode
        else:
            mode = self.mode

        target_timeout_ms: int | None | Unset
        if isinstance(self.target_timeout_ms, Unset):
            target_timeout_ms = UNSET
        else:
            target_timeout_ms = self.target_timeout_ms

        enabled: bool | None | Unset
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if mode is not UNSET:
            field_dict["mode"] = mode
        if target_timeout_ms is not UNSET:
            field_dict["target_timeout_ms"] = target_timeout_ms
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_mode(data: object) -> BroadcastUpdateModeType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                mode_type_0 = check_broadcast_update_mode_type_0(data)

                return mode_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BroadcastUpdateModeType0 | None | Unset, data)

        mode = _parse_mode(d.pop("mode", UNSET))

        def _parse_target_timeout_ms(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        target_timeout_ms = _parse_target_timeout_ms(d.pop("target_timeout_ms", UNSET))

        def _parse_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        broadcast_update = cls(
            description=description,
            mode=mode,
            target_timeout_ms=target_timeout_ms,
            enabled=enabled,
        )

        broadcast_update.additional_properties = d
        return broadcast_update

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
