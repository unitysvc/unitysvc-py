from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlanMeterPublic")


@_attrs_define
class PlanMeterPublic:
    """A plan-level meter (request logging, log storage, data transfer).

    Present only for resources the customer's plan actually defines, so the
    UI renders a quota bar per real entitlement and nothing otherwise.

    """

    key: str
    """ logging_db | logging_s3 | data_transfer_out|_in """
    based_on: str
    """ request_count | one_gigabyte """
    raw_quantity: int
    """ Used, in the base unit (rows or bytes) """
    included: int
    """ Free quota in based_on units, seat-scaled """
    cost: str
    """ Overage cost this cycle """
    overage_billable: bool | Unset = False
    """ Whether exceeding `included` is charged. False means the plan prices this resource at $0 throughout, so
    `included` is not a real ceiling and the UI should not draw progress toward it. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        based_on = self.based_on

        raw_quantity = self.raw_quantity

        included = self.included

        cost = self.cost

        overage_billable = self.overage_billable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "based_on": based_on,
                "raw_quantity": raw_quantity,
                "included": included,
                "cost": cost,
            }
        )
        if overage_billable is not UNSET:
            field_dict["overage_billable"] = overage_billable

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        key = d.pop("key")

        based_on = d.pop("based_on")

        raw_quantity = d.pop("raw_quantity")

        included = d.pop("included")

        cost = d.pop("cost")

        overage_billable = d.pop("overage_billable", UNSET)

        plan_meter_public = cls(
            key=key,
            based_on=based_on,
            raw_quantity=raw_quantity,
            included=included,
            cost=cost,
            overage_billable=overage_billable,
        )

        plan_meter_public.additional_properties = d
        return plan_meter_public

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
