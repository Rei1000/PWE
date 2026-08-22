"""Zentrale Test-Hilfe: Alembic-Upgrade (Gate 7.5b) — kein create_all."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def alembic_config() -> Config:
    return Config(str(BACKEND_ROOT / "alembic.ini"))


@contextmanager
def _alembic_env(*, database_url: str, schema: str | None = None):
    previous_url = os.environ.get("DATABASE_URL")
    previous_schema = os.environ.get("ALEMBIC_SCHEMA")
    os.environ["DATABASE_URL"] = database_url
    if schema:
        os.environ["ALEMBIC_SCHEMA"] = schema
    elif "ALEMBIC_SCHEMA" in os.environ:
        del os.environ["ALEMBIC_SCHEMA"]
    try:
        yield alembic_config()
    finally:
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url
        if previous_schema is None:
            os.environ.pop("ALEMBIC_SCHEMA", None)
        else:
            os.environ["ALEMBIC_SCHEMA"] = previous_schema


def alembic_upgrade_head(*, database_url: str, schema: str | None = None) -> None:
    """Führt `alembic upgrade head` aus. Optional isoliertes Schema via ALEMBIC_SCHEMA."""
    with _alembic_env(database_url=database_url, schema=schema) as cfg:
        command.upgrade(cfg, "head")


def alembic_downgrade_base(*, database_url: str, schema: str | None = None) -> None:
    with _alembic_env(database_url=database_url, schema=schema) as cfg:
        command.downgrade(cfg, "base")


def alembic_ensure_head(*, database_url: str, schema: str | None = None) -> None:
    """Idempotent: upgrade, oder stamp bei Legacy-create_all ohne alembic_version."""
    connect_args = {"options": f"-csearch_path={schema}"} if schema else {}
    engine = create_engine(database_url, future=True, connect_args=connect_args)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    has_app_schema = "produktdefinitions_version" in tables
    has_alembic = "alembic_version" in tables

    with _alembic_env(database_url=database_url, schema=schema) as cfg:
        if has_app_schema and not has_alembic:
            # Vor Gate 7.5b per create_all angelegt — Version nachziehen, nicht neu create.
            command.stamp(cfg, "head")
        else:
            command.upgrade(cfg, "head")
