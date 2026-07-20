from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceUsageResponse")


@_attrs_define
class ServiceUsageResponse:
    """A derived "how to use this service" guide (#1622).

    ``markdown`` is the whole answer — which channels the service offers, what
    each costs, whether it needs secrets or enrollment, and how to call it —
    synthesized from metadata so no seller has to author it. The structured
    plan it is rendered from stays server-side (canonical, testable); only the
    markdown is exposed.

    """

    markdown: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        markdown = self.markdown

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "markdown": markdown,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        markdown = d.pop("markdown")

        service_usage_response = cls(
            markdown=markdown,
        )

        service_usage_response.additional_properties = d
        return service_usage_response

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
