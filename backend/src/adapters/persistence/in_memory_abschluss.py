"""In-Memory-Implementierung — PrueflaufAbschlussPersistenz."""

from __future__ import annotations

from dataclasses import dataclass

from adapters.persistence.in_memory import InMemoryProtokollRepository, InMemoryPrueflaufRepository
from domain.pruefausfuehrung.prueflauf import Prueflauf
from domain.protokoll.snapshot import ProtokollSnapshot


@dataclass
class InMemoryPrueflaufAbschlussPersistenz:
    prueflauf_repo: InMemoryPrueflaufRepository
    protokoll_repo: InMemoryProtokollRepository

    def speichern(self, prueflauf: Prueflauf, snapshot: ProtokollSnapshot) -> None:
        self.prueflauf_repo.save(prueflauf)
        self.protokoll_repo.save(snapshot)
