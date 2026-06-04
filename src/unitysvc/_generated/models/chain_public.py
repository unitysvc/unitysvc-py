from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chain_step_public import ChainStepPublic


T = TypeVar("T", bound="ChainPublic")


@_attrs_define
class ChainPublic:
    id: UUID
    customer_id: UUID
    name: str
    default_timeout_ms: int
    enabled: bool
    created_at: datetime.datetime
    description: None | str | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    steps: list[ChainStepPublic] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.chain_step_public import ChainStepPublic

        id = str(self.id)

        customer_id = str(self.customer_id)

        name = self.name

        default_timeout_ms = self.default_timeout_ms

        enabled = self.enabled

        created_at = self.created_at.isoformat()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

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
                "id": id,
                "customer_id": customer_id,
                "name": name,
                "default_timeout_ms": default_timeout_ms,
                "enabled": enabled,
                "created_at": created_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if steps is not UNSET:
            field_dict["steps"] = steps

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chain_step_public import ChainStepPublic

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        customer_id = UUID(d.pop("customer_id"))

        name = d.pop("name")

        default_timeout_ms = d.pop("default_timeout_ms")

        enabled = d.pop("enabled")

        created_at = isoparse(d.pop("created_at"))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        _steps = d.pop("steps", UNSET)
        steps: list[ChainStepPublic] | Unset = UNSET
        if _steps is not UNSET:
            steps = []
            for steps_item_data in _steps:
                steps_item = ChainStepPublic.from_dict(steps_item_data)

                steps.append(steps_item)

        chain_public = cls(
            id=id,
            customer_id=customer_id,
            name=name,
            default_timeout_ms=default_timeout_ms,
            enabled=enabled,
            created_at=created_at,
            description=description,
            updated_at=updated_at,
            steps=steps,
        )

        chain_public.additional_properties = d
        return chain_public

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
