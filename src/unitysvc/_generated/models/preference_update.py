from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.preference_value import PreferenceValue


T = TypeVar("T", bound="PreferenceUpdate")


@_attrs_define
class PreferenceUpdate:
    """``value``: ``{"service": ...}`` (or the service as a string), a mode
    for ``request-log``, or ``auto`` / ``off`` / a path for a ``room-*``
    preference. Use ``DELETE`` to clear.

    """

    value: PreferenceValue | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.preference_value import PreferenceValue

        value: dict[str, Any] | str
        if isinstance(self.value, PreferenceValue):
            value = self.value.to_dict()
        else:
            value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.preference_value import PreferenceValue

        d = dict(src_dict)

        def _parse_value(data: object) -> PreferenceValue | str:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                value_type_0 = PreferenceValue.from_dict(data)

                return value_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(PreferenceValue | str, data)

        value = _parse_value(d.pop("value"))

        preference_update = cls(
            value=value,
        )

        preference_update.additional_properties = d
        return preference_update

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
