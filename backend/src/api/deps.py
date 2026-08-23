"""API-Abhängigkeiten — Wiring ohne Fachlogik."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from adapters.persistence.in_memory import (
    InMemoryBibliothekRepository,
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from adapters.persistence.in_memory_abschluss import InMemoryPrueflaufAbschlussPersistenz
from adapters.persistence.in_memory_identity import InMemoryBenutzerRepository, InMemorySessionStore
from adapters.pdf.protokoll_erzeugung import PdfProtokollErzeugungAdapter
from adapters.security.argon2_hasher import Argon2PasswortHasher
from adapters.storage.in_memory import InMemoryDateiSpeicher
from api.identity_seed import ensure_seed_administrator
from api.kommando_wiring import create_kommando_port
from ports.benutzer_repository import BenutzerRepository
from ports.bibliothek_repository import BibliothekRepository
from ports.datei_speicher_port import DateiSpeicherPort
from ports.externes_kommando_port import ExternesKommandoPort
from ports.katalog_repository import KatalogRepository
from ports.passwort_hasher import PasswortHasher
from ports.prueflauf_abschluss_persistenz import PrueflaufAbschlussPersistenz
from ports.protokoll_erzeugung_port import ProtokollErzeugungPort
from ports.protokoll_repository import ProtokollRepository
from ports.prueflauf_repository import PrueflaufRepository
from ports.session_store import SessionStore


@dataclass
class ApiDeps:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository
    prueflauf_repo: PrueflaufRepository
    protokoll_repo: ProtokollRepository
    abschluss_persistenz: PrueflaufAbschlussPersistenz
    erzeugung_port: ProtokollErzeugungPort
    kommando_port: ExternesKommandoPort
    datei_speicher: DateiSpeicherPort
    benutzer_repo: BenutzerRepository
    passwort_hasher: PasswortHasher
    session_store: SessionStore


def in_memory_deps(
    *,
    datei_speicher: InMemoryDateiSpeicher | None = None,
    seed_admin: bool = True,
) -> ApiDeps:
    """Explizites In-Memory-Wiring für Entwicklung, Tests und CI ohne PostgreSQL."""
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()
    storage = datei_speicher or InMemoryDateiSpeicher()
    hasher = Argon2PasswortHasher()
    benutzer_repo = InMemoryBenutzerRepository()
    session_store = InMemorySessionStore()
    deps = ApiDeps(
        katalog=katalog,
        bibliothek=bibliothek,
        prueflauf_repo=prueflauf_repo,
        protokoll_repo=protokoll_repo,
        abschluss_persistenz=InMemoryPrueflaufAbschlussPersistenz(
            prueflauf_repo=prueflauf_repo,
            protokoll_repo=protokoll_repo,
        ),
        erzeugung_port=PdfProtokollErzeugungAdapter(),
        kommando_port=create_kommando_port(),
        datei_speicher=storage,
        benutzer_repo=benutzer_repo,
        passwort_hasher=hasher,
        session_store=session_store,
    )
    if seed_admin:
        ensure_seed_administrator(benutzer_repo, hasher)
    return deps


def get_request_deps(request: Request) -> ApiDeps:
    """Request-scoped Deps (PostgreSQL) oder app-weite Deps (In-Memory / injiziert)."""
    request_deps = getattr(request.state, "deps", None)
    if request_deps is not None:
        return request_deps
    return request.app.state.deps
