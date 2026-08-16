"""Alembic Bootstrap — Upgrade/Downgrade und Schema-Parität zu create_all (Gate 7.5a)."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from adapters.persistence.postgresql.schema import init_schema

pytestmark = pytest.mark.postgresql

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL nicht gesetzt — PostgreSQL-Tests übersprungen")
    return url


def _alembic_config() -> Config:
    return Config(str(BACKEND_ROOT / "alembic.ini"))


def _schema_signature(engine) -> dict:
    insp = inspect(engine)
    tables: dict = {}
    for name in sorted(insp.get_table_names()):
        columns = tuple(
            (c["name"], str(c["type"]), bool(c["nullable"]))
            for c in insp.get_columns(name)
        )
        indexes = tuple(
            (
                ix["name"],
                tuple(ix["column_names"]),
                bool(ix.get("unique")),
            )
            for ix in sorted(insp.get_indexes(name), key=lambda i: i["name"] or "")
        )
        fks = tuple(
            (
                tuple(fk["constrained_columns"]),
                fk["referred_table"],
                tuple(fk["referred_columns"]),
            )
            for fk in sorted(
                insp.get_foreign_keys(name),
                key=lambda f: (f["referred_table"], tuple(f["constrained_columns"])),
            )
        )
        tables[name] = {"columns": columns, "indexes": indexes, "foreign_keys": fks}
    return tables


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


def test_alembic_upgrade_and_downgrade_on_empty_database(monkeypatch: pytest.MonkeyPatch):
    base_url = _database_url()
    schema = f"pwe_alembic_ud_{uuid.uuid4().hex[:10]}"
    engine = None
    try:
        engine = _engine_with_schema(base_url, schema)
        monkeypatch.setenv("DATABASE_URL", base_url)
        monkeypatch.setenv("ALEMBIC_SCHEMA", schema)
        cfg = _alembic_config()

        command.upgrade(cfg, "head")
        insp = inspect(engine)
        assert "produktdefinitions_version" in insp.get_table_names()
        assert "aktive_version" in insp.get_table_names()
        assert "alembic_version" in insp.get_table_names()

        command.downgrade(cfg, "base")
        remaining = set(inspect(engine).get_table_names()) - {"alembic_version"}
        assert "produktdefinitions_version" not in remaining
        assert "externes_kommando" not in remaining
        assert "prueflauf" not in remaining
    finally:
        monkeypatch.delenv("ALEMBIC_SCHEMA", raising=False)
        if engine is not None:
            engine.dispose()
        _drop_schema(base_url, schema)


def test_alembic_upgrade_schema_matches_create_all(monkeypatch: pytest.MonkeyPatch):
    base_url = _database_url()
    schema_create = f"pwe_alembic_ca_{uuid.uuid4().hex[:10]}"
    schema_mig = f"pwe_alembic_mg_{uuid.uuid4().hex[:10]}"
    engine_create = None
    engine_mig = None
    try:
        engine_create = _engine_with_schema(base_url, schema_create)
        init_schema(engine_create)
        sig_create = _schema_signature(engine_create)

        engine_mig = _engine_with_schema(base_url, schema_mig)
        monkeypatch.setenv("DATABASE_URL", base_url)
        monkeypatch.setenv("ALEMBIC_SCHEMA", schema_mig)
        cfg = _alembic_config()
        command.upgrade(cfg, "head")
        with engine_mig.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()
        sig_mig = _schema_signature(engine_mig)

        assert sig_mig == sig_create
    finally:
        monkeypatch.delenv("ALEMBIC_SCHEMA", raising=False)
        if engine_create is not None:
            engine_create.dispose()
        if engine_mig is not None:
            engine_mig.dispose()
        _drop_schema(base_url, schema_create)
        _drop_schema(base_url, schema_mig)


def test_init_schema_create_all_bleibt_funktionsfaehig():
    """Gate 7.5a: create_all bleibt bis 7.5b der Runtime-Pfad."""
    base_url = _database_url()
    schema = f"pwe_alembic_init_{uuid.uuid4().hex[:10]}"
    engine = None
    try:
        engine = _engine_with_schema(base_url, schema)
        init_schema(engine)
        tables = set(inspect(engine).get_table_names())
        assert {
            "produktdefinition_entwurf",
            "produktdefinitions_version",
            "aktive_version",
            "prueflauf",
            "externes_kommando",
            "routine",
            "protokoll_snapshot",
        } <= tables
    finally:
        if engine is not None:
            engine.dispose()
        _drop_schema(base_url, schema)
