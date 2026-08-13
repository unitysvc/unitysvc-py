"""Discovery of sibling UnitySVC CLIs, mounted as ``usvc`` subcommands.

A package that ships its own CLI advertises it::

    # in unitysvc-sellers' pyproject.toml
    [project.entry-points."usvc.commands"]
    seller = "unitysvc_sellers.cli:app"

and ``usvc seller ...`` runs it. The two sides agree on the group name and
nothing else: this package never imports, names, or depends on the packages
providing the subcommands, so installing one more of them adds a verb to ``usvc``
with no release here. Same contract as ``pytest``/``pytest11``.

A ``PATH`` fallback (``usvc-<name>``, then legacy ``usvc_<name>``) covers CLIs
installed into a *different* environment — ``uv tool install`` and ``pipx`` give
each tool its own venv, so entry-point metadata from one is invisible to another.
The hyphenated executable therefore remains the spelling that works everywhere;
``usvc <name>`` is sugar for whoever has both in one place.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from importlib.metadata import EntryPoint, entry_points

import click

# Typer vendors its own copy of click, and its classes are NOT the installed
# click's: `typer._click.exceptions.UsageError is not click.UsageError`. Typer's
# group machinery raises the vendored ones, so an `except click.UsageError` here
# never fires — the symptom was a suggestion that silently never appeared. The
# vendored package exposes submodules only (no top-level `command`/`echo`), so we
# build commands with the installed click and catch both lineages.
try:
    from typer._click import core as _typer_core
    from typer._click import exceptions as _typer_exceptions

    _USAGE_ERRORS: tuple[type[BaseException], ...] = (click.UsageError, _typer_exceptions.UsageError)
    _COMMAND_TYPES: tuple[type, ...] = (click.Command, _typer_core.Command)
except ImportError:  # pragma: no cover - Typer without a vendored click
    _USAGE_ERRORS = (click.UsageError,)
    _COMMAND_TYPES = (click.Command,)

from typer.core import TyperGroup

GROUP = "usvc.commands"
PREFIX = "usvc"
_SEPARATORS = ("-", "_")  # hyphen is canonical; underscore is the legacy spelling

# Names we can suggest a package for when the subcommand is missing. Strings
# only — no import, no dependency, and an unlisted name still works fine.
_SUGGESTIONS = {
    "seller": "unitysvc-sellers",
    "admin": "unitysvc-admin",
    "data": "unitysvc-data",
}


def entry_point_plugins() -> dict[str, EntryPoint]:
    """Advertised subcommands, by name.

    Reads distribution metadata only. The target module is *not* imported, so
    listing plugins in ``--help`` stays cheap no matter what they pull in.
    """
    return {ep.name: ep for ep in entry_points(group=GROUP)}


def path_plugins() -> set[str]:
    """Subcommand names backed by a ``usvc-*`` executable on ``PATH``."""
    names: set[str] = set()
    for directory in os.get_exec_path():
        try:
            entries = list(os.scandir(directory))
        except OSError:
            # An unreadable or missing PATH entry costs a help listing, not a
            # broken command: dispatch re-resolves through shutil.which.
            continue
        for entry in entries:
            stem = os.path.splitext(entry.name)[0] if os.name == "nt" else entry.name
            for separator in _SEPARATORS:
                prefix = f"{PREFIX}{separator}"
                if stem.startswith(prefix) and len(stem) > len(prefix) and os.access(entry.path, os.X_OK):
                    names.add(stem[len(prefix) :])
    return names


def path_executable(name: str) -> str | None:
    """Absolute path to the executable implementing ``name``, if any."""
    for separator in _SEPARATORS:
        found = shutil.which(f"{PREFIX}{separator}{name}")
        if found:
            return found
    return None


def _as_command(loaded: object, name: str) -> click.Command:
    """Adapt a loaded entry-point object to a Click command.

    Accepts a Typer app (the common case) or anything already Click-shaped.
    """
    if isinstance(loaded, _COMMAND_TYPES):
        return loaded
    import typer  # local: only needed once a plugin is actually invoked
    import typer.main

    if isinstance(loaded, typer.Typer):
        return typer.main.get_command(loaded)
    raise TypeError(f"{GROUP} entry point {name!r} is neither a Typer app nor a Click command: {type(loaded)!r}")


class LazyPluginCommand(click.Command):
    """Placeholder that loads its entry point only when actually invoked.

    Help rendering asks every subcommand for its short help, so returning the
    real command from ``get_command`` would import every installed plugin just to
    print ``usvc --help`` — and a plugin can drag in jinja2, mistune, json5. This
    answers the help questions from metadata and defers the import to
    ``make_context``, which Click calls only for the command being run.
    """

    def __init__(self, name: str, entry_point: EntryPoint) -> None:
        super().__init__(name=name)
        self._entry_point = entry_point
        self._target: click.Command | None = None
        origin = getattr(getattr(entry_point, "dist", None), "name", None) or entry_point.value.split(":")[0]
        self.short_help = f"Provided by {origin}."

    def target(self) -> click.Command:
        if self._target is None:
            try:
                self._target = _as_command(self._entry_point.load(), self.name or "")
            except Exception as exc:  # noqa: BLE001 - reported, never fatal to the CLI
                # Reported and exited here rather than raised as a ClickException:
                # this runs inside make_context, and an exception from there does
                # not reliably reach Typer's error formatter — it reached the user
                # as a raw traceback. A message plus SystemExit behaves the same
                # everywhere.
                click.echo(
                    f"Error: the {self.name!r} subcommand is installed but failed to load: {exc}",
                    err=True,
                )
                raise SystemExit(1) from exc
        return self._target

    def get_short_help_str(self, limit: int = 45) -> str:
        return self.short_help or ""

    def make_context(self, info_name, args, parent=None, **extra):  # type: ignore[no-untyped-def]
        # Delegating here hands the resulting context's `.command` to the real
        # plugin, so Click invokes it directly and its own parsing, options and
        # --help all apply unchanged.
        return self.target().make_context(info_name, args, parent=parent, **extra)


def build_path_command(name: str, executable: str) -> click.Command:
    """Pass-through command handing the remaining argv to ``executable``."""

    @click.command(
        name=name,
        # The external CLI owns its parsing: options we do not recognise, and its
        # own --help, must reach it untouched rather than being rejected here.
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
        add_help_option=False,
        help=f"Run {os.path.basename(executable)} (external command).",
    )
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    def run(args: tuple[str, ...]) -> None:
        argv = [executable, *args]
        if os.name == "nt":
            # Windows has no exec that replaces the process; run a child and
            # propagate its status.
            raise SystemExit(subprocess.call(argv))
        sys.stdout.flush()
        sys.stderr.flush()
        # Replace this process, so exit status, signals, TTY detection and
        # streaming output belong to the plugin rather than being relayed.
        os.execv(executable, argv)

    return run


class PluginGroup(TyperGroup):
    """Typer group that mounts discovered subcommands alongside the built-ins."""

    def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
        # Built-ins win: a stray usvc-services binary must never shadow the real
        # subcommand.
        command = super().get_command(ctx, name)
        if command is not None:
            return command

        entry_point = entry_point_plugins().get(name)
        if entry_point is not None:
            return LazyPluginCommand(name, entry_point)

        executable = path_executable(name)
        if executable is not None:
            return build_path_command(name, executable)
        return None

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted(set(super().list_commands(ctx)) | set(entry_point_plugins()) | path_plugins())

    def resolve_command(self, ctx: click.Context, args: list[str]):
        try:
            return super().resolve_command(ctx, args)
        except _USAGE_ERRORS:
            package = _SUGGESTIONS.get(args[0] if args else "")
            if package is None:
                raise
            # One line: Typer's rich error panel renders only the first line of
            # a UsageError message, so a multi-line hint is silently dropped.
            ctx.fail(f"No such command {args[0]!r}. Install {package} in this environment to enable it.")
