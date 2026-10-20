from typing import Literal, cast

PreferenceAccountPublicType = Literal["customer", "seller", "user"]

PREFERENCE_ACCOUNT_PUBLIC_TYPE_VALUES: set[PreferenceAccountPublicType] = {
    "customer",
    "seller",
    "user",
}


def check_preference_account_public_type(value: str) -> PreferenceAccountPublicType:
    if value in PREFERENCE_ACCOUNT_PUBLIC_TYPE_VALUES:
        return cast(PreferenceAccountPublicType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PREFERENCE_ACCOUNT_PUBLIC_TYPE_VALUES!r}")
