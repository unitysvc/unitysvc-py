from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plan_meter_public import PlanMeterPublic
    from ..models.service_usage_public import ServiceUsagePublic


T = TypeVar("T", bound="CycleUsageResponse")


@_attrs_define
class CycleUsageResponse:
    """Cycle-to-date usage and cost for the authenticated customer."""

    cycle_start: datetime.date
    cycle_end: datetime.date
    as_of: datetime.datetime
    days_elapsed: int
    days_total: int
    currency: str
    services_charge: str
    meters_charge: str
    total_charge: str
    projected_total_charge: str
    """ Flat extrapolation to cycle end; a projection, not a quote """
    has_active_plan: bool | Unset = False
    """ Whether the customer has an active/trialing plan subscription """
    services: list[ServiceUsagePublic] | Unset = UNSET
    meters: list[PlanMeterPublic] | Unset = UNSET
    wallet_balance: None | str | Unset = UNSET
    balance_after_usage: None | str | Unset = UNSET
    """ wallet_balance - total_charge, computed live """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cycle_start = self.cycle_start.isoformat()

        cycle_end = self.cycle_end.isoformat()

        as_of = self.as_of.isoformat()

        days_elapsed = self.days_elapsed

        days_total = self.days_total

        currency = self.currency

        services_charge = self.services_charge

        meters_charge = self.meters_charge

        total_charge = self.total_charge

        projected_total_charge = self.projected_total_charge

        has_active_plan = self.has_active_plan

        services: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.services, Unset):
            services = []
            for services_item_data in self.services:
                services_item = services_item_data.to_dict()
                services.append(services_item)

        meters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.meters, Unset):
            meters = []
            for meters_item_data in self.meters:
                meters_item = meters_item_data.to_dict()
                meters.append(meters_item)

        wallet_balance: None | str | Unset
        if isinstance(self.wallet_balance, Unset):
            wallet_balance = UNSET
        else:
            wallet_balance = self.wallet_balance

        balance_after_usage: None | str | Unset
        if isinstance(self.balance_after_usage, Unset):
            balance_after_usage = UNSET
        else:
            balance_after_usage = self.balance_after_usage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cycle_start": cycle_start,
                "cycle_end": cycle_end,
                "as_of": as_of,
                "days_elapsed": days_elapsed,
                "days_total": days_total,
                "currency": currency,
                "services_charge": services_charge,
                "meters_charge": meters_charge,
                "total_charge": total_charge,
                "projected_total_charge": projected_total_charge,
            }
        )
        if has_active_plan is not UNSET:
            field_dict["has_active_plan"] = has_active_plan
        if services is not UNSET:
            field_dict["services"] = services
        if meters is not UNSET:
            field_dict["meters"] = meters
        if wallet_balance is not UNSET:
            field_dict["wallet_balance"] = wallet_balance
        if balance_after_usage is not UNSET:
            field_dict["balance_after_usage"] = balance_after_usage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plan_meter_public import PlanMeterPublic
        from ..models.service_usage_public import ServiceUsagePublic

        d = dict(src_dict)
        cycle_start = isoparse(d.pop("cycle_start")).date()

        cycle_end = isoparse(d.pop("cycle_end")).date()

        as_of = isoparse(d.pop("as_of"))

        days_elapsed = d.pop("days_elapsed")

        days_total = d.pop("days_total")

        currency = d.pop("currency")

        services_charge = d.pop("services_charge")

        meters_charge = d.pop("meters_charge")

        total_charge = d.pop("total_charge")

        projected_total_charge = d.pop("projected_total_charge")

        has_active_plan = d.pop("has_active_plan", UNSET)

        _services = d.pop("services", UNSET)
        services: list[ServiceUsagePublic] | Unset = UNSET
        if _services is not UNSET:
            services = []
            for services_item_data in _services:
                services_item = ServiceUsagePublic.from_dict(services_item_data)

                services.append(services_item)

        _meters = d.pop("meters", UNSET)
        meters: list[PlanMeterPublic] | Unset = UNSET
        if _meters is not UNSET:
            meters = []
            for meters_item_data in _meters:
                meters_item = PlanMeterPublic.from_dict(meters_item_data)

                meters.append(meters_item)

        def _parse_wallet_balance(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        wallet_balance = _parse_wallet_balance(d.pop("wallet_balance", UNSET))

        def _parse_balance_after_usage(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        balance_after_usage = _parse_balance_after_usage(d.pop("balance_after_usage", UNSET))

        cycle_usage_response = cls(
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            as_of=as_of,
            days_elapsed=days_elapsed,
            days_total=days_total,
            currency=currency,
            services_charge=services_charge,
            meters_charge=meters_charge,
            total_charge=total_charge,
            projected_total_charge=projected_total_charge,
            has_active_plan=has_active_plan,
            services=services,
            meters=meters,
            wallet_balance=wallet_balance,
            balance_after_usage=balance_after_usage,
        )

        cycle_usage_response.additional_properties = d
        return cycle_usage_response

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
