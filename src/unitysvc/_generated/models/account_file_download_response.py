from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.account_file_download_response_scope import (
    AccountFileDownloadResponseScope,
    check_account_file_download_response_scope,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AccountFileDownloadResponse")


@_attrs_define
class AccountFileDownloadResponse:
    """Presigned download URL for one account file."""

    scope: AccountFileDownloadResponseScope
    key: str
    url: str
    expires_in: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        scope: str = self.scope

        key = self.key

        url = self.url

        expires_in = self.expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scope": scope,
                "key": key,
                "url": url,
                "expires_in": expires_in,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        scope = check_account_file_download_response_scope(d.pop("scope"))

        key = d.pop("key")

        url = d.pop("url")

        expires_in = d.pop("expires_in")

        account_file_download_response = cls(
            scope=scope,
            key=key,
            url=url,
            expires_in=expires_in,
        )

        account_file_download_response.additional_properties = d
        return account_file_download_response

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
