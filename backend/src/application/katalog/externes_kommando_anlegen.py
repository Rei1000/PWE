"""Use Case — Externes Kommando in der Katalog-Bibliothek anlegen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.externes_kommando import ExternesKommando
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class ExternesKommandoAnlegen:
    bibliothek: BibliothekRepository

    def execute(self, *, bezeichnung: str, kommandocode: str) -> ExternesKommando:
        kommando = ExternesKommando.anlegen(bezeichnung=bezeichnung, kommandocode=kommandocode)
        self.bibliothek.save_externes_kommando(kommando)
        return kommando
