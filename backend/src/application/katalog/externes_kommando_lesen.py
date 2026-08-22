"""Use Case — ein externes Kommando lesen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import ExternesKommandoNichtGefunden
from domain.katalog.externes_kommando import ExternesKommando
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class ExternesKommandoLesen:
    bibliothek: BibliothekRepository

    def execute(self, kommando_id: str) -> ExternesKommando:
        kommando = self.bibliothek.get_externes_kommando(kommando_id)
        if kommando is None:
            raise ExternesKommandoNichtGefunden(
                f"Externes Kommando {kommando_id} nicht gefunden"
            )
        return kommando
