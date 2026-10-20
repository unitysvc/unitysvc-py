from typing import Literal, cast

PreferencePublicSourceType0 = Literal["account", "default", "user"]

PREFERENCE_PUBLIC_SOURCE_TYPE_0_VALUES: set[PreferencePublicSourceType0] = {
    "account",
    "default",
    "user",
}


def check_preference_public_source_type_0(value: str) -> PreferencePublicSourceType0:
    if value in PREFERENCE_PUBLIC_SOURCE_TYPE_0_VALUES:
        return cast(PreferencePublicSourceType0, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PREFERENCE_PUBLIC_SOURCE_TYPE_0_VALUES!r}")
