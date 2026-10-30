from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.service_enrollment_status_enum import ServiceEnrollmentStatusEnum, check_service_enrollment_status_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_enrollment_create_parameters_type_0 import ServiceEnrollmentCreateParametersType0
    from ..models.service_enrollment_create_policy_type_0_item import ServiceEnrollmentCreatePolicyType0Item


T = TypeVar("T", bound="ServiceEnrollmentCreate")


@_attrs_define
class ServiceEnrollmentCreate:
    """Model for creating new Enrollments.

    customer_id is derived from the X-Role-Id header at the route level.
    service_id references the Service identity layer (not listing_id).

    """

    service_id: UUID
    status: None | ServiceEnrollmentStatusEnum | Unset = UNSET
    parameters: None | ServiceEnrollmentCreateParametersType0 | Unset = UNSET
    channel: None | str | Unset = UNSET
    policy: list[ServiceEnrollmentCreatePolicyType0Item] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_enrollment_create_parameters_type_0 import ServiceEnrollmentCreateParametersType0

        service_id = str(self.service_id)

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status

        parameters: dict[str, Any] | None | Unset
        if isinstance(self.parameters, Unset):
            parameters = UNSET
        elif isinstance(self.parameters, ServiceEnrollmentCreateParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        channel: None | str | Unset
        if isinstance(self.channel, Unset):
            channel = UNSET
        else:
            channel = self.channel

        policy: list[dict[str, Any]] | None | Unset
        if isinstance(self.policy, Unset):
            policy = UNSET
        elif isinstance(self.policy, list):
            policy = []
            for policy_type_0_item_data in self.policy:
                policy_type_0_item = policy_type_0_item_data.to_dict()
                policy.append(policy_type_0_item)

        else:
            policy = self.policy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_id": service_id,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if channel is not UNSET:
            field_dict["channel"] = channel
        if policy is not UNSET:
            field_dict["policy"] = policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_enrollment_create_parameters_type_0 import ServiceEnrollmentCreateParametersType0
        from ..models.service_enrollment_create_policy_type_0_item import ServiceEnrollmentCreatePolicyType0Item

        d = dict(src_dict)
        service_id = UUID(d.pop("service_id"))

        def _parse_status(data: object) -> None | ServiceEnrollmentStatusEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_service_enrollment_status_enum(data)

                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceEnrollmentStatusEnum | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_parameters(data: object) -> None | ServiceEnrollmentCreateParametersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = ServiceEnrollmentCreateParametersType0.from_dict(data)

                return parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceEnrollmentCreateParametersType0 | Unset, data)

        parameters = _parse_parameters(d.pop("parameters", UNSET))

        def _parse_channel(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        channel = _parse_channel(d.pop("channel", UNSET))

        def _parse_policy(data: object) -> list[ServiceEnrollmentCreatePolicyType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                policy_type_0 = []
                _policy_type_0 = data
                for policy_type_0_item_data in _policy_type_0:
                    policy_type_0_item = ServiceEnrollmentCreatePolicyType0Item.from_dict(policy_type_0_item_data)

                    policy_type_0.append(policy_type_0_item)

                return policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ServiceEnrollmentCreatePolicyType0Item] | None | Unset, data)

        policy = _parse_policy(d.pop("policy", UNSET))

        service_enrollment_create = cls(
            service_id=service_id,
            status=status,
            parameters=parameters,
            channel=channel,
            policy=policy,
        )

        service_enrollment_create.additional_properties = d
        return service_enrollment_create

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
