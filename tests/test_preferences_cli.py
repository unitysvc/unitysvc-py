"""Tests for ``usvc preferences`` (unitysvc#2659).

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


def _preference(name: str, value: Any = None) -> dict[str, Any]:
    return {
        "name": name,
        "account": {"type": "user", "id": "u1", "name": "me"},
        "value": value,
        "effective": value,
        "source": "account" if value is not None else None,
        "can_edit": True,
    }


class _Sink:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    async def list(self) -> dict[str, Any]:
        self.calls.append(("list",))
        return {"data": [_preference("notification"), _preference("ai", {"service": "labs/llm-balanced"})]}

    async def get(self, name: str) -> dict[str, Any]:
        self.calls.append(("get", name))
        return _preference(name)

    async def set(self, name: str, value: Any = None) -> dict[str, Any]:
        self.calls.append(("set", name, value))
        return _preference(name, value)

    async def clear(self, name: str) -> dict[str, Any]:
        self.calls.append(("clear", name))
        return _preference(name)

    async def set_notification(self, service: str | None) -> dict[str, Any]:
        self.calls.append(("set_notification", service))
        return _preference("notification", service)

    async def set_ai(self, service: str | None) -> dict[str, Any]:
        self.calls.append(("set_ai", service))
        return _preference("ai", service)

    async def set_request_log_mode(self, mode: str | None) -> dict[str, Any]:
        self.calls.append(("set_request_log_mode", mode))
        return _preference("request-log", mode)


def _patch_sink(monkeypatch: pytest.MonkeyPatch) -> _Sink:
    sink = _Sink()

    @asynccontextmanager
    async def fake_async_client(api_key=None, base_url=None):  # type: ignore[no-untyped-def]
        yield SimpleNamespace(preferences=sink)

    monkeypatch.setattr("unitysvc.commands.preferences.async_client", fake_async_client)
    return sink


def test_list_prints_every_preference(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("list",)]
    assert "notification" in result.output
    assert "labs/llm-balanced" in result.output


def test_get_reads_one(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["get", "ai"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("get", "ai")]


def test_set_passes_name_and_string_value(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "request-log", "--value", "truncated"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("set", "request-log", "truncated")]
    assert "request-log" in result.output


def test_set_with_no_value_clears(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "request-log"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("set", "request-log", None)]


def test_set_json_flag_parses_value(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "ai", "--value", '{"service": "labs/llm-balanced"}', "--json"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("set", "ai", {"service": "labs/llm-balanced"})]


def test_set_json_flag_rejects_malformed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "ai", "--value", "{not json", "--json"])

    assert result.exit_code != 0
    assert "not valid JSON" in result.output


def test_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["clear", "notification"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("clear", "notification")]


@pytest.mark.parametrize(("command", "method"), [("notification", "set_notification"), ("ai", "set_ai")])
def test_service_conveniences(monkeypatch: pytest.MonkeyPatch, command: str, method: str) -> None:
    sink = _patch_sink(monkeypatch)

    set_result = runner.invoke(app, [command, "labs/discord-relay"])
    clear_result = runner.invoke(app, [command])

    assert set_result.exit_code == 0, set_result.output
    assert clear_result.exit_code == 0, clear_result.output
    assert sink.calls == [(method, "labs/discord-relay"), (method, None)]


def test_request_log_sets_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["request-log", "truncated"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("set_request_log_mode", "truncated")]


def test_request_log_with_no_arg_disables(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["request-log"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("set_request_log_mode", None)]


def test_request_log_rejects_unknown_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["request-log", "on"])

    assert result.exit_code != 0
    assert sink.calls == []
