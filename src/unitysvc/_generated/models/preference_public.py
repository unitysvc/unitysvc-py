from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.preference_public_source_type_0 import PreferencePublicSourceType0, check_preference_public_source_type_0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.preference_account_public import PreferenceAccountPublic
    from ..models.preference_value import PreferenceValue


T = TypeVar("T", bound="PreferencePublic")


@_attrs_define
class PreferencePublic:
    """One preference as the current account sees it.

    ``value`` is the account's own setting (``null`` when unset), a
    :class:`PreferenceValue` or, for ``request-log``, a mode string.
    ``effective`` is what applies now and ``source`` where it comes from:
    ``account`` (its own value), ``user`` (a team's notices falling back to
    your own destination), or ``default``. ``null`` when nothing applies.

    """

    name: str
    account: PreferenceAccountPublic
    can_edit: bool
    value: None | PreferenceValue | str | Unset = UNSET
    effective: None | PreferenceValue | str | Unset = UNSET
    source: None | PreferencePublicSourceType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.preference_account_public import PreferenceAccountPublic
        from ..models.preference_value import PreferenceValue

        name = self.name

        account = self.account.to_dict()

        can_edit = self.can_edit

        value: dict[str, Any] | None | str | Unset
        if isinstance(self.value, Unset):
            value = UNSET
        elif isinstance(self.value, PreferenceValue):
            value = self.value.to_dict()
        else:
            value = self.value

        effective: dict[str, Any] | None | str | Unset
        if isinstance(self.effective, Unset):
            effective = UNSET
        elif isinstance(self.effective, PreferenceValue):
            effective = self.effective.to_dict()
        else:
            effective = self.effective

        source: None | str | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        elif isinstance(self.source, str):
            source = self.source
        else:
            source = self.source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "account": account,
                "can_edit": can_edit,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value
        if effective is not UNSET:
            field_dict["effective"] = effective
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preference_account_public import PreferenceAccountPublic
        from ..models.preference_value import PreferenceValue

        d = dict(src_dict)
        name = d.pop("name")

        account = PreferenceAccountPublic.from_dict(d.pop("account"))

        can_edit = d.pop("can_edit")

        def _parse_value(data: object) -> None | PreferenceValue | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                value_type_0 = PreferenceValue.from_dict(data)

                return value_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PreferenceValue | str | Unset, data)

        value = _parse_value(d.pop("value", UNSET))

        def _parse_effective(data: object) -> None | PreferenceValue | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                effective_type_0 = PreferenceValue.from_dict(data)

                return effective_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PreferenceValue | str | Unset, data)

        effective = _parse_effective(d.pop("effective", UNSET))

        def _parse_source(data: object) -> None | PreferencePublicSourceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                source_type_0 = check_preference_public_source_type_0(data)

                return source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PreferencePublicSourceType0 | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        preference_public = cls(
            name=name,
            account=account,
            can_edit=can_edit,
            value=value,
            effective=effective,
            source=source,
        )

        preference_public.additional_properties = d
        return preference_public

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
