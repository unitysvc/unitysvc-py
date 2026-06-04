from typing import Literal, cast

BroadcastCreateMode = Literal["async", "sync"]

BROADCAST_CREATE_MODE_VALUES: set[BroadcastCreateMode] = {
    "async",
    "sync",
}


def check_broadcast_create_mode(value: str) -> BroadcastCreateMode:
    if value in BROADCAST_CREATE_MODE_VALUES:
        return cast(BroadcastCreateMode, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BROADCAST_CREATE_MODE_VALUES!r}")
