from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.enrollment_instance_fault_type_0 import (
    EnrollmentInstanceFaultType0,
    check_enrollment_instance_fault_type_0,
)
from ..models.enrollment_instance_requested_action import (
    EnrollmentInstanceRequestedAction,
    check_enrollment_instance_requested_action,
)
from ..models.enrollment_instance_status import EnrollmentInstanceStatus, check_enrollment_instance_status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.compute_component import ComputeComponent
    from ..models.enrollment_instance_entry import EnrollmentInstanceEntry


T = TypeVar("T", bound="EnrollmentInstance")


@_attrs_define
class EnrollmentInstance:
    """The instance of an enrollment: the request, how far it has got, and the pods."""

    enrollment_id: UUID
    requested_action: EnrollmentInstanceRequestedAction
    """ What was last asked of the instance """
    generation: int
    """ Identifies this request; a new start or stop raises it """
    status: EnrollmentInstanceStatus
    """ Progress of the request. A start is succeeded when every service is ready; a stop when the instance is gone.
    """
    entries: list[EnrollmentInstanceEntry]
    reason: None | str | Unset = UNSET
    """ Machine reason when the request failed """
    fault: EnrollmentInstanceFaultType0 | None | Unset = UNSET
    """ When the request failed, whose problem it is: the platform's (the cluster could not apply it) or the
    service's (a bad image or manifest, never ready). Null when it did not fail. """
    components: list[ComputeComponent] | None | Unset = UNSET
    """ Latest view of the pods, when the agent has reported them """
    started_at: datetime.datetime | None | Unset = UNSET
    finished_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enrollment_id = str(self.enrollment_id)

        requested_action: str = self.requested_action

        generation = self.generation

        status: str = self.status

        entries = []
        for entries_item_data in self.entries:
            entries_item = entries_item_data.to_dict()
            entries.append(entries_item)

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        fault: None | str | Unset
        if isinstance(self.fault, Unset):
            fault = UNSET
        elif isinstance(self.fault, str):
            fault = self.fault
        else:
            fault = self.fault

        components: list[dict[str, Any]] | None | Unset
        if isinstance(self.components, Unset):
            components = UNSET
        elif isinstance(self.components, list):
            components = []
            for components_type_0_item_data in self.components:
                components_type_0_item = components_type_0_item_data.to_dict()
                components.append(components_type_0_item)

        else:
            components = self.components

        started_at: None | str | Unset
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        finished_at: None | str | Unset
        if isinstance(self.finished_at, Unset):
            finished_at = UNSET
        elif isinstance(self.finished_at, datetime.datetime):
            finished_at = self.finished_at.isoformat()
        else:
            finished_at = self.finished_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enrollment_id": enrollment_id,
                "requested_action": requested_action,
                "generation": generation,
                "status": status,
                "entries": entries,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason
        if fault is not UNSET:
            field_dict["fault"] = fault
        if components is not UNSET:
            field_dict["components"] = components
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if finished_at is not UNSET:
            field_dict["finished_at"] = finished_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compute_component import ComputeComponent
        from ..models.enrollment_instance_entry import EnrollmentInstanceEntry

        d = dict(src_dict)
        enrollment_id = UUID(d.pop("enrollment_id"))

        requested_action = check_enrollment_instance_requested_action(d.pop("requested_action"))

        generation = d.pop("generation")

        status = check_enrollment_instance_status(d.pop("status"))

        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:
            entries_item = EnrollmentInstanceEntry.from_dict(entries_item_data)

            entries.append(entries_item)

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        def _parse_fault(data: object) -> EnrollmentInstanceFaultType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                fault_type_0 = check_enrollment_instance_fault_type_0(data)

                return fault_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EnrollmentInstanceFaultType0 | None | Unset, data)

        fault = _parse_fault(d.pop("fault", UNSET))

        def _parse_components(data: object) -> list[ComputeComponent] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                components_type_0 = []
                _components_type_0 = data
                for components_type_0_item_data in _components_type_0:
                    components_type_0_item = ComputeComponent.from_dict(components_type_0_item_data)

                    components_type_0.append(components_type_0_item)

                return components_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ComputeComponent] | None | Unset, data)

        components = _parse_components(d.pop("components", UNSET))

        def _parse_started_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        started_at = _parse_started_at(d.pop("started_at", UNSET))

        def _parse_finished_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                finished_at_type_0 = isoparse(data)

                return finished_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        finished_at = _parse_finished_at(d.pop("finished_at", UNSET))

        enrollment_instance = cls(
            enrollment_id=enrollment_id,
            requested_action=requested_action,
            generation=generation,
            status=status,
            entries=entries,
            reason=reason,
            fault=fault,
            components=components,
            started_at=started_at,
            finished_at=finished_at,
        )

        enrollment_instance.additional_properties = d
        return enrollment_instance

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
