from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
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

    A quick-characterization spectrum derived from ``routable_keys``
    (unitysvc#1730); the gateway routes off ``routable_keys`` itself, not this:

    - ``keyed`` — one extreme: a clean menu, every service addressable by its own
      distinct routing key (each key maps to a single service); keyless access an
      optional feature. Serves ``/v1/models`` and is tool-explorable.
    - ``open`` — the middle: routable, but not a clean per-service menu — a
      keyless-only pool, partial keying, or a key that fans to several services.
    - ``collection`` — the other extreme: **not** a routing endpoint at all
      (empty ``routable_keys`` — no members, or every bucket format-collides).

    Routability is exactly ``group_type in {open, keyed}`` (``collection`` =
    empty ``routable_keys``), so the routing gate is unchanged; #1730 only re-cut
    the open↔keyed boundary. Whether a keyless request is served is a
    ``routable_keys`` fact, not a type fact.
    - ``category`` — a parent with no members of its own; its membership is the
      union of its descendants, for browsing only.

    ``open`` / ``keyed`` / ``collection`` are derived from the members at
    membership refresh; ``category`` is set explicitly and never re-derived.
    (The former ``routable`` value was split into ``open`` / ``keyed``, and the
    ``misc`` catch-all removed — unitysvc#1686.) """
    display_name: None | str | Unset = UNSET
    member_count: int | Unset = 0
    is_default: bool | Unset = False
    service_ids: list[UUID] | None | Unset = UNSET
    owner_id: None | Unset | UUID = UNSET
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

        is_default = self.is_default

        service_ids: list[str] | None | Unset
        if isinstance(self.service_ids, Unset):
            service_ids = UNSET
        elif isinstance(self.service_ids, list):
            service_ids = []
            for service_ids_type_0_item_data in self.service_ids:
                service_ids_type_0_item = str(service_ids_type_0_item_data)
                service_ids.append(service_ids_type_0_item)

        else:
            service_ids = self.service_ids

        owner_id: None | str | Unset
        if isinstance(self.owner_id, Unset):
            owner_id = UNSET
        elif isinstance(self.owner_id, UUID):
            owner_id = str(self.owner_id)
        else:
            owner_id = self.owner_id

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
        if is_default is not UNSET:
            field_dict["is_default"] = is_default
        if service_ids is not UNSET:
            field_dict["service_ids"] = service_ids
        if owner_id is not UNSET:
            field_dict["owner_id"] = owner_id
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

        is_default = d.pop("is_default", UNSET)

        def _parse_service_ids(data: object) -> list[UUID] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                service_ids_type_0 = []
                _service_ids_type_0 = data
                for service_ids_type_0_item_data in _service_ids_type_0:
                    service_ids_type_0_item = UUID(service_ids_type_0_item_data)

                    service_ids_type_0.append(service_ids_type_0_item)

                return service_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[UUID] | None | Unset, data)

        service_ids = _parse_service_ids(d.pop("service_ids", UNSET))

        def _parse_owner_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                owner_id_type_0 = UUID(data)

                return owner_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        owner_id = _parse_owner_id(d.pop("owner_id", UNSET))

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
            is_default=is_default,
            service_ids=service_ids,
            owner_id=owner_id,
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
