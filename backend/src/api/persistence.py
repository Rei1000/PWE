"""Persistenz-Konfiguration und PostgreSQL-Wiring für die API (Composition Root)."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from adapters.persistence.postgresql.bibliothek_repository import PostgresBibliothekRepository
from adapters.persistence.postgresql.abschluss_persistenz import PostgresPrueflaufAbschlussPersistenz
from adapters.persistence.postgresql.identity_repository import (
    PostgresBenutzerRepository,
    PostgresSessionStore,
)
from adapters.persistence.postgresql.katalog_repository import PostgresKatalogRepository
from adapters.persistence.postgresql.protokoll_repository import PostgresProtokollRepository
from adapters.persistence.postgresql.prueflauf_repository import PostgresPrueflaufRepository
from adapters.pdf.protokoll_erzeugung import PdfProtokollErzeugungAdapter
from adapters.security.argon2_hasher import Argon2PasswortHasher
from api.deps import ApiDeps
from api.kommando_wiring import create_kommando_port
from ports.datei_speicher_port import DateiSpeicherPort

PersistenceMode = Literal["in-memory", "postgresql"]
PostgresDepsFactory = Callable[[Session, DateiSpeicherPort], ApiDeps]

# Erwartete Kern-Tabelle nach `alembic upgrade head` (Gate 7.5b).
_REQUIRED_TABLE = "produktdefinitions_version"


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


def assert_postgresql_schema_ready(engine: Engine) -> None:
    """Prüft, dass Alembic-Migrationen angewendet wurden — erzeugt kein Schema."""
    tables = set(inspect(engine).get_table_names())
    if _REQUIRED_TABLE not in tables:
        raise PersistenceConfigurationError(
            "PostgreSQL ist erreichbar, aber das erwartete Schema fehlt "
            f"(Tabelle '{_REQUIRED_TABLE}' nicht gefunden). "
            "Bitte zuerst `alembic upgrade head` ausführen."
        )


def initialize_postgresql_engine(database_url: str) -> Engine:
    """Engine erzeugen, Verbindung prüfen und erwartetes Schema verifizieren.

    Erzeugt oder verändert kein Schema (Gate 7.5b). Voraussetzung: `alembic upgrade head`.
    """
    engine = create_sqlalchemy_engine(database_url)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        assert_postgresql_schema_ready(engine)
    except PersistenceConfigurationError:
        engine.dispose()
        raise
    except Exception as exc:
        engine.dispose()
        raise PersistenceConfigurationError(
            "PostgreSQL ist über DATABASE_URL konfiguriert, aber nicht erreichbar "
            "oder das Schema konnte nicht geprüft werden."
        ) from exc
    return engine


def postgres_deps(session: Session, datei_speicher: DateiSpeicherPort) -> ApiDeps:
    """Request-scoped ApiDeps mit allen PostgreSQL-Repositories."""
    prueflauf_repo = PostgresPrueflaufRepository(session)
    protokoll_repo = PostgresProtokollRepository(session)
    hasher = Argon2PasswortHasher()
    return ApiDeps(
        katalog=PostgresKatalogRepository(session),
        bibliothek=PostgresBibliothekRepository(session),
        prueflauf_repo=prueflauf_repo,
        protokoll_repo=protokoll_repo,
        abschluss_persistenz=PostgresPrueflaufAbschlussPersistenz(session),
        erzeugung_port=PdfProtokollErzeugungAdapter(),
        kommando_port=create_kommando_port(),
        datei_speicher=datei_speicher,
        benutzer_repo=PostgresBenutzerRepository(session),
        passwort_hasher=hasher,
        session_store=PostgresSessionStore(session),
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
