from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.routing_endpoint_plan_routing_key_type_0 import RoutingEndpointPlanRoutingKeyType0


T = TypeVar("T", bound="RoutingEndpointPlan")


@_attrs_define
class RoutingEndpointPlan:
    """A platform routing endpoint this service is *also* reachable through (#1692).

    A service in a routable platform group is callable at ``/g/<name>``, and one
    in a capability pool at ``/p/<name>`` — facts the service page could not
    otherwise learn. The contract is deliberately narrow: **the groups this
    service is in**, expressed as the URL that addresses them. It is not a
    "callable endpoints" list, and it makes no claim about the *kind* of group —
    ``base_url`` is the only signal, which is all a caller acts on.

    Every field here is frozen into the public OpenAPI schema, so the plan
    carries the three a consumer cannot derive locally and nothing else. The
    group's internal taxonomy (``group_type``, namespace) and its presentation
    (``display_name``) stay server-side. Entries are platform-owned and
    identical for every caller, which is what keeps the plan ``public``-cacheable;
    customer-owned routing objects get a separate, caller-scoped endpoint (#1692
    Part 2).

    """

    base_url: None | str | Unset = UNSET
    routing_key: None | RoutingEndpointPlanRoutingKeyType0 | Unset = UNSET
    routing_key_required: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.routing_endpoint_plan_routing_key_type_0 import RoutingEndpointPlanRoutingKeyType0

        base_url: None | str | Unset
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        routing_key: dict[str, Any] | None | Unset
        if isinstance(self.routing_key, Unset):
            routing_key = UNSET
        elif isinstance(self.routing_key, RoutingEndpointPlanRoutingKeyType0):
            routing_key = self.routing_key.to_dict()
        else:
            routing_key = self.routing_key

        routing_key_required = self.routing_key_required

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if routing_key is not UNSET:
            field_dict["routing_key"] = routing_key
        if routing_key_required is not UNSET:
            field_dict["routing_key_required"] = routing_key_required

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.routing_endpoint_plan_routing_key_type_0 import RoutingEndpointPlanRoutingKeyType0

        d = dict(src_dict)

        def _parse_base_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        def _parse_routing_key(data: object) -> None | RoutingEndpointPlanRoutingKeyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_type_0 = RoutingEndpointPlanRoutingKeyType0.from_dict(data)

                return routing_key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RoutingEndpointPlanRoutingKeyType0 | Unset, data)

        routing_key = _parse_routing_key(d.pop("routing_key", UNSET))

        routing_key_required = d.pop("routing_key_required", UNSET)

        routing_endpoint_plan = cls(
            base_url=base_url,
            routing_key=routing_key,
            routing_key_required=routing_key_required,
        )

        routing_endpoint_plan.additional_properties = d
        return routing_endpoint_plan

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
