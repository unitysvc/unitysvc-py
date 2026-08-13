"""Tests for ``usvc.commands`` subcommand discovery.

The contract under test: ``usvc`` mounts subcommands advertised by *other*
packages without importing or naming them, and does so without the eager import
cost that would make ``usvc --help`` pay for every installed plugin.
"""

from __future__ import annotations

from importlib.metadata import EntryPoint

import click
import pytest
import typer
from typer.testing import CliRunner

from unitysvc import _plugins
from unitysvc.cli import app

runner = CliRunner()


def output_of(result) -> str:
    """stdout plus stderr — Click routes errors to stderr and CliRunner keeps them apart."""
    return result.stdout + (result.stderr or "")


@pytest.fixture
def no_path_plugins(monkeypatch):
    """Ignore whatever usvc-* executables happen to be on the developer's PATH."""
    monkeypatch.setattr(_plugins, "path_plugins", lambda: set())
    monkeypatch.setattr(_plugins, "path_executable", lambda name: None)


def _fake_entry_point(name: str, target: object, monkeypatch) -> None:
    ep = EntryPoint(name=name, value="fake.module:app", group=_plugins.GROUP)
    monkeypatch.setattr(_plugins, "entry_point_plugins", lambda: {name: ep})
    monkeypatch.setattr(EntryPoint, "load", lambda self: target)


class TestDiscovery:
    def test_no_plugins_installed_lists_only_builtins(self, no_path_plugins, monkeypatch):
        """A customer with only unitysvc-py must not see seller commands."""
        monkeypatch.setattr(_plugins, "entry_point_plugins", dict)
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "seller" not in result.stdout

    def test_advertised_plugin_appears_in_help(self, no_path_plugins, monkeypatch):
        plugin = typer.Typer(help="Seller-side operations.")

        @plugin.command()
        def noop() -> None: ...

        _fake_entry_point("seller", plugin, monkeypatch)
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "seller" in result.stdout

    def test_listing_help_does_not_import_the_plugin(self, no_path_plugins, monkeypatch):
        """Names come from metadata; the target module stays unimported.

        This is what keeps ``usvc --help`` cheap regardless of what a plugin
        drags in (jinja2, mistune, ...).
        """
        loaded = []
        ep = EntryPoint(name="seller", value="fake:app", group=_plugins.GROUP)
        monkeypatch.setattr(_plugins, "entry_point_plugins", lambda: {"seller": ep})
        monkeypatch.setattr(EntryPoint, "load", lambda self: loaded.append(1))

        runner.invoke(app, ["--help"])
        assert loaded == [], "rendering --help imported a plugin"

    def test_plugin_runs_when_invoked(self, no_path_plugins, monkeypatch):
        plugin = typer.Typer()

        @plugin.callback()
        def _root() -> None:
            """Seller-side operations."""

        @plugin.command()
        def ping() -> None:
            print("pong from plugin")

        _fake_entry_point("seller", plugin, monkeypatch)
        result = runner.invoke(app, ["seller", "ping"])
        assert result.exit_code == 0
        assert "pong from plugin" in result.stdout


class TestPrecedence:
    def test_builtin_wins_over_plugin(self, monkeypatch):
        """A plugin must never shadow a real subcommand."""
        hijack = typer.Typer()

        @hijack.command()
        def evil() -> None:
            print("hijacked")

        _fake_entry_point("services", hijack, monkeypatch)
        monkeypatch.setattr(_plugins, "path_executable", lambda name: "/bin/false")

        result = runner.invoke(app, ["services", "--help"])
        assert "hijacked" not in result.stdout

    def test_entry_point_preferred_over_path(self, monkeypatch):
        plugin = typer.Typer()

        @plugin.callback()
        def _root() -> None:
            """Seller-side operations."""

        @plugin.command()
        def ping() -> None:
            print("from entry point")

        _fake_entry_point("seller", plugin, monkeypatch)
        monkeypatch.setattr(_plugins, "path_executable", lambda name: "/definitely/not/an/executable")

        result = runner.invoke(app, ["seller", "ping"])
        assert result.exit_code == 0
        assert "from entry point" in result.stdout


