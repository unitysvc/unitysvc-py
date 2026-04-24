from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.gateway_kind import GatewayKind, check_gateway_kind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resolve_request_routing_key_type_0 import ResolveRequestRoutingKeyType0


T = TypeVar("T", bound="ResolveRequest")


@_attrs_define
class ResolveRequest:
    """Dry-run resolution input, mirroring what the gateway accepts."""

    path: str
    """ Gateway request path without the gateway base URL — same shape as what ``service.dispatch(path=...)`` /
    ``group.dispatch(path=...)`` produces. Examples: ``v1/chat/completions``, ``p/openai``, ``a/my-alias/foo``. """
    routing_key: None | ResolveRequestRoutingKeyType0 | Unset = UNSET
    """ Optional routing key the gateway would match against interface ``routing_key`` rules (e.g. ``{'model':
    'gpt-4'}``). Omit to see every interface matching the path. """
    strategy: None | str | Unset = UNSET
    """ Override the group's configured routing strategy (e.g. ``by_price``, ``lowest_latency``). Omit to use the
    strategy declared on the group's ``routing_policy``. ``weighted_random`` is the implicit baseline. """
    gateway: GatewayKind | Unset = UNSET
    """ Short-form gateway selector for ``ResolveRequest.gateway``.

    Customer-facing shorthand — maps to the ``<NAME>_GATEWAY_BASE_URL``
    settings template internally. ``api`` covers HTTP services (LLM,
    uptime monitors, generic APIs); ``s3`` and ``smtp`` cover storage
    and email relay. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.resolve_request_routing_key_type_0 import ResolveRequestRoutingKeyType0

        path = self.path

        routing_key: dict[str, Any] | None | Unset
        if isinstance(self.routing_key, Unset):
            routing_key = UNSET
        elif isinstance(self.routing_key, ResolveRequestRoutingKeyType0):
            routing_key = self.routing_key.to_dict()
        else:
            routing_key = self.routing_key

        strategy: None | str | Unset
        if isinstance(self.strategy, Unset):
            strategy = UNSET
        else:
            strategy = self.strategy

        gateway: str | Unset = UNSET
        if not isinstance(self.gateway, Unset):
            gateway = self.gateway

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
            }
        )
        if routing_key is not UNSET:
            field_dict["routing_key"] = routing_key
        if strategy is not UNSET:
            field_dict["strategy"] = strategy
        if gateway is not UNSET:
            field_dict["gateway"] = gateway

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resolve_request_routing_key_type_0 import ResolveRequestRoutingKeyType0

        d = dict(src_dict)
        path = d.pop("path")

        def _parse_routing_key(data: object) -> None | ResolveRequestRoutingKeyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_type_0 = ResolveRequestRoutingKeyType0.from_dict(data)

                return routing_key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ResolveRequestRoutingKeyType0 | Unset, data)

        routing_key = _parse_routing_key(d.pop("routing_key", UNSET))

        def _parse_strategy(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        strategy = _parse_strategy(d.pop("strategy", UNSET))

        _gateway = d.pop("gateway", UNSET)
        gateway: GatewayKind | Unset
        if isinstance(_gateway, Unset):
            gateway = UNSET
        else:
            gateway = check_gateway_kind(_gateway)

        resolve_request = cls(
            path=path,
            routing_key=routing_key,
            strategy=strategy,
            gateway=gateway,
        )

        resolve_request.additional_properties = d
        return resolve_request

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
