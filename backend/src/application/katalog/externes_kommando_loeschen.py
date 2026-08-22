"""Use Case — externes Kommando löschen."""

from __future__ import annotations

from dataclasses import dataclass

from application.katalog.bibliothek_referenzen import ist_kommando_in_verwendung
from domain.katalog.errors import ExternesKommandoNichtGefunden, KommandoInVerwendung
from ports.bibliothek_repository import BibliothekRepository
from ports.katalog_repository import KatalogRepository


@dataclass
class ExternesKommandoLoeschen:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository

    def execute(self, kommando_id: str) -> None:
        if self.bibliothek.get_externes_kommando(kommando_id) is None:
            raise ExternesKommandoNichtGefunden(
                f"Externes Kommando {kommando_id} nicht gefunden"
            )
        if ist_kommando_in_verwendung(self.katalog, self.bibliothek, kommando_id):
            raise KommandoInVerwendung(
                f"Externes Kommando {kommando_id} wird noch referenziert"
            )
        self.bibliothek.delete_externes_kommando(kommando_id)
