from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChainStepPublic")


@_attrs_define
class ChainStepPublic:
    id: UUID
    chain_id: UUID
    name: str
    target_path: str
    on_success: str
    on_failure: str
    sort_order: int
    timeout_ms: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        chain_id = str(self.chain_id)

        name = self.name

        target_path = self.target_path

        on_success = self.on_success

        on_failure = self.on_failure

        sort_order = self.sort_order

        timeout_ms: int | None | Unset
        if isinstance(self.timeout_ms, Unset):
            timeout_ms = UNSET
        else:
            timeout_ms = self.timeout_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "chain_id": chain_id,
                "name": name,
                "target_path": target_path,
                "on_success": on_success,
                "on_failure": on_failure,
                "sort_order": sort_order,
            }
        )
        if timeout_ms is not UNSET:
            field_dict["timeout_ms"] = timeout_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        chain_id = UUID(d.pop("chain_id"))

        name = d.pop("name")

        target_path = d.pop("target_path")

        on_success = d.pop("on_success")

        on_failure = d.pop("on_failure")

        sort_order = d.pop("sort_order")

        def _parse_timeout_ms(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        timeout_ms = _parse_timeout_ms(d.pop("timeout_ms", UNSET))

        chain_step_public = cls(
            id=id,
            chain_id=chain_id,
            name=name,
            target_path=target_path,
            on_success=on_success,
            on_failure=on_failure,
            sort_order=sort_order,
            timeout_ms=timeout_ms,
        )

        chain_step_public.additional_properties = d
        return chain_step_public

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
