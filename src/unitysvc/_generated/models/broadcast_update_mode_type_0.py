from typing import Literal, cast

BroadcastUpdateModeType0 = Literal["async", "sync"]

BROADCAST_UPDATE_MODE_TYPE_0_VALUES: set[BroadcastUpdateModeType0] = {
    "async",
    "sync",
}


def check_broadcast_update_mode_type_0(value: str) -> BroadcastUpdateModeType0:
    if value in BROADCAST_UPDATE_MODE_TYPE_0_VALUES:
        return cast(BroadcastUpdateModeType0, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BROADCAST_UPDATE_MODE_TYPE_0_VALUES!r}")
