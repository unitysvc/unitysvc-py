from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.customer_content_update_values import CustomerContentUpdateValues


T = TypeVar("T", bound="CustomerContentUpdate")


@_attrs_define
class CustomerContentUpdate:
    """Owner replacement. The current revision is required, even for an empty save."""

    version: int
    values: CustomerContentUpdateValues

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        values = self.values.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "version": version,
                "values": values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_content_update_values import CustomerContentUpdateValues

        d = dict(src_dict)
        version = d.pop("version")

        values = CustomerContentUpdateValues.from_dict(d.pop("values"))

        customer_content_update = cls(
            version=version,
            values=values,
        )

        return customer_content_update
