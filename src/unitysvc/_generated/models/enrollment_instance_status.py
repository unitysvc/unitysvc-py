from typing import Literal, cast

EnrollmentInstanceStatus = Literal["failed", "in_progress", "pending", "succeeded"]

ENROLLMENT_INSTANCE_STATUS_VALUES: set[EnrollmentInstanceStatus] = {
    "failed",
    "in_progress",
    "pending",
    "succeeded",
}


def check_enrollment_instance_status(value: str) -> EnrollmentInstanceStatus:
    if value in ENROLLMENT_INSTANCE_STATUS_VALUES:
        return cast(EnrollmentInstanceStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ENROLLMENT_INSTANCE_STATUS_VALUES!r}")
