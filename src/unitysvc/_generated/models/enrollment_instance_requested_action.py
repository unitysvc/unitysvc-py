from typing import Literal, cast

EnrollmentInstanceRequestedAction = Literal["start", "stop"]

ENROLLMENT_INSTANCE_REQUESTED_ACTION_VALUES: set[EnrollmentInstanceRequestedAction] = {
    "start",
    "stop",
}


def check_enrollment_instance_requested_action(value: str) -> EnrollmentInstanceRequestedAction:
    if value in ENROLLMENT_INSTANCE_REQUESTED_ACTION_VALUES:
        return cast(EnrollmentInstanceRequestedAction, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ENROLLMENT_INSTANCE_REQUESTED_ACTION_VALUES!r}")
