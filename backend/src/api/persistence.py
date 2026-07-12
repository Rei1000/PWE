"""Persistenz-Konfiguration und PostgreSQL-Wiring für die API (Composition Root)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from adapters.persistence.postgresql.abschluss_persistenz import PostgresPrueflaufAbschlussPersistenz
from adapters.persistence.postgresql.katalog_repository import PostgresKatalogRepository
from adapters.persistence.postgresql.protokoll_repository import PostgresProtokollRepository
from adapters.persistence.postgresql.prueflauf_repository import PostgresPrueflaufRepository
from adapters.persistence.postgresql.schema import init_schema
from adapters.pdf.protokoll_erzeugung import PdfProtokollErzeugungAdapter
from api.deps import ApiDeps

PersistenceMode = Literal["in-memory", "postgresql"]


class PersistenceConfigurationError(RuntimeError):
    """Ungültige oder nicht erreichbare Datenbankkonfiguration beim Start."""


@dataclass(frozen=True)
class PersistenceSettings:
    database_url: str | None

    @classmethod
    def from_env(cls) -> PersistenceSettings:
        raw = os.environ.get("DATABASE_URL")
        if raw is None or not raw.strip():
            return cls(database_url=None)
        return cls(database_url=raw.strip())

    @property
    def mode(self) -> PersistenceMode:
        return "postgresql" if self.database_url else "in-memory"


def create_sqlalchemy_engine(database_url: str) -> Engine:
    return create_engine(database_url, future=True)


def initialize_postgresql_engine(database_url: str) -> Engine:
    """Engine erzeugen, Schema sicherstellen und Verbindung prüfen."""
    engine = create_sqlalchemy_engine(database_url)
    try:
        init_schema(engine)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        engine.dispose()
        raise PersistenceConfigurationError(
            "PostgreSQL ist über DATABASE_URL konfiguriert, aber nicht erreichbar "
            "oder das Schema konnte nicht initialisiert werden."
        ) from exc
    return engine


def postgres_deps(session: Session) -> ApiDeps:
    """Request-scoped ApiDeps mit allen PostgreSQL-Repositories."""
    prueflauf_repo = PostgresPrueflaufRepository(session)
    protokoll_repo = PostgresProtokollRepository(session)
    return ApiDeps(
        katalog=PostgresKatalogRepository(session),
        prueflauf_repo=prueflauf_repo,
        protokoll_repo=protokoll_repo,
        abschluss_persistenz=PostgresPrueflaufAbschlussPersistenz(session),
        erzeugung_port=PdfProtokollErzeugungAdapter(),
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
