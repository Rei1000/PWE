"""Fixtures für PostgreSQL-Adapter-Tests — Schema nur via Alembic (Gate 7.5b)."""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from adapters.persistence.postgresql.bibliothek_repository import PostgresBibliothekRepository
from adapters.persistence.postgresql.katalog_repository import PostgresKatalogRepository
from adapters.persistence.postgresql.protokoll_repository import PostgresProtokollRepository
from adapters.persistence.postgresql.prueflauf_repository import PostgresPrueflaufRepository
from tests.support.alembic_migrate import alembic_upgrade_head


def _database_url() -> str | None:
    return os.environ.get("DATABASE_URL")


@pytest.fixture(scope="session")
def pg_engine():
    url = _database_url()
    if not url:
        pytest.skip("DATABASE_URL nicht gesetzt — PostgreSQL-Tests übersprungen")
    schema = f"pwe_test_{uuid.uuid4().hex[:12]}"
    raw = create_engine(url, future=True)
    with raw.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
        conn.commit()
    raw.dispose()
    alembic_upgrade_head(database_url=url, schema=schema)
    engine = create_engine(url, future=True, connect_args={"options": f"-csearch_path={schema}"})
    yield engine
    engine.dispose()
    with create_engine(url, future=True).connect() as conn:
        conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        conn.commit()


@pytest.fixture
def pg_session(pg_engine) -> Session:
    connection = pg_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, expire_on_commit=False)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def pg_repos(pg_session):
    return (
        PostgresKatalogRepository(pg_session),
        PostgresBibliothekRepository(pg_session),
        PostgresPrueflaufRepository(pg_session),
        PostgresProtokollRepository(pg_session),
    )
