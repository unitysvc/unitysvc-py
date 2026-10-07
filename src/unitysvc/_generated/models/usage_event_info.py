from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usage_event_metrics import UsageEventMetrics


T = TypeVar("T", bound="UsageEventInfo")


@_attrs_define
class UsageEventInfo:
    """Linked usage event data.

    Charges are derived from the pricing bundle at statement time; the raw
    ClickHouse event stores only the bundle reference and usage metrics.

    """

    usage_metrics: UsageEventMetrics
    pricing_bundle_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.usage_event_metrics import UsageEventMetrics

        usage_metrics = self.usage_metrics.to_dict()

        pricing_bundle_id: None | str | Unset
        if isinstance(self.pricing_bundle_id, Unset):
            pricing_bundle_id = UNSET
        else:
            pricing_bundle_id = self.pricing_bundle_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "usage_metrics": usage_metrics,
            }
        )
        if pricing_bundle_id is not UNSET:
            field_dict["pricing_bundle_id"] = pricing_bundle_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_event_metrics import UsageEventMetrics

        d = dict(src_dict)
        usage_metrics = UsageEventMetrics.from_dict(d.pop("usage_metrics"))

        def _parse_pricing_bundle_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pricing_bundle_id = _parse_pricing_bundle_id(d.pop("pricing_bundle_id", UNSET))

        usage_event_info = cls(
            usage_metrics=usage_metrics,
            pricing_bundle_id=pricing_bundle_id,
        )

        usage_event_info.additional_properties = d
        return usage_event_info

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
