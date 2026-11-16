"""Tests for ``usvc rooms`` (unitysvc#2846 C8).

``async_client`` is monkeypatched with a recording sink, so no backend is
needed: each command must call the right ``client.rooms`` method with the
right arguments and print its result.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any

import pytest
from typer.testing import CliRunner

from unitysvc.commands.rooms import app

runner = CliRunner()

ROOM = {
    "id": "11111111-1111-4111-8111-111111111111",
    "kind": "chat",
    "name": "Book club",
    "handle": "book-club",
    "role": "owner",
    "status": "active",
}


class _Rooms:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []

    async def list(self, **filters: Any) -> Any:
        self.calls.append(("list", filters))
        return SimpleNamespace(data=[ROOM])

    async def get(self, target: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get", target, kwargs))
        message = {"offset": 3, "sent_at": "2026-10-31T10:00:00Z", "sender_name": "Ann", "body": "hello"}
        return {"description": "Read together", **ROOM, "messages": {"data": [message], "next": 3}}

    async def post(self, target: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("post", target, kwargs))
        return {"room_id": ROOM["id"], "offset": 4}

    async def members(self, target: str) -> Any:
        self.calls.append(("members", target))
        return SimpleNamespace(data=[{"name": "Ann", "account_type": "customer", "role": "owner", "joined_at": "x"}])

    async def update(self, target: str, **settings: Any) -> dict[str, Any]:
        self.calls.append(("update", target, settings))
        return {**ROOM, **settings}

    async def delivery(self, target: str) -> dict[str, Any]:
        self.calls.append(("delivery", target))
        return {"connectors": [{"name": "main", "notify": "notify", "email": None, "post": None}], "can_edit": True}

    async def add_connector(self, target: str, name: str, **channels: Any) -> dict[str, Any]:
        self.calls.append(("add_connector", target, name, channels))
        return {"connectors": [{"name": name, **channels}], "can_edit": True}

    async def update_connector(self, target: str, name: str, **channels: Any) -> dict[str, Any]:
        self.calls.append(("update_connector", target, name, channels))
        return {"connectors": [{"name": name, **channels}], "can_edit": True}

    async def remove_connector(self, target: str, name: str) -> dict[str, Any]:
        self.calls.append(("remove_connector", target, name))
        return {"connectors": [], "can_edit": True}

    async def commands(self) -> Any:
        self.calls.append(("commands",))
        return SimpleNamespace(data=[{"syntax": "!allow $<amount>", "summary": "Allow", "sender": "customer"}])

    async def available_commands(self, target: str) -> Any:
        self.calls.append(("available_commands", target))
        return SimpleNamespace(
            data=[{"syntax": "!allow $<amount>", "summary": "Allow", "available": False, "reason": "Sellers only"}]
        )

    async def accept_live_requests(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("accept_live_requests", kwargs))
        return {"client_id": kwargs["client_id"] or "c-new", "expires_in": 60}

    async def stop_accepting_live_requests(self, **kwargs: Any) -> None:
        self.calls.append(("stop_accepting_live_requests", kwargs))

    async def live_waiting(self) -> Any:
        self.calls.append(("live_waiting",))
        return SimpleNamespace(data=[{"room_id": ROOM["id"], "handle": "book-club", "requesters": 1}])

    async def live_status(self, target: str) -> Any:
        self.calls.append(("live_status", target))
        return SimpleNamespace(data=[{"member_id": "m1", "name": "Ann", "state": "accepting", "available": True}])

    async def request_live_help(self, target: str, member: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("request_live_help", target, member, kwargs))
        return {"target_member_id": member, "generation": "g1", "client_id": "c-new", "state": "accepting"}

    async def cancel_live_help(self, target: str, member: str, **kwargs: Any) -> None:
        self.calls.append(("cancel_live_help", target, member, kwargs))

    async def resolve_live_help(self, target: str, **kwargs: Any) -> None:
        self.calls.append(("resolve_live_help", target, kwargs))

    async def next_room(self, current: Any = None, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("next_room", current, kwargs))
        return {"room_id": ROOM["id"], "handle": "book-club", "claim_token": "t1", "expires_in": 60}

    async def renew_claim(self, target: str, claim_token: str) -> dict[str, Any]:
        self.calls.append(("renew_claim", target, claim_token))
        return {"room_id": ROOM["id"], "handle": "book-club", "claim_token": claim_token, "expires_in": 60}

    async def return_later(self, target: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("return_later", target, kwargs))
        return {"attention_pending": True, "attention_since": "2026-11-16T00:00:00Z"}

    async def mark_done(self, target: str, offset: int) -> dict[str, Any]:
        self.calls.append(("mark_done", target, offset))
        return {"attention_pending": False, "attention_since": None}

    async def create_invitation(self, target: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("create_invitation", target, kwargs))
        return {"token": "ABCD1234", "role": kwargs["role"]}

    async def invitations(self, target: str, **kwargs: Any) -> Any:
        self.calls.append(("invitations", target, kwargs))
        return SimpleNamespace(data=[{"id": "c1", "token": "ABCD1234"}])

    async def revoke_invitation(self, target: str, code_id: str) -> dict[str, Any]:
        self.calls.append(("revoke_invitation", target, code_id))
        return {"id": code_id, "status": "revoked"}

    async def join(self, token: str) -> dict[str, Any]:
        self.calls.append(("join", token))
        return ROOM

    async def leave(self, target: str) -> None:
        self.calls.append(("leave", target))


@pytest.fixture
def rooms(monkeypatch: pytest.MonkeyPatch) -> _Rooms:
    sink = _Rooms()

    @asynccontextmanager
    async def fake_async_client(api_key=None, base_url=None):  # type: ignore[no-untyped-def]
        yield SimpleNamespace(rooms=sink)

    monkeypatch.setattr("unitysvc.commands.rooms.async_client", fake_async_client)
    return sink


def test_list_passes_the_filters(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["list", "--kind", "chat", "--enrollment", "e1", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert rooms.calls == [("list", {"kind": "chat", "enrollment": "e1", "service": None})]
    assert json.loads(result.output)[0]["handle"] == "book-club"
    table = runner.invoke(app, ["list", "--service", "s1"])
    assert table.exit_code == 0 and "Book club" in table.output
    assert rooms.calls[-1] == ("list", {"kind": None, "enrollment": None, "service": "s1"})


def test_show_prints_messages_and_the_next_cursor(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["show", "me", "--after", "2", "--limit", "10"])
    assert result.exit_code == 0, result.output
    assert rooms.calls == [("get", "me", {"after": 2, "limit": 10})]
    assert "Ann" in result.output and "hello" in result.output and "--after 3" in result.output


def test_post_members_and_settings(rooms: _Rooms) -> None:
    assert runner.invoke(app, ["post", "book-club", "hi all", "--id", "k1"]).exit_code == 0
    assert rooms.calls[-1] == ("post", "book-club", {"body": "hi all", "client_message_id": "k1"})
    assert "Ann" in runner.invoke(app, ["members", "book-club"]).output
    result = runner.invoke(app, ["set", "book-club", "--status", "readonly", "--retention", "3600"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("update", "book-club", {"retention_seconds": 3600, "status": "readonly"})
    assert runner.invoke(app, ["set", "book-club"]).exit_code == 1


def test_delivery_and_connectors(rooms: _Rooms) -> None:
    shown = json.loads(runner.invoke(app, ["delivery", "me"]).output)
    assert shown["connectors"][0]["name"] == "main" and shown["can_edit"] is True
    result = runner.invoke(app, ["connector", "add", "me", "discord", "--notify", "labs/msg-to-discord"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("add_connector", "me", "discord", {"notify": "labs/msg-to-discord"})
    assert json.loads(result.output)["connectors"][0]["name"] == "discord"
    # ``off`` turns a channel off (null); channels left out are not sent.
    result = runner.invoke(
        app, ["connector", "set", "me", "discord", "--email", "off", "--post", "labs/discord-to-msg"]
    )
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("update_connector", "me", "discord", {"email": None, "post": "labs/discord-to-msg"})
    assert runner.invoke(app, ["connector", "set", "me", "discord"]).exit_code == 1
    assert runner.invoke(app, ["connector", "remove", "me", "discord"]).exit_code == 0
    assert rooms.calls[-1] == ("remove_connector", "me", "discord")


def test_commands_everywhere_and_in_a_room(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["commands"])
    assert result.exit_code == 0 and "!allow" in result.output
    assert rooms.calls[-1] == ("commands",)
    result = runner.invoke(app, ["commands", "book-club", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("available_commands", "book-club")
    assert json.loads(result.output)[0]["reason"] == "Sellers only"
    assert "Sellers only" in runner.invoke(app, ["commands", "book-club"]).output


def test_post_mentions_and_reports_a_command_outcome(rooms: _Rooms, monkeypatch: pytest.MonkeyPatch) -> None:
    result = runner.invoke(app, ["post", "book-club", "@staff look", "--mention", "m1", "-m", "m2"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("post", "book-club", {"body": "@staff look", "mentions": ["m1", "m2"]})

    async def post(target: str, **kwargs: Any) -> dict[str, Any]:
        return {"room_id": ROOM["id"], "offset": 5, "command": {"status": "refused", "message": "Not [now]"}}

    monkeypatch.setattr(rooms, "post", post)
    result = runner.invoke(app, ["post", "book-club", "!allow $6"])
    assert result.exit_code == 0, result.output
    assert "Not [now]" in result.output


def test_live_help_commands(rooms: _Rooms) -> None:
    assert json.loads(runner.invoke(app, ["live", "status", "book-club"]).output)[0]["state"] == "accepting"
    assert rooms.calls[-1] == ("live_status", "book-club")
    assert json.loads(runner.invoke(app, ["live", "waiting"]).output)[0]["handle"] == "book-club"
    result = runner.invoke(app, ["live", "accept"])
    assert result.exit_code == 0 and json.loads(result.output)["client_id"] == "c-new"
    assert rooms.calls[-1] == ("accept_live_requests", {"client_id": None, "mode": "accepting"})
    assert runner.invoke(app, ["live", "accept", "--client-id", "c-new", "--draining"]).exit_code == 0
    assert rooms.calls[-1] == ("accept_live_requests", {"client_id": "c-new", "mode": "draining"})
    assert runner.invoke(app, ["live", "stop", "--client-id", "c-new"]).exit_code == 0
    assert rooms.calls[-1] == ("stop_accepting_live_requests", {"client_id": "c-new"})
    result = runner.invoke(app, ["live", "request", "book-club", "m1", "--client-id", "c1", "--generation", "g1"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("request_live_help", "book-club", "m1", {"client_id": "c1", "generation": "g1"})
    assert runner.invoke(app, ["live", "cancel", "book-club", "m1", "--client-id", "c1"]).exit_code == 0
    assert rooms.calls[-1] == ("cancel_live_help", "book-club", "m1", {"client_id": "c1"})
    assert runner.invoke(app, ["live", "resolve", "book-club"]).exit_code == 0
    assert rooms.calls[-1] == ("resolve_live_help", "book-club", {"generation": None})


def test_work_queue_commands(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["work", "next"])
    assert result.exit_code == 0 and json.loads(result.output)["claim_token"] == "t1"
    assert rooms.calls[-1] == ("next_room", None, {"claim_token": None, "offset": None})
    result = runner.invoke(app, ["work", "next", "--current", ROOM["id"], "--claim", "t1", "--offset", "7"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("next_room", ROOM["id"], {"claim_token": "t1", "offset": 7})
    assert runner.invoke(app, ["work", "claim", "book-club", "t1"]).exit_code == 0
    assert rooms.calls[-1] == ("renew_claim", "book-club", "t1")
    assert runner.invoke(app, ["work", "return-later", "book-club", "--claim", "t1"]).exit_code == 0
    assert rooms.calls[-1] == ("return_later", "book-club", {"claim_token": "t1"})
    result = runner.invoke(app, ["work", "done", "book-club", "7"])
    assert result.exit_code == 0 and json.loads(result.output)["attention_pending"] is False
    assert rooms.calls[-1] == ("mark_done", "book-club", 7)


def test_invitations_join_and_leave(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["invite", "book-club", "--role", "moderator", "--max-uses", "5"])
    assert result.exit_code == 0 and "ABCD1234" in result.output
    assert rooms.calls[-1] == ("create_invitation", "book-club", {"role": "moderator", "max_uses": 5})
    assert runner.invoke(app, ["invitations", "book-club", "--all"]).exit_code == 0
    assert rooms.calls[-1] == ("invitations", "book-club", {"include_inactive": True})
    assert runner.invoke(app, ["revoke", "book-club", "c1"]).exit_code == 0
    assert "@book-club" in runner.invoke(app, ["join", "ABCD1234"]).output
    assert runner.invoke(app, ["leave", "book-club", "--yes"]).exit_code == 0
    assert rooms.calls[-1] == ("leave", "book-club")


TRICKY = "a long room description with [bold]tags[/bold] and [/INST] " * 6


def test_json_output_is_plain_and_exact(rooms: _Rooms, monkeypatch: pytest.MonkeyPatch) -> None:
    """--format json writes the JSON as is: no wrapping inside long strings,
    no markup interpretation of brackets."""
    monkeypatch.setitem(ROOM, "description", TRICKY)
    result = runner.invoke(app, ["list", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)[0]["description"] == TRICKY
    shown = runner.invoke(app, ["show", "book-club", "--format", "json"])
    assert shown.exit_code == 0, shown.output
    assert json.loads(shown.output)["description"] == TRICKY


def test_user_content_is_printed_literally(rooms: _Rooms, monkeypatch: pytest.MonkeyPatch) -> None:
    """Room names, descriptions, senders and bodies are user content: Rich
    tags in them neither crash the CLI nor change what is shown."""
    literal = "Literal [/INST] text"

    async def get(target: str, **kwargs: Any) -> dict[str, Any]:
        message = {"offset": 3, "sent_at": "t", "sender_name": "[red]Eve[/red]", "body": literal}
        return {**ROOM, "name": "[bold]Club[/bold]", "description": literal, "messages": {"data": [message], "next": 3}}

    monkeypatch.setattr(rooms, "get", get)
    result = runner.invoke(app, ["show", "book-club"])
    assert result.exit_code == 0, result.output
    assert result.output.count(literal) == 2
    assert "[bold]Club[/bold]" in result.output and "[red]Eve[/red]" in result.output

    monkeypatch.setitem(ROOM, "name", "[bold]Club[/bold]")
    table = runner.invoke(app, ["list"])
    assert table.exit_code == 0, table.output
    assert "[bold]Club[/bold]" in table.output


def test_chat_opens_the_room_with_the_accounts_rooms_client(rooms: _Rooms, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[Any] = []

    async def fake_run_chat(client_rooms: Any, room: Any, **options: Any) -> None:
        seen.append((client_rooms, room, options["filters"], options["join_code"]))

    monkeypatch.setattr("unitysvc.chat.run_chat", fake_run_chat)
    result = runner.invoke(app, ["chat", "@helpdesk", "--enrollment", "e1"])
    assert result.exit_code == 0, result.output
    assert seen == [(rooms, "@helpdesk", {"enrollment": "e1"}, None)]


def test_list_narrows_by_name_and_new_activity(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["list", "--name", "Book", "--new", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == (
        "list",
        {"kind": None, "enrollment": None, "service": None, "q": "Book", "new_activity": True},
    )
    assert runner.invoke(app, ["list", "--closed"]).exit_code == 0
    assert rooms.calls[-1] == ("list", {"kind": None, "enrollment": None, "service": None, "include_closed": True})


def test_post_attaches_files_and_needs_text_or_a_file(rooms: _Rooms, tmp_path: Any) -> None:
    (tmp_path / "log.txt").write_text("boom")
    result = runner.invoke(app, ["post", "helpdesk", "--attach", str(tmp_path / "log.txt")])
    assert result.exit_code == 0, result.output
    _, target, sent = rooms.calls[-1]
    assert target == "helpdesk" and sent["body"] == ""
    assert sent["attachments"] == [{"base64": "Ym9vbQ==", "filename": "log.txt"}]

    assert runner.invoke(app, ["post", "helpdesk"]).exit_code == 1
    url_only = runner.invoke(app, ["post", "helpdesk", "--attach", "https://example.com/a.pdf"])
    assert url_only.exit_code == 1 and "URL alone needs text" in " ".join(url_only.output.split())
    missing = runner.invoke(app, ["post", "helpdesk", "--attach", str(tmp_path / "nope.png")])
    # Rich wraps at the terminal width, so compare without line breaks.
    assert missing.exit_code == 1 and "not a file" in " ".join(missing.output.split())
