from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.broadcast_create_mode import BroadcastCreateMode, check_broadcast_create_mode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.broadcast_target_create import BroadcastTargetCreate


T = TypeVar("T", bound="BroadcastCreate")


@_attrs_define
class BroadcastCreate:
    name: str
    description: None | str | Unset = UNSET
    mode: BroadcastCreateMode | Unset = "sync"
    target_timeout_ms: int | Unset = 30000
    enabled: bool | Unset = True
    targets: list[BroadcastTargetCreate] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.broadcast_target_create import BroadcastTargetCreate

        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode

        target_timeout_ms = self.target_timeout_ms

        enabled = self.enabled

        targets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.targets, Unset):
            targets = []
            for targets_item_data in self.targets:
                targets_item = targets_item_data.to_dict()
                targets.append(targets_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if mode is not UNSET:
            field_dict["mode"] = mode
        if target_timeout_ms is not UNSET:
            field_dict["target_timeout_ms"] = target_timeout_ms
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if targets is not UNSET:
            field_dict["targets"] = targets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.broadcast_target_create import BroadcastTargetCreate

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        _mode = d.pop("mode", UNSET)
        mode: BroadcastCreateMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = check_broadcast_create_mode(_mode)

        target_timeout_ms = d.pop("target_timeout_ms", UNSET)

        enabled = d.pop("enabled", UNSET)

        _targets = d.pop("targets", UNSET)
        targets: list[BroadcastTargetCreate] | Unset = UNSET
        if _targets is not UNSET:
            targets = []
            for targets_item_data in _targets:
                targets_item = BroadcastTargetCreate.from_dict(targets_item_data)

                targets.append(targets_item)

        broadcast_create = cls(
            name=name,
            description=description,
            mode=mode,
            target_timeout_ms=target_timeout_ms,
            enabled=enabled,
            targets=targets,
        )

        broadcast_create.additional_properties = d
        return broadcast_create

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
