from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.access_plan_enrollment_mode import AccessPlanEnrollmentMode, check_access_plan_enrollment_mode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_interface_plan import AccessInterfacePlan
    from ..models.channel_plan import ChannelPlan
    from ..models.parameter_requirement import ParameterRequirement


T = TypeVar("T", bound="AccessPlan")


@_attrs_define
class AccessPlan:
    """The generic, context-free access plan served to every consumer (#1638)."""

    enrollment_mode: AccessPlanEnrollmentMode | Unset = "disallowed"
    parameters: list[ParameterRequirement] | Unset = UNSET
    interfaces: list[AccessInterfacePlan] | Unset = UNSET
    channels: list[ChannelPlan] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_interface_plan import AccessInterfacePlan
        from ..models.channel_plan import ChannelPlan
        from ..models.parameter_requirement import ParameterRequirement

        enrollment_mode: str | Unset = UNSET
        if not isinstance(self.enrollment_mode, Unset):
            enrollment_mode = self.enrollment_mode

        parameters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)

        interfaces: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.interfaces, Unset):
            interfaces = []
            for interfaces_item_data in self.interfaces:
                interfaces_item = interfaces_item_data.to_dict()
                interfaces.append(interfaces_item)

        channels: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.channels, Unset):
            channels = []
            for channels_item_data in self.channels:
                channels_item = channels_item_data.to_dict()
                channels.append(channels_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enrollment_mode is not UNSET:
            field_dict["enrollment_mode"] = enrollment_mode
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if interfaces is not UNSET:
            field_dict["interfaces"] = interfaces
        if channels is not UNSET:
            field_dict["channels"] = channels

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_interface_plan import AccessInterfacePlan
        from ..models.channel_plan import ChannelPlan
        from ..models.parameter_requirement import ParameterRequirement

        d = dict(src_dict)
        _enrollment_mode = d.pop("enrollment_mode", UNSET)
        enrollment_mode: AccessPlanEnrollmentMode | Unset
        if isinstance(_enrollment_mode, Unset):
            enrollment_mode = UNSET
        else:
            enrollment_mode = check_access_plan_enrollment_mode(_enrollment_mode)

        _parameters = d.pop("parameters", UNSET)
        parameters: list[ParameterRequirement] | Unset = UNSET
        if _parameters is not UNSET:
            parameters = []
            for parameters_item_data in _parameters:
                parameters_item = ParameterRequirement.from_dict(parameters_item_data)

                parameters.append(parameters_item)

        _interfaces = d.pop("interfaces", UNSET)
        interfaces: list[AccessInterfacePlan] | Unset = UNSET
        if _interfaces is not UNSET:
            interfaces = []
            for interfaces_item_data in _interfaces:
                interfaces_item = AccessInterfacePlan.from_dict(interfaces_item_data)

                interfaces.append(interfaces_item)

        _channels = d.pop("channels", UNSET)
        channels: list[ChannelPlan] | Unset = UNSET
        if _channels is not UNSET:
            channels = []
            for channels_item_data in _channels:
                channels_item = ChannelPlan.from_dict(channels_item_data)

                channels.append(channels_item)

        access_plan = cls(
            enrollment_mode=enrollment_mode,
            parameters=parameters,
            interfaces=interfaces,
            channels=channels,
        )

        access_plan.additional_properties = d
        return access_plan

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
