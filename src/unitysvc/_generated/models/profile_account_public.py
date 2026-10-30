from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.profile_account_public_type import ProfileAccountPublicType, check_profile_account_public_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProfileAccountPublic")


@_attrs_define
class ProfileAccountPublic:
    type_: ProfileAccountPublicType
    name: str
    id: None | str | Unset = UNSET
    joined_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        name = self.name

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        joined_at: None | str | Unset
        if isinstance(self.joined_at, Unset):
            joined_at = UNSET
        elif isinstance(self.joined_at, datetime.datetime):
            joined_at = self.joined_at.isoformat()
        else:
            joined_at = self.joined_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "name": name,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if joined_at is not UNSET:
            field_dict["joined_at"] = joined_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = check_profile_account_public_type(d.pop("type"))

        name = d.pop("name")

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_joined_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                joined_at_type_0 = isoparse(data)

                return joined_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        joined_at = _parse_joined_at(d.pop("joined_at", UNSET))

        profile_account_public = cls(
            type_=type_,
            name=name,
            id=id,
            joined_at=joined_at,
        )

        profile_account_public.additional_properties = d
        return profile_account_public

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
