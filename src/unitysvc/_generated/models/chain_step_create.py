from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChainStepCreate")


@_attrs_define
class ChainStepCreate:
    name: str
    target_path: str
    sort_order: int
    on_success: str | Unset = "stop"
    on_failure: str | Unset = "continue"
    timeout_ms: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        target_path = self.target_path

        sort_order = self.sort_order

        on_success = self.on_success

        on_failure = self.on_failure

        timeout_ms: int | None | Unset
        if isinstance(self.timeout_ms, Unset):
            timeout_ms = UNSET
        else:
            timeout_ms = self.timeout_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "target_path": target_path,
                "sort_order": sort_order,
            }
        )
        if on_success is not UNSET:
            field_dict["on_success"] = on_success
        if on_failure is not UNSET:
            field_dict["on_failure"] = on_failure
        if timeout_ms is not UNSET:
            field_dict["timeout_ms"] = timeout_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        target_path = d.pop("target_path")

        sort_order = d.pop("sort_order")

        on_success = d.pop("on_success", UNSET)

        on_failure = d.pop("on_failure", UNSET)

        def _parse_timeout_ms(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        timeout_ms = _parse_timeout_ms(d.pop("timeout_ms", UNSET))

        chain_step_create = cls(
            name=name,
            target_path=target_path,
            sort_order=sort_order,
            on_success=on_success,
            on_failure=on_failure,
            timeout_ms=timeout_ms,
        )

        chain_step_create.additional_properties = d
        return chain_step_create

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
