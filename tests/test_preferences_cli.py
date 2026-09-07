"""Tests for ``usvc preferences`` (unitysvc#2063).

``async_client`` is monkeypatched so no backend is required — mirrors the
``_Sink`` pattern in ``test_secrets_cli.py``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any

import pytest
from typer.testing import CliRunner

from unitysvc.commands.preferences import app

runner = CliRunner()


class _Sink:
    def __init__(self) -> None:
        self.set_calls: list[tuple[str, Any]] = []
        self.notification_destination_calls: list[str | None] = []

    async def set(self, name: str, value: Any = None) -> SimpleNamespace:
        self.set_calls.append((name, value))
        return SimpleNamespace(preference={name: value})

    async def set_notification_destination(self, service: str | None) -> SimpleNamespace:
        self.notification_destination_calls.append(service)
        return SimpleNamespace(preference={"notification": {"destination": service}})


def _patch_sink(monkeypatch: pytest.MonkeyPatch) -> _Sink:
    sink = _Sink()

    @asynccontextmanager
    async def fake_async_client(api_key=None, base_url=None):  # type: ignore[no-untyped-def]
        yield SimpleNamespace(preferences=sink)

    monkeypatch.setattr("unitysvc.commands.preferences.async_client", fake_async_client)
    return sink


def test_set_passes_name_and_string_value(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "request-log", "--value", "truncated"])

    assert result.exit_code == 0, result.output
    assert sink.set_calls == [("request-log", "truncated")]
    assert "request-log" in result.output


def test_set_with_no_value_clears(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "request-log"])

    assert result.exit_code == 0, result.output
    assert sink.set_calls == [("request-log", None)]


def test_set_json_flag_parses_value(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "some-flag", "--value", "true", "--json"])

    assert result.exit_code == 0, result.output
    assert sink.set_calls == [("some-flag", True)]


def test_set_json_flag_rejects_malformed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "some-flag", "--value", "{not json", "--json"])

    assert result.exit_code != 0
    assert "not valid JSON" in result.output


def test_notification_destination_sets_service(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["notification-destination", "labs/discord-relay"])

    assert result.exit_code == 0, result.output
    assert sink.notification_destination_calls == ["labs/discord-relay"]


def test_notification_destination_with_no_arg_clears(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["notification-destination"])

    assert result.exit_code == 0, result.output
    assert sink.notification_destination_calls == [None]
