from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_enrollment import CustomerEnrollment


T = TypeVar("T", bound="CustomerEnrollmentsResponse")


@_attrs_define
class CustomerEnrollmentsResponse:
    """Paginated list of the caller's enrollments."""

    data: list[CustomerEnrollment]
    count: int
    skip: int
    limit: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_enrollment import CustomerEnrollment

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        count = self.count

        skip = self.skip

        limit = self.limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "count": count,
                "skip": skip,
                "limit": limit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_enrollment import CustomerEnrollment

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = CustomerEnrollment.from_dict(data_item_data)

            data.append(data_item)

        count = d.pop("count")

        skip = d.pop("skip")

        limit = d.pop("limit")

        customer_enrollments_response = cls(
            data=data,
            count=count,
            skip=skip,
            limit=limit,
        )

        customer_enrollments_response.additional_properties = d
        return customer_enrollments_response

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
