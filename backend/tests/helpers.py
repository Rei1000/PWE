"""Wiederverwendbare Test-Bausteine."""

from __future__ import annotations

from adapters.persistence.in_memory import InMemoryProtokollRepository, InMemoryPrueflaufRepository
from adapters.persistence.in_memory_abschluss import InMemoryPrueflaufAbschlussPersistenz
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAnfrage, ExternesKommandoAntwort
from domain.pruefausfuehrung.prueflauf import Prueflauf
from ports.externes_kommando_port import ExternesKommandoPort
from ports.prueflauf_repository import PrueflaufRepository


def in_memory_abschluss_persistenz(
    prueflauf_repo: InMemoryPrueflaufRepository,
    protokoll_repo: InMemoryProtokollRepository,
) -> InMemoryPrueflaufAbschlussPersistenz:
    return InMemoryPrueflaufAbschlussPersistenz(
        prueflauf_repo=prueflauf_repo,
        protokoll_repo=protokoll_repo,
    )


class CountingKommandoPort:
    """Spy-Port — zählt `ausfuehren`-Aufrufe für Vorbedingungs-Tests."""

    def __init__(
        self,
        inner: ExternesKommandoPort | None = None,
        *,
        antworten: dict[str, ExternesKommandoAntwort] | None = None,
    ) -> None:
        self._inner = inner or SimuliertesExternesKommandoPort(antworten)
        self.ausfuehren_count = 0

    def ausfuehren(self, anfrage: ExternesKommandoAnfrage) -> ExternesKommandoAntwort:
        self.ausfuehren_count += 1
        return self._inner.ausfuehren(anfrage)


class CountingPrueflaufRepository(PrueflaufRepository):
    def __init__(self, inner: InMemoryPrueflaufRepository) -> None:
        self._inner = inner
        self.save_count = 0

    def save(self, prueflauf: Prueflauf) -> None:
        self.save_count += 1
        self._inner.save(prueflauf)

    def get(self, prueflauf_id: str) -> Prueflauf | None:
        return self._inner.get(prueflauf_id)

