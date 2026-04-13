from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.service_alias_public_request_routing_key_type_0 import ServiceAliasPublicRequestRoutingKeyType0
  from ..models.service_alias_public_routing_key_override_type_0 import ServiceAliasPublicRoutingKeyOverrideType0





T = TypeVar("T", bound="ServiceAliasPublic")



@_attrs_define
class ServiceAliasPublic:
    """ Public response model for ServiceAlias.

     """

    id: UUID
    customer_id: UUID
    name: str
    target_path: str
    created_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    request_routing_key: Union['ServiceAliasPublicRequestRoutingKeyType0', None, Unset] = UNSET
    routing_key_override: Union['ServiceAliasPublicRoutingKeyOverrideType0', None, Unset] = UNSET
    is_routing: Union[Unset, bool] = True
    updated_at: Union[None, Unset, datetime.datetime] = UNSET
    deactivated_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_alias_public_request_routing_key_type_0 import ServiceAliasPublicRequestRoutingKeyType0
        from ..models.service_alias_public_routing_key_override_type_0 import ServiceAliasPublicRoutingKeyOverrideType0
        id = str(self.id)

        customer_id = str(self.customer_id)

        name = self.name

        target_path = self.target_path

        created_at = self.created_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        request_routing_key: Union[None, Unset, dict[str, Any]]
        if isinstance(self.request_routing_key, Unset):
            request_routing_key = UNSET
        elif isinstance(self.request_routing_key, ServiceAliasPublicRequestRoutingKeyType0):
            request_routing_key = self.request_routing_key.to_dict()
        else:
            request_routing_key = self.request_routing_key

        routing_key_override: Union[None, Unset, dict[str, Any]]
        if isinstance(self.routing_key_override, Unset):
            routing_key_override = UNSET
        elif isinstance(self.routing_key_override, ServiceAliasPublicRoutingKeyOverrideType0):
            routing_key_override = self.routing_key_override.to_dict()
        else:
            routing_key_override = self.routing_key_override

        is_routing = self.is_routing

        updated_at: Union[None, Unset, str]
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        deactivated_at: Union[None, Unset, str]
        if isinstance(self.deactivated_at, Unset):
            deactivated_at = UNSET
        elif isinstance(self.deactivated_at, datetime.datetime):
            deactivated_at = self.deactivated_at.isoformat()
        else:
            deactivated_at = self.deactivated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "customer_id": customer_id,
            "name": name,
            "target_path": target_path,
            "created_at": created_at,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if request_routing_key is not UNSET:
            field_dict["request_routing_key"] = request_routing_key
        if routing_key_override is not UNSET:
            field_dict["routing_key_override"] = routing_key_override
        if is_routing is not UNSET:
            field_dict["is_routing"] = is_routing
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if deactivated_at is not UNSET:
            field_dict["deactivated_at"] = deactivated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_alias_public_request_routing_key_type_0 import ServiceAliasPublicRequestRoutingKeyType0
        from ..models.service_alias_public_routing_key_override_type_0 import ServiceAliasPublicRoutingKeyOverrideType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        customer_id = UUID(d.pop("customer_id"))




        name = d.pop("name")

        target_path = d.pop("target_path")

        created_at = isoparse(d.pop("created_at"))




        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_request_routing_key(data: object) -> Union['ServiceAliasPublicRequestRoutingKeyType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                request_routing_key_type_0 = ServiceAliasPublicRequestRoutingKeyType0.from_dict(data)



                return request_routing_key_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceAliasPublicRequestRoutingKeyType0', None, Unset], data)

        request_routing_key = _parse_request_routing_key(d.pop("request_routing_key", UNSET))


        def _parse_routing_key_override(data: object) -> Union['ServiceAliasPublicRoutingKeyOverrideType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_override_type_0 = ServiceAliasPublicRoutingKeyOverrideType0.from_dict(data)



                return routing_key_override_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceAliasPublicRoutingKeyOverrideType0', None, Unset], data)

        routing_key_override = _parse_routing_key_override(d.pop("routing_key_override", UNSET))


        is_routing = d.pop("is_routing", UNSET)

        def _parse_updated_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)



                return updated_at_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        def _parse_deactivated_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deactivated_at_type_0 = isoparse(data)



                return deactivated_at_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        deactivated_at = _parse_deactivated_at(d.pop("deactivated_at", UNSET))


        service_alias_public = cls(
            id=id,
            customer_id=customer_id,
            name=name,
            target_path=target_path,
            created_at=created_at,
            description=description,
            request_routing_key=request_routing_key,
            routing_key_override=routing_key_override,
            is_routing=is_routing,
            updated_at=updated_at,
            deactivated_at=deactivated_at,
        )


        service_alias_public.additional_properties = d
        return service_alias_public

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
