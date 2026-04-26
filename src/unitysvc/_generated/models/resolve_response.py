from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resolve_candidate import ResolveCandidate
    from ..models.resolve_response_routing_strategy_type_0 import ResolveResponseRoutingStrategyType0


T = TypeVar("T", bound="ResolveResponse")


@_attrs_define
class ResolveResponse:
    """Dry-run result: candidate services, strategy, optional pre-pick."""

    candidates: list[ResolveCandidate]
    routing_strategy: None | ResolveResponseRoutingStrategyType0 | Unset = UNSET
    """ Effective strategy object (``{name, content_dependent, [timeout_ms], [parameters]}``), or ``None`` if the
    default ``weighted_random`` applies. ``content_dependent=True`` means final selection depends on the request
    body and the server can't pre-select — ``selected`` will be ``None``. """
    selected: None | ResolveCandidate | Unset = UNSET
    """ Pre-selected candidate for content-independent strategies (weighted random, by-price, by-latency, ...).
    ``None`` when the strategy is content-dependent — the caller must supply a body to get a deterministic pick. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.resolve_candidate import ResolveCandidate
        from ..models.resolve_response_routing_strategy_type_0 import ResolveResponseRoutingStrategyType0

        candidates = []
        for candidates_item_data in self.candidates:
            candidates_item = candidates_item_data.to_dict()
            candidates.append(candidates_item)

        routing_strategy: dict[str, Any] | None | Unset
        if isinstance(self.routing_strategy, Unset):
            routing_strategy = UNSET
        elif isinstance(self.routing_strategy, ResolveResponseRoutingStrategyType0):
            routing_strategy = self.routing_strategy.to_dict()
        else:
            routing_strategy = self.routing_strategy

        selected: dict[str, Any] | None | Unset
        if isinstance(self.selected, Unset):
            selected = UNSET
        elif isinstance(self.selected, ResolveCandidate):
            selected = self.selected.to_dict()
        else:
            selected = self.selected

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "candidates": candidates,
            }
        )
        if routing_strategy is not UNSET:
            field_dict["routing_strategy"] = routing_strategy
        if selected is not UNSET:
            field_dict["selected"] = selected

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resolve_candidate import ResolveCandidate
        from ..models.resolve_response_routing_strategy_type_0 import ResolveResponseRoutingStrategyType0

        d = dict(src_dict)
        candidates = []
        _candidates = d.pop("candidates")
        for candidates_item_data in _candidates:
            candidates_item = ResolveCandidate.from_dict(candidates_item_data)

            candidates.append(candidates_item)

        def _parse_routing_strategy(data: object) -> None | ResolveResponseRoutingStrategyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_strategy_type_0 = ResolveResponseRoutingStrategyType0.from_dict(data)

                return routing_strategy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ResolveResponseRoutingStrategyType0 | Unset, data)

        routing_strategy = _parse_routing_strategy(d.pop("routing_strategy", UNSET))

        def _parse_selected(data: object) -> None | ResolveCandidate | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                selected_type_0 = ResolveCandidate.from_dict(data)

                return selected_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ResolveCandidate | Unset, data)

        selected = _parse_selected(d.pop("selected", UNSET))

        resolve_response = cls(
            candidates=candidates,
            routing_strategy=routing_strategy,
            selected=selected,
        )

        resolve_response.additional_properties = d
        return resolve_response

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
