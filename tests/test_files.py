"""Unit tests for :class:`unitysvc.files.Files` (unitysvc#1533).

Exercises the account-files surface against mocked ``httpx`` transports.
Two hosts are in play: the UnitySVC API (mint/list/presign — mocked via
the generated client's transport, as in ``test_groups.py``) and the
storage endpoint (upload POST / download GET — mocked by monkeypatching
``httpx.Client``, since the facade deliberately uses a bare client so
the storage host never sees the API key).
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from unitysvc import Client

TICKET = {
    "key": "reports/report.pdf",
    "url": "https://storage.example/account-files",
    "fields": {
        "policy": "signed-policy",
        "key": "home/cust/user/reports/report.pdf",
        "Content-Type": "application/pdf",
    },
    "expires_in": 900,
    "max_bytes": 1073741824,
    "scope": "personal",
}


def _api_transport(payload: dict, captured: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


def _patch_storage(
    monkeypatch: pytest.MonkeyPatch,
    handler,
) -> None:
    """Make bare ``httpx.Client(...)`` calls hit a mock storage transport."""
    real_client = httpx.Client

    def fake_client(**kwargs):
        kwargs.pop("transport", None)
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr("unitysvc.files.httpx.Client", fake_client)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
def test_list_sends_scope_and_path() -> None:
    payload = {
        "scope": "personal",
        "path": "reports/",
        "objects": [{"key": "reports/q2.pdf", "size": 42, "last_modified": "2026-07-14T12:00:00"}],
        "common_prefixes": ["reports/2026/"],
        "is_truncated": False,
        "next_continuation_token": None,
        "shared_enabled": True,
    }
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _api_transport(payload, captured)
        resp = client.files.list("reports", scope="personal")

    assert captured[0].url.path.endswith("/files/list")
    assert captured[0].url.params["scope"] == "personal"
    assert captured[0].url.params["path"] == "reports"
    assert resp.shared_enabled is True
    assert [o.key for o in resp.objects] == ["reports/q2.pdf"]
    assert resp.common_prefixes == ["reports/2026/"]


# ---------------------------------------------------------------------------
# upload — mint via API, then multipart POST to storage
# ---------------------------------------------------------------------------
def test_upload_mints_then_posts_fields_before_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "report.pdf"
    src.write_bytes(b"hello")

    api_captured: list[httpx.Request] = []
    storage_captured: list[httpx.Request] = []

    def storage_handler(request: httpx.Request) -> httpx.Response:
        storage_captured.append(request)
        return httpx.Response(204)

    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _api_transport(TICKET, api_captured)
        _patch_storage(monkeypatch, storage_handler)
        key = client.files.upload(src, "reports", scope="personal")

    assert key == "reports/report.pdf"

    # Mint request: key parts only — never a full key or bucket.
    mint = json.loads(api_captured[0].content)
    assert mint["filename"] == "report.pdf"
    assert mint["size"] == 5
    assert mint["path"] == "reports"
    assert mint["scope"] == "personal"

    # Storage POST: multipart with every policy field, and the file LAST.
    body = storage_captured[0].content
    assert storage_captured[0].url == TICKET["url"]
    for field in TICKET["fields"]:
        assert f'name="{field}"'.encode() in body
    assert body.index(b'name="policy"') < body.index(b'name="file"')
    assert b"hello" in body
    # The API key must never reach the storage host.
    assert "authorization" not in {k.lower() for k in storage_captured[0].headers}
    assert "svcpass_test" not in str(storage_captured[0].headers)


def test_upload_storage_rejection_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from unitysvc.exceptions import APIError

    src = tmp_path / "big.bin"
    src.write_bytes(b"x" * 10)

    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _api_transport(TICKET, [])
        _patch_storage(
            monkeypatch,
            lambda request: httpx.Response(400, text="EntityTooLarge"),
        )
        with pytest.raises(APIError, match="EntityTooLarge"):
            client.files.upload(src)


# ---------------------------------------------------------------------------
# download — presign via API, then GET from storage
# ---------------------------------------------------------------------------
def test_download_streams_to_dest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    presign = {
        "scope": "personal",
        "key": "reports/q2.pdf",
        "url": "https://storage.example/presigned?sig=abc",
        "expires_in": 900,
    }
    api_captured: list[httpx.Request] = []
    storage_captured: list[httpx.Request] = []

    def storage_handler(request: httpx.Request) -> httpx.Response:
        storage_captured.append(request)
        return httpx.Response(200, content=b"pdf-bytes")

    dest = tmp_path / "local.pdf"
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _api_transport(presign, api_captured)
        _patch_storage(monkeypatch, storage_handler)
        written = client.files.download("reports/q2.pdf", dest)

    assert written == dest
    assert dest.read_bytes() == b"pdf-bytes"
    assert api_captured[0].url.path.endswith("/files/download")
    assert api_captured[0].url.params["key"] == "reports/q2.pdf"
    assert str(storage_captured[0].url) == presign["url"]
    assert "authorization" not in {k.lower() for k in storage_captured[0].headers}


# ---------------------------------------------------------------------------
# CLI virtual-path grammar
# ---------------------------------------------------------------------------
def test_split_vpath() -> None:
    import typer

    from unitysvc.commands.files import _split_vpath

    assert _split_vpath("personal/reports/q2.pdf") == ("personal", "reports/q2.pdf")
    assert _split_vpath("shared") == ("shared", "")
    assert _split_vpath("/personal/") == ("personal", "")
    with pytest.raises(typer.BadParameter):
        _split_vpath("reports/q2.pdf")
    with pytest.raises(typer.BadParameter):
        _split_vpath("")
