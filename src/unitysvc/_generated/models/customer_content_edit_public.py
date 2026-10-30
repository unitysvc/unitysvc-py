from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.profile_account_public import ProfileAccountPublic
    from ..models.values import Values


T = TypeVar("T", bound="CustomerContentEditPublic")


@_attrs_define
class CustomerContentEditPublic:
    """Private account editor for one matching document; version is a revision."""

    account: ProfileAccountPublic
    version: int
    values: Values
    can_edit: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        account = self.account.to_dict()

        version = self.version

        values = self.values.to_dict()

        can_edit = self.can_edit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "account": account,
                "version": version,
                "values": values,
                "can_edit": can_edit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_account_public import ProfileAccountPublic
        from ..models.values import Values

        d = dict(src_dict)
        account = ProfileAccountPublic.from_dict(d.pop("account"))

        version = d.pop("version")

        values = Values.from_dict(d.pop("values"))

        can_edit = d.pop("can_edit")

        customer_content_edit_public = cls(
            account=account,
            version=version,
            values=values,
            can_edit=can_edit,
        )

        customer_content_edit_public.additional_properties = d
        return customer_content_edit_public

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
