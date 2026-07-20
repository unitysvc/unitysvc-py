from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_document_detail import ServiceDocumentDetail


T = TypeVar("T", bound="ServiceDocumentsResponse")


@_attrs_define
class ServiceDocumentsResponse:
    """A service's documents, plus which interface they speak to (#1617).

    A service can expose several user access interfaces — a stable
    ``canonical`` URL, a ``latest`` alias — that usually differ only in
    ``base_url``. The documents are rendered against one of them, named by its
    key; the rest come back in ``available_interfaces`` so a caller can say
    "reachable via canonical / latest" and re-request another with
    ``?interface=<key>``.

    """

    interface: None | str | Unset = UNSET
    available_interfaces: list[str] | Unset = UNSET
    documents: list[ServiceDocumentDetail] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_document_detail import ServiceDocumentDetail

        interface: None | str | Unset
        if isinstance(self.interface, Unset):
            interface = UNSET
        else:
            interface = self.interface

        available_interfaces: list[str] | Unset = UNSET
        if not isinstance(self.available_interfaces, Unset):
            available_interfaces = self.available_interfaces

        documents: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.documents, Unset):
            documents = []
            for documents_item_data in self.documents:
                documents_item = documents_item_data.to_dict()
                documents.append(documents_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if interface is not UNSET:
            field_dict["interface"] = interface
        if available_interfaces is not UNSET:
            field_dict["available_interfaces"] = available_interfaces
        if documents is not UNSET:
            field_dict["documents"] = documents

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_document_detail import ServiceDocumentDetail

        d = dict(src_dict)

        def _parse_interface(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        interface = _parse_interface(d.pop("interface", UNSET))

        available_interfaces = cast(list[str], d.pop("available_interfaces", UNSET))

        _documents = d.pop("documents", UNSET)
        documents: list[ServiceDocumentDetail] | Unset = UNSET
        if _documents is not UNSET:
            documents = []
            for documents_item_data in _documents:
                documents_item = ServiceDocumentDetail.from_dict(documents_item_data)

                documents.append(documents_item)

        service_documents_response = cls(
            interface=interface,
            available_interfaces=available_interfaces,
            documents=documents,
        )

        service_documents_response.additional_properties = d
        return service_documents_response

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
