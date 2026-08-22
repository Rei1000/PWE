"""Use Case — alle externen Kommandos der Bibliothek listen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.externes_kommando import ExternesKommando
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class ExterneKommandosListen:
    bibliothek: BibliothekRepository

    def execute(self) -> list[ExternesKommando]:
        return self.bibliothek.list_externe_kommandos()
