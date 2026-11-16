from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ComputeComponent")


@_attrs_define
class ComputeComponent:
    service: str
    pod: str
    phase: str
    ready: bool
    reason: None | str | Unset = UNSET
    restart_count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service = self.service

        pod = self.pod

        phase = self.phase

        ready = self.ready

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        restart_count = self.restart_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service": service,
                "pod": pod,
                "phase": phase,
                "ready": ready,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason
        if restart_count is not UNSET:
            field_dict["restart_count"] = restart_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        service = d.pop("service")

        pod = d.pop("pod")

        phase = d.pop("phase")

        ready = d.pop("ready")

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        restart_count = d.pop("restart_count", UNSET)

        compute_component = cls(
            service=service,
            pod=pod,
            phase=phase,
            ready=ready,
            reason=reason,
            restart_count=restart_count,
        )

        compute_component.additional_properties = d
        return compute_component

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
