"""Use Case — externes Kommando aktualisieren."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import ExternesKommandoNichtGefunden
from domain.katalog.externes_kommando import ExternesKommando
from domain.shared.errors import InvariantViolation
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class ExternesKommandoAktualisieren:
    bibliothek: BibliothekRepository

    def execute(
        self,
        kommando_id: str,
        *,
        bezeichnung: str,
        kommandocode: str,
    ) -> ExternesKommando:
        if self.bibliothek.get_externes_kommando(kommando_id) is None:
            raise ExternesKommandoNichtGefunden(
                f"Externes Kommando {kommando_id} nicht gefunden"
            )
        bezeichnung = bezeichnung.strip()
        kommandocode = kommandocode.strip()
        if not bezeichnung:
            raise InvariantViolation("Bezeichnung des externen Kommandos darf nicht leer sein")
        if not kommandocode:
            raise InvariantViolation("Kommandocode darf nicht leer sein")
        aktualisiert = ExternesKommando(
            kommando_id=kommando_id,
            bezeichnung=bezeichnung,
            kommandocode=kommandocode,
        )
        self.bibliothek.save_externes_kommando(aktualisiert)
        return aktualisiert
