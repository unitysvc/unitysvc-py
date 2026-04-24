from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerAccessInterface")


@_attrs_define
class CustomerAccessInterface:
    """Access interface entry exposed to customers.

    The actual ``api_key`` is never included — secrets are
    write-only. ``base_url`` is resolved against the active gateway
    config so the client can dispatch without further substitution.

    Scoping fields let the SDK filter the returned list:

    - ``enrollment_id`` — set when the interface is bound to a
      specific enrollment (BYOK/BYOE services); ``None`` for shared
      interfaces. SDK uses this for
      ``service.dispatch(enrollment=enr)`` resolution.
    - ``group_id`` — set when the interface is declared on a
      service group rather than on the service itself; ``None`` for
      per-service interfaces. Reserved; not yet populated by this
      endpoint.

    Intentionally omits:
    - ``is_primary`` — for most multi-interface services the
      interfaces are *different operations* (chat vs embeddings,
      put vs list), not alternatives, so a "primary" flag is
      misleading. Callers with more than one interface select
      explicitly via ``service.dispatch(interface="<name>")``.
    - ``is_active`` — only active interfaces are returned, so the
      field would always be ``True``.
    - ``sort_order`` — seller-internal ordering hint, used to
      sort this response but not surfaced to the customer.

    """

    id: UUID
    name: str
    description: None | str | Unset = UNSET
    access_method: None | str | Unset = UNSET
    base_url: None | str | Unset = UNSET
    group_id: None | Unset | UUID = UNSET
    enrollment_id: None | Unset | UUID = UNSET
    customer_secrets_needed: list[str] | None | Unset = UNSET
    customer_secrets_optional: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        access_method: None | str | Unset
        if isinstance(self.access_method, Unset):
            access_method = UNSET
        else:
            access_method = self.access_method

        base_url: None | str | Unset
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        group_id: None | str | Unset
        if isinstance(self.group_id, Unset):
            group_id = UNSET
        elif isinstance(self.group_id, UUID):
            group_id = str(self.group_id)
        else:
            group_id = self.group_id

        enrollment_id: None | str | Unset
        if isinstance(self.enrollment_id, Unset):
            enrollment_id = UNSET
        elif isinstance(self.enrollment_id, UUID):
            enrollment_id = str(self.enrollment_id)
        else:
            enrollment_id = self.enrollment_id

        customer_secrets_needed: list[str] | None | Unset
        if isinstance(self.customer_secrets_needed, Unset):
            customer_secrets_needed = UNSET
        elif isinstance(self.customer_secrets_needed, list):
            customer_secrets_needed = self.customer_secrets_needed

        else:
            customer_secrets_needed = self.customer_secrets_needed

        customer_secrets_optional: list[str] | None | Unset
        if isinstance(self.customer_secrets_optional, Unset):
            customer_secrets_optional = UNSET
        elif isinstance(self.customer_secrets_optional, list):
            customer_secrets_optional = self.customer_secrets_optional

        else:
            customer_secrets_optional = self.customer_secrets_optional

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if access_method is not UNSET:
            field_dict["access_method"] = access_method
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if enrollment_id is not UNSET:
            field_dict["enrollment_id"] = enrollment_id
        if customer_secrets_needed is not UNSET:
            field_dict["customer_secrets_needed"] = customer_secrets_needed
        if customer_secrets_optional is not UNSET:
            field_dict["customer_secrets_optional"] = customer_secrets_optional

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_access_method(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        access_method = _parse_access_method(d.pop("access_method", UNSET))

        def _parse_base_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        def _parse_group_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                group_id_type_0 = UUID(data)

                return group_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        group_id = _parse_group_id(d.pop("group_id", UNSET))

        def _parse_enrollment_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                enrollment_id_type_0 = UUID(data)

                return enrollment_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        enrollment_id = _parse_enrollment_id(d.pop("enrollment_id", UNSET))

        def _parse_customer_secrets_needed(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                customer_secrets_needed_type_0 = cast(list[str], data)

                return customer_secrets_needed_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        customer_secrets_needed = _parse_customer_secrets_needed(d.pop("customer_secrets_needed", UNSET))

        def _parse_customer_secrets_optional(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                customer_secrets_optional_type_0 = cast(list[str], data)

                return customer_secrets_optional_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        customer_secrets_optional = _parse_customer_secrets_optional(d.pop("customer_secrets_optional", UNSET))

        customer_access_interface = cls(
            id=id,
            name=name,
            description=description,
            access_method=access_method,
            base_url=base_url,
            group_id=group_id,
            enrollment_id=enrollment_id,
            customer_secrets_needed=customer_secrets_needed,
            customer_secrets_optional=customer_secrets_optional,
        )

        customer_access_interface.additional_properties = d
        return customer_access_interface

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
