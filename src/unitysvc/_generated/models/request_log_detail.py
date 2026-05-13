from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sanitized_error_info import SanitizedErrorInfo
    from ..models.upstream_response_info import UpstreamResponseInfo
    from ..models.usage_event_info import UsageEventInfo
    from ..models.user_request_info import UserRequestInfo


T = TypeVar("T", bound="RequestLogDetail")


@_attrs_define
class RequestLogDetail:
    """Customer-facing request log detail (#1032 / #882).

    Includes the customer's own request and the upstream response —
    the two pieces a customer needs to debug their own traffic.
    Deliberately omits ``gateway_request`` (transformed body, upstream
    URL, seller's upstream credentials) since exposing it would leak
    the seller's upstream identity and credential material to customers.

    Bodies are returned truncated to the inline cap by default. When
    ``truncate_long_message=false`` and the body was stored in full
    (``complete`` mode at write-time), the detail endpoint fetches the
    full body from S3 and substitutes it into the response — the
    shape stays the same.

    """

    log_id: str
    event_id: str
    event_timestamp: str
    gateway_source: str
    customer_id: str
    user_id: str
    user_request: UserRequestInfo
    """ User's original request details. """
    service_id: None | str | Unset = UNSET
    service_enrollment_id: None | str | Unset = UNSET
    upstream_response: None | Unset | UpstreamResponseInfo = UNSET
    usage_event: None | Unset | UsageEventInfo = UNSET
    error: None | SanitizedErrorInfo | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sanitized_error_info import SanitizedErrorInfo
        from ..models.upstream_response_info import UpstreamResponseInfo
        from ..models.usage_event_info import UsageEventInfo
        from ..models.user_request_info import UserRequestInfo

        log_id = self.log_id

        event_id = self.event_id

        event_timestamp = self.event_timestamp

        gateway_source = self.gateway_source

        customer_id = self.customer_id

        user_id = self.user_id

        user_request = self.user_request.to_dict()

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        else:
            service_id = self.service_id

        service_enrollment_id: None | str | Unset
        if isinstance(self.service_enrollment_id, Unset):
            service_enrollment_id = UNSET
        else:
            service_enrollment_id = self.service_enrollment_id

        upstream_response: dict[str, Any] | None | Unset
        if isinstance(self.upstream_response, Unset):
            upstream_response = UNSET
        elif isinstance(self.upstream_response, UpstreamResponseInfo):
            upstream_response = self.upstream_response.to_dict()
        else:
            upstream_response = self.upstream_response

        usage_event: dict[str, Any] | None | Unset
        if isinstance(self.usage_event, Unset):
            usage_event = UNSET
        elif isinstance(self.usage_event, UsageEventInfo):
            usage_event = self.usage_event.to_dict()
        else:
            usage_event = self.usage_event

        error: dict[str, Any] | None | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        elif isinstance(self.error, SanitizedErrorInfo):
            error = self.error.to_dict()
        else:
            error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "log_id": log_id,
                "event_id": event_id,
                "event_timestamp": event_timestamp,
                "gateway_source": gateway_source,
                "customer_id": customer_id,
                "user_id": user_id,
                "user_request": user_request,
            }
        )
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if service_enrollment_id is not UNSET:
            field_dict["service_enrollment_id"] = service_enrollment_id
        if upstream_response is not UNSET:
            field_dict["upstream_response"] = upstream_response
        if usage_event is not UNSET:
            field_dict["usage_event"] = usage_event
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sanitized_error_info import SanitizedErrorInfo
        from ..models.upstream_response_info import UpstreamResponseInfo
        from ..models.usage_event_info import UsageEventInfo
        from ..models.user_request_info import UserRequestInfo

        d = dict(src_dict)
        log_id = d.pop("log_id")

        event_id = d.pop("event_id")

        event_timestamp = d.pop("event_timestamp")

        gateway_source = d.pop("gateway_source")

        customer_id = d.pop("customer_id")

        user_id = d.pop("user_id")

        user_request = UserRequestInfo.from_dict(d.pop("user_request"))

        def _parse_service_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))

        def _parse_service_enrollment_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_enrollment_id = _parse_service_enrollment_id(d.pop("service_enrollment_id", UNSET))

        def _parse_upstream_response(data: object) -> None | Unset | UpstreamResponseInfo:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                upstream_response_type_0 = UpstreamResponseInfo.from_dict(data)

                return upstream_response_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpstreamResponseInfo, data)

        upstream_response = _parse_upstream_response(d.pop("upstream_response", UNSET))

        def _parse_usage_event(data: object) -> None | Unset | UsageEventInfo:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                usage_event_type_0 = UsageEventInfo.from_dict(data)

                return usage_event_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UsageEventInfo, data)

        usage_event = _parse_usage_event(d.pop("usage_event", UNSET))

        def _parse_error(data: object) -> None | SanitizedErrorInfo | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_type_0 = SanitizedErrorInfo.from_dict(data)

                return error_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SanitizedErrorInfo | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        request_log_detail = cls(
            log_id=log_id,
            event_id=event_id,
            event_timestamp=event_timestamp,
            gateway_source=gateway_source,
            customer_id=customer_id,
            user_id=user_id,
            user_request=user_request,
            service_id=service_id,
            service_enrollment_id=service_enrollment_id,
            upstream_response=upstream_response,
            usage_event=usage_event,
            error=error,
        )

        request_log_detail.additional_properties = d
        return request_log_detail

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
