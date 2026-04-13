"""Unit tests for :mod:`unitysvc._http` (response unwrapping)."""

from __future__ import annotations

import pytest

from unitysvc import (
    APIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)
from unitysvc._http import unwrap


class _FakeResponse:
    """Minimal stand-in for the generated ``Response`` object."""

    def __init__(self, status_code: int, parsed: object | None = None, content: bytes = b"") -> None:
        self.status_code = status_code
        self.parsed = parsed
        self.content = content


def test_unwrap_success_returns_parsed() -> None:
    body = {"name": "openai-key"}
    assert unwrap(_FakeResponse(200, parsed=body)) == body


def test_unwrap_204_returns_none() -> None:
    assert unwrap(_FakeResponse(204, parsed=None, content=b"")) is None


def test_unwrap_401_raises_authentication_error() -> None:
    with pytest.raises(AuthenticationError) as excinfo:
        unwrap(_FakeResponse(401, content=b'{"detail":"bad key"}'))
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == {"detail": "bad key"}


def test_unwrap_404_raises_not_found() -> None:
    with pytest.raises(NotFoundError) as excinfo:
        unwrap(_FakeResponse(404, content=b'{"detail":"missing"}'))
    assert excinfo.value.status_code == 404


def test_unwrap_422_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        unwrap(_FakeResponse(422, content=b'{"detail":"bad body"}'))


def test_unwrap_non_json_body_is_passed_through_as_bytes() -> None:
    with pytest.raises(APIError) as excinfo:
        unwrap(_FakeResponse(500, content=b"<html>boom</html>"))
    assert excinfo.value.status_code == 500
    # Non-JSON bodies are surfaced as raw bytes in `detail`.
    assert excinfo.value.detail == b"<html>boom</html>"
