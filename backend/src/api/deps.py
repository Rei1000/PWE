"""API-Abhängigkeiten — Wiring ohne Fachlogik."""

from __future__ import annotations

from dataclasses import dataclass

from adapters.persistence.in_memory import (
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from adapters.pdf.protokoll_erzeugung import PdfProtokollErzeugungAdapter
from ports.katalog_repository import KatalogRepository
from ports.protokoll_erzeugung_port import ProtokollErzeugungPort
from ports.protokoll_repository import ProtokollRepository
from ports.prueflauf_repository import PrueflaufRepository


@dataclass
class ApiDeps:
    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository
    protokoll_repo: ProtokollRepository
    erzeugung_port: ProtokollErzeugungPort


def in_memory_deps() -> ApiDeps:
    """Standard-Wiring für Entwicklung und Tests (kein PostgreSQL in diesem Slice)."""
    return ApiDeps(
        katalog=InMemoryKatalogRepository(),
        prueflauf_repo=InMemoryPrueflaufRepository(),
        protokoll_repo=InMemoryProtokollRepository(),
        erzeugung_port=PdfProtokollErzeugungAdapter(),
    )
