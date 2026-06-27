"""Use Case: Nachweis an PrüfschrittDurchführung erfassen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain.pruefausfuehrung.prueflauf import Nachweis, NachweisArt, Prueflauf
from domain.shared.errors import DomainError
from ports.prueflauf_repository import PrueflaufRepository


class PrueflaufNichtGefunden(DomainError):
    pass


@dataclass
class NachweisErfassen:
    prueflauf_repo: PrueflaufRepository

    def execute(
        self,
        prueflauf_id: str,
        prozedur_schritt_id: str,
        art: NachweisArt,
        payload: dict[str, Any],
        *,
        ist_automatisch: bool = False,
    ) -> Nachweis:
        prueflauf = self._lade_offenen_prueflauf(prueflauf_id)
        nachweis = prueflauf.add_nachweis(
            prozedur_schritt_id, art, payload, ist_automatisch=ist_automatisch
        )
        self.prueflauf_repo.save(prueflauf)
        return nachweis

    def _lade_offenen_prueflauf(self, prueflauf_id: str) -> Prueflauf:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(prueflauf_id)
        return prueflauf
