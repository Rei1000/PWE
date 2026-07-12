"""Port — atomische Persistierung beim Prüflauf-Abschluss."""

from __future__ import annotations

from typing import Protocol

from domain.pruefausfuehrung.prueflauf import Prueflauf
from domain.protokoll.snapshot import ProtokollSnapshot


class PrueflaufAbschlussPersistenz(Protocol):
    def speichern(self, prueflauf: Prueflauf, snapshot: ProtokollSnapshot) -> None: ...
