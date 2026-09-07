from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.secret_requirement import SecretRequirement


T = TypeVar("T", bound="ChannelPlan")


@_attrs_define
class ChannelPlan:
    """How one upstream channel of a service can be accessed (generic)."""

    name: str
    channel_type: str
    free: bool | Unset = False
    price_description: None | str | Unset = UNSET
    price: None | str | Unset = UNSET
    currency: None | str | Unset = UNSET
    requires_enrollment: bool | Unset = False
    required_secrets: list[SecretRequirement] | Unset = UNSET
    optional_secrets: list[SecretRequirement] | Unset = UNSET
    default: bool | Unset = False
    selector: None | str | Unset = UNSET
    applicable_interfaces: list[str] | None | Unset = UNSET
    request_formats: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.secret_requirement import SecretRequirement

        name = self.name

        channel_type = self.channel_type

        free = self.free

        price_description: None | str | Unset
        if isinstance(self.price_description, Unset):
            price_description = UNSET
        else:
            price_description = self.price_description

        price: None | str | Unset
        if isinstance(self.price, Unset):
            price = UNSET
        else:
            price = self.price

        currency: None | str | Unset
        if isinstance(self.currency, Unset):
            currency = UNSET
        else:
            currency = self.currency

        requires_enrollment = self.requires_enrollment

        required_secrets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.required_secrets, Unset):
            required_secrets = []
            for required_secrets_item_data in self.required_secrets:
                required_secrets_item = required_secrets_item_data.to_dict()
                required_secrets.append(required_secrets_item)

        optional_secrets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.optional_secrets, Unset):
            optional_secrets = []
            for optional_secrets_item_data in self.optional_secrets:
                optional_secrets_item = optional_secrets_item_data.to_dict()
                optional_secrets.append(optional_secrets_item)

        default = self.default

        selector: None | str | Unset
        if isinstance(self.selector, Unset):
            selector = UNSET
        else:
            selector = self.selector

        applicable_interfaces: list[str] | None | Unset
        if isinstance(self.applicable_interfaces, Unset):
            applicable_interfaces = UNSET
        elif isinstance(self.applicable_interfaces, list):
            applicable_interfaces = self.applicable_interfaces

        else:
            applicable_interfaces = self.applicable_interfaces

        request_formats: list[str] | None | Unset
        if isinstance(self.request_formats, Unset):
            request_formats = UNSET
        elif isinstance(self.request_formats, list):
            request_formats = self.request_formats

        else:
            request_formats = self.request_formats

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "channel_type": channel_type,
            }
        )
        if free is not UNSET:
            field_dict["free"] = free
        if price_description is not UNSET:
            field_dict["price_description"] = price_description
        if price is not UNSET:
            field_dict["price"] = price
        if currency is not UNSET:
            field_dict["currency"] = currency
        if requires_enrollment is not UNSET:
            field_dict["requires_enrollment"] = requires_enrollment
        if required_secrets is not UNSET:
            field_dict["required_secrets"] = required_secrets
        if optional_secrets is not UNSET:
            field_dict["optional_secrets"] = optional_secrets
        if default is not UNSET:
            field_dict["default"] = default
        if selector is not UNSET:
            field_dict["selector"] = selector
        if applicable_interfaces is not UNSET:
            field_dict["applicable_interfaces"] = applicable_interfaces
        if request_formats is not UNSET:
            field_dict["request_formats"] = request_formats

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.secret_requirement import SecretRequirement

        d = dict(src_dict)
        name = d.pop("name")

        channel_type = d.pop("channel_type")

        free = d.pop("free", UNSET)

        def _parse_price_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        price_description = _parse_price_description(d.pop("price_description", UNSET))

        def _parse_price(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        price = _parse_price(d.pop("price", UNSET))

        def _parse_currency(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        currency = _parse_currency(d.pop("currency", UNSET))

        requires_enrollment = d.pop("requires_enrollment", UNSET)

        _required_secrets = d.pop("required_secrets", UNSET)
        required_secrets: list[SecretRequirement] | Unset = UNSET
        if _required_secrets is not UNSET:
            required_secrets = []
            for required_secrets_item_data in _required_secrets:
                required_secrets_item = SecretRequirement.from_dict(required_secrets_item_data)

                required_secrets.append(required_secrets_item)

        _optional_secrets = d.pop("optional_secrets", UNSET)
        optional_secrets: list[SecretRequirement] | Unset = UNSET
        if _optional_secrets is not UNSET:
            optional_secrets = []
            for optional_secrets_item_data in _optional_secrets:
                optional_secrets_item = SecretRequirement.from_dict(optional_secrets_item_data)

                optional_secrets.append(optional_secrets_item)

        default = d.pop("default", UNSET)

        def _parse_selector(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        selector = _parse_selector(d.pop("selector", UNSET))

        def _parse_applicable_interfaces(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                applicable_interfaces_type_0 = cast(list[str], data)

                return applicable_interfaces_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        applicable_interfaces = _parse_applicable_interfaces(d.pop("applicable_interfaces", UNSET))

        def _parse_request_formats(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                request_formats_type_0 = cast(list[str], data)

                return request_formats_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        request_formats = _parse_request_formats(d.pop("request_formats", UNSET))

        channel_plan = cls(
            name=name,
            channel_type=channel_type,
            free=free,
            price_description=price_description,
            price=price,
            currency=currency,
            requires_enrollment=requires_enrollment,
            required_secrets=required_secrets,
            optional_secrets=optional_secrets,
            default=default,
            selector=selector,
            applicable_interfaces=applicable_interfaces,
            request_formats=request_formats,
        )

        channel_plan.additional_properties = d
        return channel_plan

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
