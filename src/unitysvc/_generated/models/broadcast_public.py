from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.broadcast_public_mode import BroadcastPublicMode, check_broadcast_public_mode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.broadcast_target_public import BroadcastTargetPublic


T = TypeVar("T", bound="BroadcastPublic")


@_attrs_define
class BroadcastPublic:
    id: UUID
    customer_id: UUID
    name: str
    mode: BroadcastPublicMode
    target_timeout_ms: int
    enabled: bool
    created_at: datetime.datetime
    owner_id: None | Unset | UUID = UNSET
    description: None | str | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    targets: list[BroadcastTargetPublic] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.broadcast_target_public import BroadcastTargetPublic

        id = str(self.id)

        customer_id = str(self.customer_id)

        name = self.name

        mode: str = self.mode

        target_timeout_ms = self.target_timeout_ms

        enabled = self.enabled

        created_at = self.created_at.isoformat()

        owner_id: None | str | Unset
        if isinstance(self.owner_id, Unset):
            owner_id = UNSET
        elif isinstance(self.owner_id, UUID):
            owner_id = str(self.owner_id)
        else:
            owner_id = self.owner_id

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
                "id": id,
                "customer_id": customer_id,
                "name": name,
                "mode": mode,
                "target_timeout_ms": target_timeout_ms,
                "enabled": enabled,
                "created_at": created_at,
            }
        )
        if owner_id is not UNSET:
            field_dict["owner_id"] = owner_id
        if description is not UNSET:
            field_dict["description"] = description
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if targets is not UNSET:
            field_dict["targets"] = targets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.broadcast_target_public import BroadcastTargetPublic

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        customer_id = UUID(d.pop("customer_id"))

        name = d.pop("name")

        mode = check_broadcast_public_mode(d.pop("mode"))

        target_timeout_ms = d.pop("target_timeout_ms")

        enabled = d.pop("enabled")

        created_at = isoparse(d.pop("created_at"))

        def _parse_owner_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                owner_id_type_0 = UUID(data)

                return owner_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        owner_id = _parse_owner_id(d.pop("owner_id", UNSET))

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

        _targets = d.pop("targets", UNSET)
        targets: list[BroadcastTargetPublic] | Unset = UNSET
        if _targets is not UNSET:
            targets = []
            for targets_item_data in _targets:
                targets_item = BroadcastTargetPublic.from_dict(targets_item_data)

                targets.append(targets_item)

        broadcast_public = cls(
            id=id,
            customer_id=customer_id,
            name=name,
            mode=mode,
            target_timeout_ms=target_timeout_ms,
            enabled=enabled,
            created_at=created_at,
            owner_id=owner_id,
            description=description,
            updated_at=updated_at,
            targets=targets,
        )

        broadcast_public.additional_properties = d
        return broadcast_public

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
