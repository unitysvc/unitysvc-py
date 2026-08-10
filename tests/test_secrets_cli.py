"""Tests for ``usvc secrets upload`` and its ``.env``-style manifest parser.

Parser and dry-run paths are fully offline; the upload loop monkeypatches
``async_client`` so no backend is required.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from unitysvc.commands.secrets import (
    ManifestResolutionError,
    _parse_secrets_text,
    _resolve_rhs,
    app,
)

runner = CliRunner()


# --- parser ---------------------------------------------------------------
def test_parse_extracts_values_and_descriptions() -> None:
    text = "# header\n\n# the base url\nBASE=https://x.example.com\nID='demo'\n"
    assert _parse_secrets_text(text, environ={}) == [
        ("BASE", "https://x.example.com", "the base url", None),
        ("ID", "demo", None, None),
    ]


def test_parse_resolves_env_expansion() -> None:
    text = "BASE=${BASE:-https://default.example.com}\nKEY=${KEY:-}\n"
    assert _parse_secrets_text(text, environ={"BASE": "https://real.example.com"}) == [
        ("BASE", "https://real.example.com", None, None),
        ("KEY", "", None, None),
    ]


def test_parse_multiline_description_and_header_separation() -> None:
    text = "# file header\n\n# line 1\n# line 2\nFOO=bar\n"
    assert _parse_secrets_text(text, environ={}) == [("FOO", "bar", "line 1\nline 2", None)]


# --- parser: trailing ``# variable`` marker -------------------------------
def test_parse_trailing_variable_marker_sets_sensitive_false() -> None:
    text = "# email\nNOTIFY_EMAIL=me@example.com   # variable\nKEY=sk-abc\n"
    assert _parse_secrets_text(text, environ={}) == [
        ("NOTIFY_EMAIL", "me@example.com", "email", False),
        ("KEY", "sk-abc", None, None),
    ]


def test_parse_variable_marker_case_insensitive_and_env_aware() -> None:
    text = "BASE=${BASE:-https://d.example}  # Variable\n"
    assert _parse_secrets_text(text, environ={"BASE": "https://real.example"}) == [
        ("BASE", "https://real.example", None, False),
    ]


def test_parse_non_marker_trailing_comment_stripped_but_stays_secret() -> None:
    assert _parse_secrets_text("TOK=sk-abc   # rotate me\n", environ={}) == [
        ("TOK", "sk-abc", None, None),
    ]


def test_parse_hash_in_value_preserved() -> None:
    # A ``#`` not preceded by whitespace is part of the value (quoted or not);
    # a trailing marker after a space is still honored.
    assert _parse_secrets_text('P="a b#c"   # variable\n', environ={}) == [
        ("P", "a b#c", None, False),
    ]
    assert _parse_secrets_text("TOK=a#b\n", environ={}) == [("TOK", "a#b", None, None)]


def test_double_quoted_expansion_is_resolved_not_literal() -> None:
    # Regression: a fully double-quoted ``${...}`` used to short-circuit and
    # upload the literal string. The shell expands inside double quotes, so we do
    # too — this is the exact form the committed manifests use.
    assert _resolve_rhs('"${ENDPOINT:-https://d.example}"', {}) == "https://d.example"
    assert _resolve_rhs('"${ENDPOINT:-https://d.example}"', {"ENDPOINT": "https://real"}) == "https://real"
    assert _resolve_rhs('"${KEY:-}"', {}) == ""


def test_single_quoted_expansion_stays_literal() -> None:
    # Single quotes are literal in the shell — no expansion.
    assert _resolve_rhs("'${KEY:-x}'", {"KEY": "real"}) == "${KEY:-x}"


def test_required_bare_expansion_errors_when_unset_or_empty() -> None:
    # ``${NAME}`` (no default) is required: unset or empty aborts, quoted or not.
    with pytest.raises(ManifestResolutionError) as exc:
        _resolve_rhs("${SECRET_KEY}", {})
    assert exc.value.name == "SECRET_KEY"
    with pytest.raises(ManifestResolutionError):
        _resolve_rhs('"${SECRET_KEY}"', {})  # quoted, still required
    with pytest.raises(ManifestResolutionError):
        _resolve_rhs("${SECRET_KEY}", {"SECRET_KEY": ""})  # set but empty


def test_required_bare_expansion_uses_env_when_set() -> None:
    assert _resolve_rhs("${SECRET_KEY}", {"SECRET_KEY": "s3cr3t"}) == "s3cr3t"
    assert _resolve_rhs('"${SECRET_KEY}"', {"SECRET_KEY": "s3cr3t"}) == "s3cr3t"


def test_parse_two_line_optional_then_required_unset() -> None:
    # Optional line followed by a required one for the same name: last assignment
    # wins, and the required (defaultless) form aborts.
    with pytest.raises(ManifestResolutionError) as exc:
        _parse_secrets_text('export K="${K:-}"\nexport K="${K}"\n', environ={})
    assert exc.value.name == "K"


# --- dry-run --------------------------------------------------------------
def test_dry_run_flags_descriptions(tmp_path: Path) -> None:
    f = tmp_path / "secrets.env.example"
    f.write_text("# guidance for A\nA=${A:-1}\nEMPTY=${EMPTY:-}\n")
    result = runner.invoke(app, ["upload", str(f), "--dry-run", "-f", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == [
        {"name": "A", "status": "would set (+desc)"},
        {"name": "EMPTY", "status": "would set"},
    ]


def test_empty_input_is_a_clean_noop() -> None:
    result = runner.invoke(app, ["upload", "-", "--dry-run"], input="# nothing\n")
    assert result.exit_code == 0
    assert "No secrets found" in result.output


def test_required_unset_aborts_with_clean_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A required ``${NAME}`` whose var is unset fails the upload (exit 1) with a
    # targeted message, rather than a traceback or a silent empty upload.
    monkeypatch.delenv("S3_RELAY_SECRET_KEY", raising=False)
    f = tmp_path / "secrets.env.example"
    f.write_text('export S3_RELAY_SECRET_KEY="${S3_RELAY_SECRET_KEY}"\n')
    result = runner.invoke(app, ["upload", str(f), "--dry-run"])
    assert result.exit_code == 1
    assert "S3_RELAY_SECRET_KEY" in result.output
    assert "required" in result.output.lower()


# --- upload path (mock) ---------------------------------------------------
class _Sink:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str | None, bool | None]] = []

    async def set(
        self,
        name: str,
        value: str,
        *,
        sensitive: bool | None = None,
        description: str | None = None,
    ) -> SimpleNamespace:
        self.calls.append((name, value, description, sensitive))
        return SimpleNamespace(name=name, sensitive=sensitive)


def _patch_sink(monkeypatch: pytest.MonkeyPatch) -> _Sink:
    sink = _Sink()

    @asynccontextmanager
    async def fake_async_client(api_key=None, base_url=None):  # type: ignore[no-untyped-def]
        yield SimpleNamespace(secrets=sink)

    monkeypatch.setattr("unitysvc.commands.secrets.async_client", fake_async_client)
    return sink


def test_upload_sets_every_entry_with_its_description(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    f = tmp_path / "secrets.env.example"
    f.write_text("# guidance for A\nA=1\nEMPTY=\n")
    result = runner.invoke(app, ["upload", str(f)])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("A", "1", "guidance for A", None), ("EMPTY", "", None, None)]
    assert "uploaded 2" in result.output


def test_upload_threads_variable_marker_as_sensitive_false(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    f = tmp_path / "secrets.env.example"
    f.write_text("NOTIFY_EMAIL=me@example.com  # variable\nKEY=sk-abc\n")
    result = runner.invoke(app, ["upload", str(f)])

    assert result.exit_code == 0, result.output
    assert sink.calls == [
        ("NOTIFY_EMAIL", "me@example.com", None, False),
        ("KEY", "sk-abc", None, None),
    ]
    assert "1 as variable(s)" in result.output
