"""API-Abhängigkeiten — Wiring ohne Fachlogik."""

from __future__ import annotations

from dataclasses import dataclass

from adapters.persistence.in_memory import (
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from adapters.persistence.in_memory_abschluss import InMemoryPrueflaufAbschlussPersistenz
from adapters.pdf.protokoll_erzeugung import PdfProtokollErzeugungAdapter
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_abschluss_persistenz import PrueflaufAbschlussPersistenz
from ports.protokoll_erzeugung_port import ProtokollErzeugungPort
from ports.protokoll_repository import ProtokollRepository
from ports.prueflauf_repository import PrueflaufRepository


@dataclass
class ApiDeps:
    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository
    protokoll_repo: ProtokollRepository
    abschluss_persistenz: PrueflaufAbschlussPersistenz
    erzeugung_port: ProtokollErzeugungPort


def in_memory_deps() -> ApiDeps:
    """Standard-Wiring für Entwicklung und Tests (kein PostgreSQL in diesem Slice)."""
    katalog = InMemoryKatalogRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()
    return ApiDeps(
        katalog=katalog,
        prueflauf_repo=prueflauf_repo,
        protokoll_repo=protokoll_repo,
        abschluss_persistenz=InMemoryPrueflaufAbschlussPersistenz(
            prueflauf_repo=prueflauf_repo,
            protokoll_repo=protokoll_repo,
        ),
        erzeugung_port=PdfProtokollErzeugungAdapter(),
    )
