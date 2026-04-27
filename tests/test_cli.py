"""Smoke tests for the ``usvc`` CLI.

Uses Typer's CliRunner to exercise help output and argument parsing
without hitting the network. Deeper coverage will come with end-to-end
tests against a mock HTTP server once the backend surface stabilizes.
"""

from __future__ import annotations

import re

from typer.testing import CliRunner

from unitysvc.cli import app

runner = CliRunner()

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _plain(text: str) -> str:
    """Strip ANSI escapes and collapse whitespace.

    Rich's help output interleaves ANSI codes between characters and
    wraps lines based on terminal width — neither matters when checking
    that an option flag appears in the help, but both break naive
    substring matches in narrow CI terminals.
    """
    stripped = _ANSI_RE.sub("", text)
    return re.sub(r"\s+", " ", stripped)


def test_help_runs_cleanly() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    plain = _plain(result.stdout)
    assert "UnitySVC customer CLI" in plain
    for sub in ("secrets", "aliases", "recurrent-requests", "groups", "services", "enrollments", "resolve"):
        assert sub in plain


def test_secrets_help_lists_subcommands() -> None:
    result = runner.invoke(app, ["secrets", "--help"])
    assert result.exit_code == 0
    plain = _plain(result.stdout)
    for sub in ("list", "set", "delete"):
        assert sub in plain


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


# ---------------------------------------------------------------------------
# New command groups: smoke + arg parsing
# ---------------------------------------------------------------------------
def test_groups_help_lists_subcommands() -> None:
    result = runner.invoke(app, ["groups", "--help"])
    assert result.exit_code == 0
    plain = _plain(result.stdout)
    for sub in ("list", "show", "services", "dispatch"):
        assert sub in plain


def test_services_help_lists_subcommands() -> None:
    result = runner.invoke(app, ["services", "--help"])
    assert result.exit_code == 0
    plain = _plain(result.stdout)
    for sub in (
        "show",
        "interfaces",
        "dispatch",
        "schedule",
        "enroll",
        "required-secrets",
        "optional-secrets",
    ):
        assert sub in plain


def test_enrollments_help_lists_subcommands() -> None:
    result = runner.invoke(app, ["enrollments", "--help"])
    assert result.exit_code == 0
    plain = _plain(result.stdout)
    for sub in ("list", "show", "cancel"):
        assert sub in plain


def test_resolve_help_runs_cleanly() -> None:
    result = runner.invoke(app, ["resolve", "--help"])
    assert result.exit_code == 0
    plain = _plain(result.stdout)
    assert "--path" in plain
    assert "--routing-key" in plain


def test_groups_list_without_api_key_exits(monkeypatch) -> None:
    monkeypatch.delenv("UNITYSVC_API_KEY", raising=False)
    result = runner.invoke(app, ["groups", "list"])
    assert result.exit_code == 1
    assert "Missing customer API key" in result.stdout


def test_services_schedule_requires_a_recurrence_form(monkeypatch) -> None:
    monkeypatch.setenv("UNITYSVC_API_KEY", "svcpass_test")
    # Argument validation runs before any HTTP call, so this should
    # exit non-zero with a BadParameter message and never touch network.
    result = runner.invoke(
        app,
        ["services", "schedule", "00000000-0000-0000-0000-000000000000"],
    )
    assert result.exit_code != 0
    combined = _plain(result.output + (result.stderr or ""))
    assert "one of --recurrence, --interval, or --cron" in combined


def test_services_schedule_rejects_multiple_recurrence_forms(monkeypatch) -> None:
    monkeypatch.setenv("UNITYSVC_API_KEY", "svcpass_test")
    result = runner.invoke(
        app,
        [
            "services",
            "schedule",
            "00000000-0000-0000-0000-000000000000",
            "--interval",
            "60",
            "--cron",
            "* * * * *",
        ],
    )
    assert result.exit_code != 0
    assert "only one of" in _plain(result.output + (result.stderr or ""))


def test_services_dispatch_rejects_json_and_data_together(monkeypatch) -> None:
    monkeypatch.setenv("UNITYSVC_API_KEY", "svcpass_test")
    result = runner.invoke(
        app,
        [
            "services",
            "dispatch",
            "00000000-0000-0000-0000-000000000000",
            "--json",
            "{}",
            "--data",
            "raw",
        ],
    )
    assert result.exit_code != 0
    assert "mutually exclusive" in _plain(result.output + (result.stderr or ""))


def test_services_enroll_parses_parameter_pairs(monkeypatch) -> None:
    """``--parameter K=V`` should parse without complaint up to the network call."""
    from unitysvc.commands._helpers import parse_parameters

    out = parse_parameters('{"a": 1}', ["b=2", "c=hello world"])
    assert out == {"a": 1, "b": "2", "c": "hello world"}


def test_helpers_build_recurrence_interval_and_cron() -> None:
    from unitysvc.commands._helpers import build_recurrence

    assert build_recurrence(None, 300, None, "UTC") == {
        "schedule_type": "interval",
        "interval_seconds": 300,
    }
    assert build_recurrence(None, None, "*/5 * * * *", "America/Los_Angeles") == {
        "schedule_type": "cron",
        "cron_expression": "*/5 * * * *",
        "timezone": "America/Los_Angeles",
    }
    assert build_recurrence('{"schedule_type": "interval", "interval_seconds": 60}', None, None, "UTC") == {
        "schedule_type": "interval",
        "interval_seconds": 60,
    }


def test_helpers_parse_headers_and_json() -> None:
    from unitysvc.commands._helpers import parse_headers, parse_json_option

    assert parse_headers(None) is None
    assert parse_headers(["X-A: 1", "X-B:2"]) == {"X-A": "1", "X-B": "2"}
    assert parse_json_option(None) is None
    assert parse_json_option('{"a": 1}') == {"a": 1}
