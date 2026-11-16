from typing import Literal, cast

EnrollmentInstanceFaultType0 = Literal["platform", "seller"]

ENROLLMENT_INSTANCE_FAULT_TYPE_0_VALUES: set[EnrollmentInstanceFaultType0] = {
    "platform",
    "seller",
}


def check_enrollment_instance_fault_type_0(value: str) -> EnrollmentInstanceFaultType0:
    if value in ENROLLMENT_INSTANCE_FAULT_TYPE_0_VALUES:
        return cast(EnrollmentInstanceFaultType0, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ENROLLMENT_INSTANCE_FAULT_TYPE_0_VALUES!r}")
