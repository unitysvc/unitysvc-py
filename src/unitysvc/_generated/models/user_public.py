from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_public_preference_type_0 import UserPublicPreferenceType0


T = TypeVar("T", bound="UserPublic")


@_attrs_define
class UserPublic:
    """For API response"""

    id: UUID
    email: str
    is_superuser: bool | Unset = False
    full_name: None | str | Unset = UNSET
    preference: None | Unset | UserPublicPreferenceType0 = UNSET
    primary_email_configured: bool | Unset = False

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_public_preference_type_0 import UserPublicPreferenceType0

        id = str(self.id)

        email = self.email

        is_superuser = self.is_superuser

        full_name: None | str | Unset
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

        preference: dict[str, Any] | None | Unset
        if isinstance(self.preference, Unset):
            preference = UNSET
        elif isinstance(self.preference, UserPublicPreferenceType0):
            preference = self.preference.to_dict()
        else:
            preference = self.preference

        primary_email_configured = self.primary_email_configured

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "email": email,
            }
        )
        if is_superuser is not UNSET:
            field_dict["is_superuser"] = is_superuser
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if preference is not UNSET:
            field_dict["preference"] = preference
        if primary_email_configured is not UNSET:
            field_dict["primary_email_configured"] = primary_email_configured

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_public_preference_type_0 import UserPublicPreferenceType0

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        email = d.pop("email")

        is_superuser = d.pop("is_superuser", UNSET)

        def _parse_full_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))

        def _parse_preference(data: object) -> None | Unset | UserPublicPreferenceType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                preference_type_0 = UserPublicPreferenceType0.from_dict(data)

                return preference_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UserPublicPreferenceType0, data)

        preference = _parse_preference(d.pop("preference", UNSET))

        primary_email_configured = d.pop("primary_email_configured", UNSET)

        user_public = cls(
            id=id,
            email=email,
            is_superuser=is_superuser,
            full_name=full_name,
            preference=preference,
            primary_email_configured=primary_email_configured,
        )

        return user_public
