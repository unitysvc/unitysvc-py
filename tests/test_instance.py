"""``client.instance(id)`` (``Instance``: start / stop / get / wait / credentials) and
``usvc instances`` (unitysvc#3016): a container service's instance is run through the
customer API, since it has no gateway route."""

from __future__ import annotations

import json

import httpx
import pytest
from typer.testing import CliRunner

from unitysvc import AsyncClient, Client
from unitysvc.commands.instances import app

ENROLLMENT = "22222222-2222-4222-8222-222222222222"
BASE = "https://test.example/v1/customer"
runner = CliRunner()


def _state(status: str = "succeeded", *, fault: str | None = None, action: str = "start", reason: str | None = None):
    return {
        "enrollment_id": ENROLLMENT,
        "requested_action": action,
        "generation": 3,
        "status": status,
        "reason": reason,
        "fault": fault,
        "components": [{"service": "web", "pod": "web-0", "phase": "Running", "ready": status == "succeeded"}],
        "entries": [{"name": "web", "hostname": "abcd.x", "url": "https://abcd.x", "auth": "none"}],
    }


class _Server:
    """Answers the instance routes; ``states`` is what successive reads return."""

    def __init__(self, states: list[dict]) -> None:
        self.states = list(states)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path
        if path.endswith("/credentials"):
            return httpx.Response(200, json={"key": "k-123"})
        if request.method == "POST":
            action = "stop" if path.endswith("/stop") else "start"
            return httpx.Response(202, json=_state("pending", action=action))
        state = self.states.pop(0) if len(self.states) > 1 else self.states[0]
        return httpx.Response(200, json=state)


def _client(server: _Server, *, asynchronous: bool = False):
    cls = AsyncClient if asynchronous else Client
    client = cls(api_key="svcpass_test", base_url=BASE)
    wire = httpx.MockTransport(server)
    if asynchronous:
        client._client.get_async_httpx_client()._transport = wire
    else:
        client._client.get_httpx_client()._transport = wire
    return client


def test_start_posts_and_returns_the_pending_request() -> None:
    server = _Server([_state()])
    state = _client(server).instance(ENROLLMENT).start()
    assert (server.requests[0].method, server.requests[0].url.path) == (
        "POST",
        f"/v1/customer/enrollments/{ENROLLMENT}/instance/start",
    )
    assert state.status == "pending"


def test_stop_posts() -> None:
    server = _Server([_state()])
    _client(server).instance(ENROLLMENT).stop()
    assert server.requests[0].url.path.endswith("/instance/stop")


def test_get_sends_wait_and_parses_fault_and_entries() -> None:
    server = _Server([_state("failed", fault="platform", reason="apply_error")])
    state = _client(server).instance(ENROLLMENT).get(wait=30)
    assert server.requests[0].url.params["wait"] == "30"
    assert state.status == "failed" and state.fault == "platform" and state.reason == "apply_error"
    assert state.entries[0].url == "https://abcd.x"


def test_credentials_returns_the_key() -> None:
    assert _client(_Server([_state()])).instance(ENROLLMENT).credentials().key == "k-123"


def test_wait_polls_until_finished() -> None:
    server = _Server([_state("pending"), _state("in_progress"), _state("succeeded")])
    state = _client(server).instance(ENROLLMENT).wait(timeout=30)
    assert state.status == "succeeded"
    assert len(server.requests) == 3


def test_wait_times_out() -> None:
    with pytest.raises(TimeoutError):
        _client(_Server([_state("pending")])).instance(ENROLLMENT).wait(timeout=0.01)


def test_enrollment_exposes_its_instance() -> None:
    server = _Server([_state()])
    client = _client(server)
    enrollment = client.enrollments.get  # noqa: F841 — the wrapper is built from a record
    from unitysvc.enrollments import Enrollment

    class _Raw:
        id = ENROLLMENT

    Enrollment(_Raw(), parent=client).instance.start()  # type: ignore[arg-type]
    assert server.requests[0].url.path.endswith("/instance/start")


@pytest.mark.asyncio
async def test_async_facade() -> None:
    server = _Server([_state("pending"), _state("succeeded")])
    client = _client(server, asynchronous=True)
    started = await client.instance(ENROLLMENT).start()
    assert started.status == "pending"
    state = await client.instance(ENROLLMENT).wait(timeout=30)
    assert state.status == "succeeded"
    assert (await client.instance(ENROLLMENT).credentials()).key == "k-123"


# --- CLI -----------------------------------------------------------------


@pytest.fixture
def cli(monkeypatch: pytest.MonkeyPatch):
    from contextlib import asynccontextmanager

    holder: dict[str, _Server] = {}

    def use(server: _Server) -> _Server:
        holder["server"] = server
        return server

    @asynccontextmanager
    async def fake(api_key=None, base_url=None):
        yield _client(holder["server"], asynchronous=True)

    monkeypatch.setattr("unitysvc.commands.instances.async_client", fake)
    return use


def _run(*args: str):
    return runner.invoke(app, list(args))


@pytest.mark.parametrize(
    ("final", "code"),
    [
        (_state("succeeded"), 0),
        (_state("failed", fault="seller", reason="never_ready"), 1),
        (_state("failed", fault="platform", reason="hostname_conflict"), 75),
    ],
)
def test_check_exit_codes_and_stops_afterwards(cli, final: dict, code: int) -> None:
    server = cli(_Server([final]))
    result = _run("check", ENROLLMENT, "--timeout", "30")
    assert result.exit_code == code, result.output
    posts = [r.url.path.rsplit("/", 1)[-1] for r in server.requests if r.method == "POST"]
    assert posts == ["start", "stop"]


def test_check_keep_does_not_stop(cli) -> None:
    server = cli(_Server([_state("succeeded")]))
    assert _run("check", ENROLLMENT, "--keep").exit_code == 0
    assert [r.url.path.rsplit("/", 1)[-1] for r in server.requests if r.method == "POST"] == ["start"]


def test_status_json_and_exit_code(cli) -> None:
    cli(_Server([_state("failed", fault="platform")]))
    result = _run("status", ENROLLMENT, "--format", "json")
    assert result.exit_code == 75
    assert json.loads(result.output)["fault"] == "platform"


def test_key_prints_only_the_key(cli) -> None:
    cli(_Server([_state()]))
    result = _run("key", ENROLLMENT)
    assert result.exit_code == 0 and result.output.strip() == "k-123"


def test_start_wait_exits_like_check(cli) -> None:
    cli(_Server([_state("succeeded")]))
    assert _run("start", ENROLLMENT, "--wait").exit_code == 0
