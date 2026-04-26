from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_detail_list_price_type_0 import ServiceDetailListPriceType0


T = TypeVar("T", bound="ServiceDetail")


@_attrs_define
class ServiceDetail:
    """Full customer-facing service details.

    Sourced from ``service_mview``. Intentionally narrow:

    - Omits seller-internal fields (``seller_id``, ``routing_vars``,
      ``payout_price``, ``ops_subscription_id``, ``ops_customer_id``)
      and draft-only fields (``pending_revision_id``).
    - Omits review stats (``review_count``, ``average_rating``) and
      logo URLs (``provider_logo``, ``offering_logo``,
      ``seller_logo``); those belong to the marketing/dashboard
      surface, not the SDK.
    - Omits ``tagline`` as marketing copy not used for dispatch.

    """

    id: UUID
    name: str
    display_name: None | str | Unset = UNSET
    service_type: None | str | Unset = UNSET
    gateway_type: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    provider_name: None | str | Unset = UNSET
    seller_name: None | str | Unset = UNSET
    capabilities: list[str] | None | Unset = UNSET
    tags: list[str] | None | Unset = UNSET
    list_price: None | ServiceDetailListPriceType0 | Unset = UNSET
    enrollment_required: bool | Unset = False
    listing_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_detail_list_price_type_0 import ServiceDetailListPriceType0

        id = str(self.id)

        name = self.name

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        service_type: None | str | Unset
        if isinstance(self.service_type, Unset):
            service_type = UNSET
        else:
            service_type = self.service_type

        gateway_type: None | str | Unset
        if isinstance(self.gateway_type, Unset):
            gateway_type = UNSET
        else:
            gateway_type = self.gateway_type

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        provider_name: None | str | Unset
        if isinstance(self.provider_name, Unset):
            provider_name = UNSET
        else:
            provider_name = self.provider_name

        seller_name: None | str | Unset
        if isinstance(self.seller_name, Unset):
            seller_name = UNSET
        else:
            seller_name = self.seller_name

        capabilities: list[str] | None | Unset
        if isinstance(self.capabilities, Unset):
            capabilities = UNSET
        elif isinstance(self.capabilities, list):
            capabilities = self.capabilities

        else:
            capabilities = self.capabilities

        tags: list[str] | None | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        list_price: dict[str, Any] | None | Unset
        if isinstance(self.list_price, Unset):
            list_price = UNSET
        elif isinstance(self.list_price, ServiceDetailListPriceType0):
            list_price = self.list_price.to_dict()
        else:
            list_price = self.list_price

        enrollment_required = self.enrollment_required

        listing_type: None | str | Unset
        if isinstance(self.listing_type, Unset):
            listing_type = UNSET
        else:
            listing_type = self.listing_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if service_type is not UNSET:
            field_dict["service_type"] = service_type
        if gateway_type is not UNSET:
            field_dict["gateway_type"] = gateway_type
        if description is not UNSET:
            field_dict["description"] = description
        if provider_name is not UNSET:
            field_dict["provider_name"] = provider_name
        if seller_name is not UNSET:
            field_dict["seller_name"] = seller_name
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities
        if tags is not UNSET:
            field_dict["tags"] = tags
        if list_price is not UNSET:
            field_dict["list_price"] = list_price
        if enrollment_required is not UNSET:
            field_dict["enrollment_required"] = enrollment_required
        if listing_type is not UNSET:
            field_dict["listing_type"] = listing_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_detail_list_price_type_0 import ServiceDetailListPriceType0

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_service_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_type = _parse_service_type(d.pop("service_type", UNSET))

        def _parse_gateway_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        gateway_type = _parse_gateway_type(d.pop("gateway_type", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_provider_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_name = _parse_provider_name(d.pop("provider_name", UNSET))

        def _parse_seller_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        seller_name = _parse_seller_name(d.pop("seller_name", UNSET))

        def _parse_capabilities(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                capabilities_type_0 = cast(list[str], data)

                return capabilities_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        capabilities = _parse_capabilities(d.pop("capabilities", UNSET))

        def _parse_tags(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        tags = _parse_tags(d.pop("tags", UNSET))

        def _parse_list_price(data: object) -> None | ServiceDetailListPriceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                list_price_type_0 = ServiceDetailListPriceType0.from_dict(data)

                return list_price_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceDetailListPriceType0 | Unset, data)

        list_price = _parse_list_price(d.pop("list_price", UNSET))

        enrollment_required = d.pop("enrollment_required", UNSET)

        def _parse_listing_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        listing_type = _parse_listing_type(d.pop("listing_type", UNSET))

        service_detail = cls(
            id=id,
            name=name,
            display_name=display_name,
            service_type=service_type,
            gateway_type=gateway_type,
            description=description,
            provider_name=provider_name,
            seller_name=seller_name,
            capabilities=capabilities,
            tags=tags,
            list_price=list_price,
            enrollment_required=enrollment_required,
            listing_type=listing_type,
        )

        service_detail.additional_properties = d
        return service_detail

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
