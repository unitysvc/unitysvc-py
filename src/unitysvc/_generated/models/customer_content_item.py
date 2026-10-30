from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_content_attachment import CustomerContentAttachment


T = TypeVar("T", bound="CustomerContentItem")


@_attrs_define
class CustomerContentItem:
    text: str
    public: bool | Unset = False
    attachments: list[CustomerContentAttachment] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        public = self.public

        attachments: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "text": text,
            }
        )
        if public is not UNSET:
            field_dict["public"] = public
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_content_attachment import CustomerContentAttachment

        d = dict(src_dict)
        text = d.pop("text")

        public = d.pop("public", UNSET)

        _attachments = d.pop("attachments", UNSET)
        attachments: list[CustomerContentAttachment] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = CustomerContentAttachment.from_dict(attachments_item_data)

                attachments.append(attachments_item)

        customer_content_item = cls(
            text=text,
            public=public,
            attachments=attachments,
        )

        return customer_content_item
