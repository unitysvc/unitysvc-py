"""Regression tests for owner-scoped fields on generated customer models.

The backend added a nullable ``owner_id`` to the alias/chain/broadcast
public response models (#1471): ``None`` means a shared team-owned
resource, a UUID means a personal resource owned by that user. Verify the
generated ``from_dict`` / ``to_dict`` round-trip both cases.
"""

from __future__ import annotations

from uuid import UUID

from unitysvc._generated.models.broadcast_public import BroadcastPublic
from unitysvc._generated.models.chain_public import ChainPublic
from unitysvc._generated.models.service_alias_public import ServiceAliasPublic

CUSTOMER_ID = "11111111-1111-1111-1111-111111111111"
RESOURCE_ID = "22222222-2222-2222-2222-222222222222"
OWNER_ID = "33333333-3333-3333-3333-333333333333"


def test_service_alias_public_accepts_shared_null_owner_id() -> None:
    alias = ServiceAliasPublic.from_dict(
        {
            "id": RESOURCE_ID,
            "customer_id": CUSTOMER_ID,
            "name": "my-alias",
            "target_path": "/l/foo",
            "created_at": "2026-07-05T12:00:00Z",
            "owner_id": None,
        }
    )

    assert alias.customer_id == UUID(CUSTOMER_ID)
    assert alias.owner_id is None
    assert alias.to_dict()["owner_id"] is None


def test_service_alias_public_parses_personal_owner_id() -> None:
    alias = ServiceAliasPublic.from_dict(
        {
            "id": RESOURCE_ID,
            "customer_id": CUSTOMER_ID,
            "name": "my-alias",
            "target_path": "/l/foo",
            "created_at": "2026-07-05T12:00:00Z",
            "owner_id": OWNER_ID,
        }
    )

    assert alias.owner_id == UUID(OWNER_ID)
    assert alias.to_dict()["owner_id"] == OWNER_ID


def test_service_alias_public_omits_owner_id_when_absent() -> None:
    alias = ServiceAliasPublic.from_dict(
        {
            "id": RESOURCE_ID,
            "customer_id": CUSTOMER_ID,
            "name": "my-alias",
            "target_path": "/l/foo",
            "created_at": "2026-07-05T12:00:00Z",
        }
    )

    assert "owner_id" not in alias.to_dict()


def test_chain_public_accepts_shared_null_owner_id() -> None:
    chain = ChainPublic.from_dict(
        {
            "id": RESOURCE_ID,
            "customer_id": CUSTOMER_ID,
            "name": "my-chain",
            "default_timeout_ms": 1000,
            "enabled": True,
            "created_at": "2026-07-05T12:00:00Z",
            "owner_id": None,
        }
    )

    assert chain.owner_id is None
    assert chain.to_dict()["owner_id"] is None


def test_chain_public_parses_personal_owner_id() -> None:
    chain = ChainPublic.from_dict(
        {
            "id": RESOURCE_ID,
            "customer_id": CUSTOMER_ID,
            "name": "my-chain",
            "default_timeout_ms": 1000,
            "enabled": True,
            "created_at": "2026-07-05T12:00:00Z",
            "owner_id": OWNER_ID,
        }
    )

    assert chain.owner_id == UUID(OWNER_ID)
    assert chain.to_dict()["owner_id"] == OWNER_ID


def test_broadcast_public_accepts_shared_null_owner_id() -> None:
    broadcast = BroadcastPublic.from_dict(
        {
            "id": RESOURCE_ID,
            "customer_id": CUSTOMER_ID,
            "name": "my-broadcast",
            "mode": "async",
            "target_timeout_ms": 1000,
            "enabled": True,
            "created_at": "2026-07-05T12:00:00Z",
            "owner_id": None,
        }
    )

    assert broadcast.owner_id is None
    assert broadcast.to_dict()["owner_id"] is None


def test_broadcast_public_parses_personal_owner_id() -> None:
    broadcast = BroadcastPublic.from_dict(
        {
            "id": RESOURCE_ID,
            "customer_id": CUSTOMER_ID,
            "name": "my-broadcast",
            "mode": "sync",
            "target_timeout_ms": 1000,
            "enabled": True,
            "created_at": "2026-07-05T12:00:00Z",
            "owner_id": OWNER_ID,
        }
    )

    assert broadcast.owner_id == UUID(OWNER_ID)
    assert broadcast.to_dict()["owner_id"] == OWNER_ID
