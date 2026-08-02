from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_type_enum import GroupTypeEnum, check_group_type_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_group_view_details_type_0 import CustomerGroupViewDetailsType0


T = TypeVar("T", bound="CustomerGroupView")


@_attrs_define
class CustomerGroupView:
    """Unified shape for the merged /customer/groups list — either a read-only
    platform ServiceGroup or the customer's own editable ServiceCollection.

    """

    id: UUID
    name: str
    owner_type: str
    editable: bool
    group_type: GroupTypeEnum
    """ Type of service group. Derived from members, not authored (unitysvc#1686).

    Two of the five types are routable (a ``/g/<name>`` endpoint); the rest are
    not:

    - ``open``  — routable, and members share a common request format, so a
      request with **no** routing key fans safely across them. A key may still
      be passed to select one. (Also the single-member case.)
    - ``keyed`` — routable, but members accept different formats, so a keyless
      request is ambiguous: a routing key is **required**, and every key
      resolves to a format-homogeneous set.
    - ``collection`` — not a routing endpoint. A browse-only set, or a would-be
      routable group demoted because some routing key spans incompatible
      formats (a request to that key couldn't be served reliably).
    - ``category`` — a parent with no members of its own; its membership is the
      union of its descendants, for browsing only.
    - ``capability_pool`` (#1244) — the ``/p/<name>`` namespace; membership is
      claim-driven (services instantiated from a ServiceTemplate whose
      ``pool_name`` matches), set by a dedicated refresh.

    ``open`` / ``keyed`` / ``collection`` are derived from the members at
    membership refresh; ``category`` and ``capability_pool`` are set explicitly
    and never re-derived. (The former ``routable`` value was split into
    ``open`` / ``keyed``, and the ``misc`` catch-all removed — unitysvc#1686.) """
    display_name: None | str | Unset = UNSET
    member_count: int | Unset = 0
    details: CustomerGroupViewDetailsType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_group_view_details_type_0 import CustomerGroupViewDetailsType0

        id = str(self.id)

        name = self.name

        owner_type = self.owner_type

        editable = self.editable

        group_type: str = self.group_type

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        member_count = self.member_count

        details: dict[str, Any] | None | Unset
        if isinstance(self.details, Unset):
            details = UNSET
        elif isinstance(self.details, CustomerGroupViewDetailsType0):
            details = self.details.to_dict()
        else:
            details = self.details

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "owner_type": owner_type,
                "editable": editable,
                "group_type": group_type,
            }
        )
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if member_count is not UNSET:
            field_dict["member_count"] = member_count
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_group_view_details_type_0 import CustomerGroupViewDetailsType0

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        owner_type = d.pop("owner_type")

        editable = d.pop("editable")

        group_type = check_group_type_enum(d.pop("group_type"))

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        member_count = d.pop("member_count", UNSET)

        def _parse_details(data: object) -> CustomerGroupViewDetailsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                details_type_0 = CustomerGroupViewDetailsType0.from_dict(data)

                return details_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerGroupViewDetailsType0 | None | Unset, data)

        details = _parse_details(d.pop("details", UNSET))

        customer_group_view = cls(
            id=id,
            name=name,
            owner_type=owner_type,
            editable=editable,
            group_type=group_type,
            display_name=display_name,
            member_count=member_count,
            details=details,
        )

        customer_group_view.additional_properties = d
        return customer_group_view

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
