from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usage_metrics import UsageMetrics


T = TypeVar("T", bound="ServiceUsagePublic")


@_attrs_define
class ServiceUsagePublic:
    """One service's usage and cost for the billing cycle."""

    service_id: UUID
    service_name: str
    """ Service name, blank if since deleted """
    request_count: int
    success_count: int
    error_count: int
    customer_charge: str
    """ Cost for this service this cycle """
    channel: str | Unset = ""
    """ Upstream access channel used """
    usage_metrics: UsageMetrics | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service_id = str(self.service_id)

        service_name = self.service_name

        request_count = self.request_count

        success_count = self.success_count

        error_count = self.error_count

        customer_charge = self.customer_charge

        channel = self.channel

        usage_metrics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage_metrics, Unset):
            usage_metrics = self.usage_metrics.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_id": service_id,
                "service_name": service_name,
                "request_count": request_count,
                "success_count": success_count,
                "error_count": error_count,
                "customer_charge": customer_charge,
            }
        )
        if channel is not UNSET:
            field_dict["channel"] = channel
        if usage_metrics is not UNSET:
            field_dict["usage_metrics"] = usage_metrics

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_metrics import UsageMetrics

        d = dict(src_dict)
        service_id = UUID(d.pop("service_id"))

        service_name = d.pop("service_name")

        request_count = d.pop("request_count")

        success_count = d.pop("success_count")

        error_count = d.pop("error_count")

        customer_charge = d.pop("customer_charge")

        channel = d.pop("channel", UNSET)

        _usage_metrics = d.pop("usage_metrics", UNSET)
        usage_metrics: UsageMetrics | Unset
        if isinstance(_usage_metrics, Unset):
            usage_metrics = UNSET
        else:
            usage_metrics = UsageMetrics.from_dict(_usage_metrics)

        service_usage_public = cls(
            service_id=service_id,
            service_name=service_name,
            request_count=request_count,
            success_count=success_count,
            error_count=error_count,
            customer_charge=customer_charge,
            channel=channel,
            usage_metrics=usage_metrics,
        )

        service_usage_public.additional_properties = d
        return service_usage_public

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
