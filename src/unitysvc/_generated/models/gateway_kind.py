from typing import Literal, cast

GatewayKind = Literal["api", "s3", "smtp"]

GATEWAY_KIND_VALUES: set[GatewayKind] = {
    "api",
    "s3",
    "smtp",
}


def check_gateway_kind(value: str) -> GatewayKind:
    if value in GATEWAY_KIND_VALUES:
        return cast(GatewayKind, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GATEWAY_KIND_VALUES!r}")
