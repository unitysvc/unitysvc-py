"""Smoke tests for the ``usvc`` CLI.

Uses Typer's CliRunner to exercise help output and argument parsing
without hitting the network. Deeper coverage will come with end-to-end
tests against a mock HTTP server once the backend surface stabilizes.
"""

from __future__ import annotations

from typer.testing import CliRunner

from unitysvc.cli import app

runner = CliRunner()


def test_help_runs_cleanly() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "UnitySVC customer CLI" in result.stdout
    assert "secrets" in result.stdout
    assert "aliases" in result.stdout
    assert "recurrent-requests" in result.stdout


def test_secrets_help_lists_subcommands() -> None:
    result = runner.invoke(app, ["secrets", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "set" in result.stdout
    assert "delete" in result.stdout


def test_env_command_prints_defaults(monkeypatch) -> None:
    monkeypatch.delenv("UNITYSVC_API_KEY", raising=False)
    monkeypatch.delenv("UNITYSVC_API_URL", raising=False)
    monkeypatch.delenv("UNITYSVC_API_BASE_URL", raising=False)
    monkeypatch.delenv("UNITYSVC_S3_BASE_URL", raising=False)
    monkeypatch.delenv("UNITYSVC_SMTP_BASE_URL", raising=False)

    result = runner.invoke(app, ["env"])
    assert result.exit_code == 0
    assert "UNITYSVC_API_KEY" in result.stdout
    assert "UNITYSVC_API_URL" in result.stdout
    assert "UNITYSVC_API_BASE_URL" in result.stdout


def test_secrets_list_without_api_key_exits(monkeypatch) -> None:
    monkeypatch.delenv("UNITYSVC_API_KEY", raising=False)
    result = runner.invoke(app, ["secrets", "list"])
    assert result.exit_code == 1
    assert "Missing customer API key" in result.stdout
