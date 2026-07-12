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
from ports.bibliothek_repository import BibliothekRepository
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


def in_memory_deps() -> ApiDeps:
    """Explizites In-Memory-Wiring für Entwicklung, Tests und CI ohne PostgreSQL."""
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()
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
    )


def get_request_deps(request: Request) -> ApiDeps:
    """Request-scoped Deps (PostgreSQL) oder app-weite Deps (In-Memory / injiziert)."""
    request_deps = getattr(request.state, "deps", None)
    if request_deps is not None:
        return request_deps
    return request.app.state.deps
