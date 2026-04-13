from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID

if TYPE_CHECKING:
  from ..models.service_alias_public import ServiceAliasPublic





T = TypeVar("T", bound="SwitchRoutingResponse")



@_attrs_define
class SwitchRoutingResponse:
    """ Response from ``POST /aliases/{id}/switch``.

     """

    alias: 'ServiceAliasPublic'
    """ Public response model for ServiceAlias. """
    demoted_alias_id: Union[None, UUID, Unset] = UNSET
    """ ID of the sibling alias that was demoted when switching on. Null when switching off or when no sibling was
    routing. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_alias_public import ServiceAliasPublic
        alias = self.alias.to_dict()

        demoted_alias_id: Union[None, Unset, str]
        if isinstance(self.demoted_alias_id, Unset):
            demoted_alias_id = UNSET
        elif isinstance(self.demoted_alias_id, UUID):
            demoted_alias_id = str(self.demoted_alias_id)
        else:
            demoted_alias_id = self.demoted_alias_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "alias": alias,
        })
        if demoted_alias_id is not UNSET:
            field_dict["demoted_alias_id"] = demoted_alias_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_alias_public import ServiceAliasPublic
        d = dict(src_dict)
        alias = ServiceAliasPublic.from_dict(d.pop("alias"))




        def _parse_demoted_alias_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                demoted_alias_id_type_0 = UUID(data)



                return demoted_alias_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        demoted_alias_id = _parse_demoted_alias_id(d.pop("demoted_alias_id", UNSET))


        switch_routing_response = cls(
            alias=alias,
            demoted_alias_id=demoted_alias_id,
        )


        switch_routing_response.additional_properties = d
        return switch_routing_response

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
