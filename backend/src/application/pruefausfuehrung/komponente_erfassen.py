"""Use Case: Komponente für Istbestückung erfassen (ADR-0006)."""

from __future__ import annotations

from dataclasses import dataclass

from domain.pruefausfuehrung.prueflauf import Nachweis, Prueflauf
from domain.shared.errors import DomainError
from ports.prueflauf_repository import PrueflaufRepository


class PrueflaufNichtGefunden(DomainError):
    pass


@dataclass
class KomponenteErfassen:
    prueflauf_repo: PrueflaufRepository

    def execute(self, prueflauf_id: str, komponenten_typ: str, seriennummer: str) -> Nachweis:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(prueflauf_id)

        nachweis = prueflauf.erfasse_komponente(komponenten_typ, seriennummer)
        self.prueflauf_repo.save(prueflauf)
        return nachweis
