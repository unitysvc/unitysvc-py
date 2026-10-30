from typing import Literal, cast

ProfileAccountPublicType = Literal["customer", "seller"]

PROFILE_ACCOUNT_PUBLIC_TYPE_VALUES: set[ProfileAccountPublicType] = {
    "customer",
    "seller",
}


def check_profile_account_public_type(value: str) -> ProfileAccountPublicType:
    if value in PROFILE_ACCOUNT_PUBLIC_TYPE_VALUES:
        return cast(ProfileAccountPublicType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PROFILE_ACCOUNT_PUBLIC_TYPE_VALUES!r}")
