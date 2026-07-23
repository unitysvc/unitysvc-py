from typing import Literal, cast

AccessPlanEnrollmentMode = Literal["disallowed", "optional", "required"]

ACCESS_PLAN_ENROLLMENT_MODE_VALUES: set[AccessPlanEnrollmentMode] = {
    "disallowed",
    "optional",
    "required",
}


def check_access_plan_enrollment_mode(value: str) -> AccessPlanEnrollmentMode:
    if value in ACCESS_PLAN_ENROLLMENT_MODE_VALUES:
        return cast(AccessPlanEnrollmentMode, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ACCESS_PLAN_ENROLLMENT_MODE_VALUES!r}")