class TestPathFallback:
    def test_path_executable_prefers_hyphen_over_underscore(self, monkeypatch):
        seen = []

        def fake_which(candidate):
            seen.append(candidate)
            return "/usr/bin/" + candidate if candidate == "usvc_seller" else None

        monkeypatch.setattr(_plugins.shutil, "which", fake_which)
        assert _plugins.path_executable("seller") == "/usr/bin/usvc_seller"
        assert seen == ["usvc-seller", "usvc_seller"], "hyphen must be tried first"

    def test_dispatch_execs_with_remaining_argv(self, monkeypatch):
        monkeypatch.setattr(_plugins, "entry_point_plugins", dict)
        monkeypatch.setattr(_plugins, "path_executable", lambda name: "/usr/bin/usvc-seller")
        monkeypatch.setattr(_plugins.os, "name", "posix")

        captured = {}
        monkeypatch.setattr(_plugins.os, "execv", lambda exe, argv: captured.update(exe=exe, argv=argv))

        runner.invoke(app, ["seller", "specs", "validate", "--force"])
        assert captured["exe"] == "/usr/bin/usvc-seller"
        assert captured["argv"] == ["/usr/bin/usvc-seller", "specs", "validate", "--force"]

    def test_plugin_help_is_passed_through_not_intercepted(self, monkeypatch):
        """``usvc seller --help`` must reach the plugin, not print ours."""
        monkeypatch.setattr(_plugins, "entry_point_plugins", dict)
        monkeypatch.setattr(_plugins, "path_executable", lambda name: "/usr/bin/usvc-seller")
        monkeypatch.setattr(_plugins.os, "name", "posix")

        captured = {}
        monkeypatch.setattr(_plugins.os, "execv", lambda exe, argv: captured.update(argv=argv))

        runner.invoke(app, ["seller", "--help"])
        assert captured["argv"] == ["/usr/bin/usvc-seller", "--help"]


class TestFailureModes:
    def test_broken_plugin_does_not_break_the_cli(self, no_path_plugins, monkeypatch):
        ep = EntryPoint(name="seller", value="fake:app", group=_plugins.GROUP)
        monkeypatch.setattr(_plugins, "entry_point_plugins", lambda: {"seller": ep})

        def explode(self):
            raise ModuleNotFoundError("No module named 'unitysvc_sellers'")

        monkeypatch.setattr(EntryPoint, "load", explode)

        assert runner.invoke(app, ["--help"]).exit_code == 0, "one bad plugin took down --help"
        result = runner.invoke(app, ["seller"])
        assert result.exit_code != 0
        assert "failed to load" in output_of(result)

    def test_unknown_first_party_command_suggests_the_package(self, no_path_plugins, monkeypatch):
        monkeypatch.setattr(_plugins, "entry_point_plugins", dict)
        result = runner.invoke(app, ["seller"])
        assert result.exit_code != 0
        assert "unitysvc-sellers" in output_of(result)

    def test_unknown_unrelated_command_still_errors_plainly(self, no_path_plugins, monkeypatch):
        monkeypatch.setattr(_plugins, "entry_point_plugins", dict)
        result = runner.invoke(app, ["nonsense"])
        assert result.exit_code != 0
        assert "unitysvc-sellers" not in output_of(result)

    def test_non_typer_non_click_target_is_reported(self, no_path_plugins, monkeypatch):
        _fake_entry_point("seller", object(), monkeypatch)
        result = runner.invoke(app, ["seller"])
        assert result.exit_code != 0
        assert "failed to load" in output_of(result)

    def test_plain_click_command_is_accepted(self, no_path_plugins, monkeypatch):
        @click.command()
        def plain() -> None:
            print("plain click")

        _fake_entry_point("seller", plain, monkeypatch)
        result = runner.invoke(app, ["seller"])
        assert result.exit_code == 0
        assert "plain click" in result.stdout
