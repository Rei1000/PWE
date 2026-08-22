"""Alembic als führender Schema-Pfad (Gate 7.5b)."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text

from api.app import create_app
from api.persistence import (
    PersistenceConfigurationError,
    assert_postgresql_schema_ready,
    initialize_postgresql_engine,
)
from tests.support.alembic_migrate import alembic_downgrade_base, alembic_upgrade_head

pytestmark = pytest.mark.postgresql

EXPECTED_TABLES = {
    "produktdefinition_entwurf",
    "produktdefinitions_version",
    "aktive_version",
    "prueflauf",
    "externes_kommando",
    "routine",
    "pruefschritt_vorlage",
    "protokoll_snapshot",
}


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL nicht gesetzt — PostgreSQL-Tests übersprungen")
    return url


def _engine_with_schema(base_url: str, schema: str):
    raw = create_engine(base_url, future=True)
    with raw.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
        conn.commit()
    raw.dispose()
    return create_engine(
        base_url,
        future=True,
        connect_args={"options": f"-csearch_path={schema}"},
    )


def _drop_schema(base_url: str, schema: str) -> None:
    engine = create_engine(base_url, future=True)
    with engine.connect() as conn:
        conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        conn.commit()
    engine.dispose()


def test_alembic_upgrade_downgrade_reupgrade_on_empty_schema():
    base_url = _database_url()
    schema = f"pwe_alembic_ud_{uuid.uuid4().hex[:10]}"
    engine = None
    try:
        engine = _engine_with_schema(base_url, schema)
        alembic_upgrade_head(database_url=base_url, schema=schema)
        tables = set(inspect(engine).get_table_names())
        assert EXPECTED_TABLES <= tables
        assert "alembic_version" in tables

        alembic_downgrade_base(database_url=base_url, schema=schema)
        remaining = set(inspect(engine).get_table_names()) - {"alembic_version"}
        assert EXPECTED_TABLES.isdisjoint(remaining)

        alembic_upgrade_head(database_url=base_url, schema=schema)
        assert EXPECTED_TABLES <= set(inspect(engine).get_table_names())
    finally:
        if engine is not None:
            engine.dispose()
        _drop_schema(base_url, schema)


def test_alembic_creates_full_current_schema():
    base_url = _database_url()
    schema = f"pwe_alembic_full_{uuid.uuid4().hex[:10]}"
    engine = None
    try:
        engine = _engine_with_schema(base_url, schema)
        alembic_upgrade_head(database_url=base_url, schema=schema)
        insp = inspect(engine)
        assert EXPECTED_TABLES <= set(insp.get_table_names())
        fks = insp.get_foreign_keys("aktive_version")
        assert any(
            fk["referred_table"] == "produktdefinitions_version"
            and "version_id" in fk["constrained_columns"]
            for fk in fks
        )
    finally:
        if engine is not None:
            engine.dispose()
        _drop_schema(base_url, schema)


def test_runtime_fails_clearly_without_migration():
    base_url = _database_url()
    schema = f"pwe_alembic_empty_{uuid.uuid4().hex[:10]}"
    engine = None
    try:
        engine = _engine_with_schema(base_url, schema)
        before = set(inspect(engine).get_table_names())
        with pytest.raises(PersistenceConfigurationError, match="Schema fehlt"):
            assert_postgresql_schema_ready(engine)
        after = set(inspect(engine).get_table_names())
        assert after == before
        assert "produktdefinitions_version" not in after
    finally:
        if engine is not None:
            engine.dispose()
        _drop_schema(base_url, schema)


def test_runtime_does_not_create_schema():
    base_url = _database_url()
    schema = f"pwe_alembic_nogen_{uuid.uuid4().hex[:10]}"
    engine = None
    try:
        engine = _engine_with_schema(base_url, schema)
        before = set(inspect(engine).get_table_names())
        with pytest.raises(PersistenceConfigurationError):
            assert_postgresql_schema_ready(engine)
        assert set(inspect(engine).get_table_names()) == before
    finally:
        if engine is not None:
            engine.dispose()
        _drop_schema(base_url, schema)


def test_runtime_works_after_public_alembic_upgrade(monkeypatch: pytest.MonkeyPatch):
    """Nach Migration auf dem DATABASE_URL-Schema startet die API (wie Docker/CI)."""
    base_url = _database_url()
    alembic_upgrade_head(database_url=base_url)
    monkeypatch.setenv("DATABASE_URL", base_url)
    engine = initialize_postgresql_engine(base_url)
    try:
        with TestClient(create_app()) as client:
            assert client.get("/health").status_code == 200
    finally:
        engine.dispose()
