"""Alembic environment — Schema aus adapters.persistence.postgresql.schema (Gate 7.5a/b).

PostgreSQL-Schemaänderungen erfolgen ausschließlich über Alembic-Migrationen.
Die FastAPI-Runtime erzeugt oder verändert kein Datenbankschema.

Optional: ALEMBIC_SCHEMA setzt search_path (Tests mit isoliertem Schema).
"""

from __future__ import annotations

import os

from alembic import context
from sqlalchemy import engine_from_config, pool, text

from adapters.persistence.postgresql.schema import Base

config = context.config

# Kein logging.config.fileConfig: die Standard-alembic.ini setzt root=WARN und
# disable_existing_loggers=True — das zerstört pytest-caplog und App-Logger
# nach CLI-/Test-Läufen. Alembic bleibt ohne ini-Logging voll nutzbar.

target_metadata = Base.metadata


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL ist nicht gesetzt. "
            "Beispiel: postgresql+psycopg://postgres:postgres@localhost:5432/app"
        )
    return url


def _apply_optional_schema(connection) -> None:
    schema = os.environ.get("ALEMBIC_SCHEMA", "").strip()
    if schema:
        connection.execute(text(f'SET search_path TO "{schema}"'))
        connection.commit()


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        _apply_optional_schema(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
