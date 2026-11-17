from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EnrollmentInstanceEntry")


@_attrs_define
class EnrollmentInstanceEntry:
    """A customer-visible URL declared by the instance specification."""

    name: str
    hostname: str
    url: str
    """ https URL of the entry (hostname and path) """
    auth: str
    """ Who may reach it: login, key or app """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        hostname = self.hostname

        url = self.url

        auth = self.auth

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "hostname": hostname,
                "url": url,
                "auth": auth,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        hostname = d.pop("hostname")

        url = d.pop("url")

        auth = d.pop("auth")

        enrollment_instance_entry = cls(
            name=name,
            hostname=hostname,
            url=url,
            auth=auth,
        )

        enrollment_instance_entry.additional_properties = d
        return enrollment_instance_entry

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
