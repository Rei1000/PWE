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
from adapters.pdf.protokoll_erzeugung import PdfProtokollErzeugungAdapter
from adapters.storage.in_memory import InMemoryDateiSpeicher
from api.kommando_wiring import create_kommando_port
from ports.bibliothek_repository import BibliothekRepository
from ports.datei_speicher_port import DateiSpeicherPort
from ports.externes_kommando_port import ExternesKommandoPort
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_abschluss_persistenz import PrueflaufAbschlussPersistenz
from ports.protokoll_erzeugung_port import ProtokollErzeugungPort
from ports.protokoll_repository import ProtokollRepository
from ports.prueflauf_repository import PrueflaufRepository


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


def in_memory_deps(
    *,
    datei_speicher: InMemoryDateiSpeicher | None = None,
) -> ApiDeps:
    """Explizites In-Memory-Wiring für Entwicklung, Tests und CI ohne PostgreSQL."""
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()
    storage = datei_speicher or InMemoryDateiSpeicher()
    return ApiDeps(
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
    )


def get_request_deps(request: Request) -> ApiDeps:
    """Request-scoped Deps (PostgreSQL) oder app-weite Deps (In-Memory / injiziert)."""
    request_deps = getattr(request.state, "deps", None)
    if request_deps is not None:
        return request_deps
    return request.app.state.deps
