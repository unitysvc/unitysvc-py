from typing import Literal, cast

BroadcastPublicMode = Literal["async", "sync"]

BROADCAST_PUBLIC_MODE_VALUES: set[BroadcastPublicMode] = {
    "async",
    "sync",
}


def check_broadcast_public_mode(value: str) -> BroadcastPublicMode:
    if value in BROADCAST_PUBLIC_MODE_VALUES:
        return cast(BroadcastPublicMode, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BROADCAST_PUBLIC_MODE_VALUES!r}")
