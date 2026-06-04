from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chain_step_create import ChainStepCreate


T = TypeVar("T", bound="ChainCreate")


@_attrs_define
class ChainCreate:
    name: str
    description: None | str | Unset = UNSET
    default_timeout_ms: int | Unset = 10000
    enabled: bool | Unset = True
    steps: list[ChainStepCreate] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.chain_step_create import ChainStepCreate

        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        default_timeout_ms = self.default_timeout_ms

        enabled = self.enabled

        steps: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.steps, Unset):
            steps = []
            for steps_item_data in self.steps:
                steps_item = steps_item_data.to_dict()
                steps.append(steps_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if default_timeout_ms is not UNSET:
            field_dict["default_timeout_ms"] = default_timeout_ms
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if steps is not UNSET:
            field_dict["steps"] = steps

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chain_step_create import ChainStepCreate

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        default_timeout_ms = d.pop("default_timeout_ms", UNSET)

        enabled = d.pop("enabled", UNSET)

        _steps = d.pop("steps", UNSET)
        steps: list[ChainStepCreate] | Unset = UNSET
        if _steps is not UNSET:
            steps = []
            for steps_item_data in _steps:
                steps_item = ChainStepCreate.from_dict(steps_item_data)

                steps.append(steps_item)

        chain_create = cls(
            name=name,
            description=description,
            default_timeout_ms=default_timeout_ms,
            enabled=enabled,
            steps=steps,
        )

        chain_create.additional_properties = d
        return chain_create

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
