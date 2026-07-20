from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_category_enum import DocumentCategoryEnum, check_document_category_enum
from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceDocumentDetail")


@_attrs_define
class ServiceDocumentDetail:
    """A document plus its content.

    Renderable documents (code examples, connectivity tests) come back
    **rendered against one user access interface** — gateway base URL
    substituted, ``.j2`` stripped from the filename — so ``content`` is
    something the caller can run, not a template full of placeholders. This
    matches what the frontend asks for when it renders an example.

    The interface the content was rendered against is a response-level fact —
    every renderable document in a response uses the same one — so it lives on
    the enclosing ``ServiceDocumentsResponse.interface`` rather than being
    repeated here.

    ``content`` is None when the document is stored as a URL or a binary the
    caller should fetch itself; follow ``external_url`` in that case.

    """

    id: UUID
    title: str
    category: DocumentCategoryEnum
    mime_type: str
    description: None | str | Unset = UNSET
    version: None | str | Unset = UNSET
    sort_order: int | Unset = 0
    external_url: None | str | Unset = UNSET
    filename: None | str | Unset = UNSET
    content: None | str | Unset = UNSET
    render_error: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        title = self.title

        category: str = self.category

        mime_type = self.mime_type

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        version: None | str | Unset
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        sort_order = self.sort_order

        external_url: None | str | Unset
        if isinstance(self.external_url, Unset):
            external_url = UNSET
        else:
            external_url = self.external_url

        filename: None | str | Unset
        if isinstance(self.filename, Unset):
            filename = UNSET
        else:
            filename = self.filename

        content: None | str | Unset
        if isinstance(self.content, Unset):
            content = UNSET
        else:
            content = self.content

        render_error: None | str | Unset
        if isinstance(self.render_error, Unset):
            render_error = UNSET
        else:
            render_error = self.render_error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "category": category,
                "mime_type": mime_type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if version is not UNSET:
            field_dict["version"] = version
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order
        if external_url is not UNSET:
            field_dict["external_url"] = external_url
        if filename is not UNSET:
            field_dict["filename"] = filename
        if content is not UNSET:
            field_dict["content"] = content
        if render_error is not UNSET:
            field_dict["render_error"] = render_error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        title = d.pop("title")

        category = check_document_category_enum(d.pop("category"))

        mime_type = d.pop("mime_type")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        version = _parse_version(d.pop("version", UNSET))

        sort_order = d.pop("sort_order", UNSET)

        def _parse_external_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_url = _parse_external_url(d.pop("external_url", UNSET))

        def _parse_filename(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        filename = _parse_filename(d.pop("filename", UNSET))

        def _parse_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        content = _parse_content(d.pop("content", UNSET))

        def _parse_render_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        render_error = _parse_render_error(d.pop("render_error", UNSET))

        service_document_detail = cls(
            id=id,
            title=title,
            category=category,
            mime_type=mime_type,
            description=description,
            version=version,
            sort_order=sort_order,
            external_url=external_url,
            filename=filename,
            content=content,
            render_error=render_error,
        )

        service_document_detail.additional_properties = d
        return service_document_detail

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
