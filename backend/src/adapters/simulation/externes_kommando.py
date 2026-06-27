"""Simulations-Adapter für ExternesKommandoPort (ADR-0001, Tests/V1)."""

from __future__ import annotations

from domain.pruefausfuehrung.kommando_ausfuehrung import (
    ExternesKommandoAnfrage,
    ExternesKommandoAntwort,
)


class SimuliertesExternesKommandoPort:
    """Konfigurierbare Antworten — ersetzt COM-Hardware in Tests und Entwicklung."""

    def __init__(
        self,
        antworten: dict[str, ExternesKommandoAntwort] | None = None,
    ) -> None:
        self._antworten: dict[str, ExternesKommandoAntwort] = dict(antworten or {})

    def registriere_antwort(self, kommandocode: str, antwort: ExternesKommandoAntwort) -> None:
        self._antworten[kommandocode] = antwort

    def ausfuehren(self, anfrage: ExternesKommandoAnfrage) -> ExternesKommandoAntwort:
        if anfrage.kommandocode not in self._antworten:
            return ExternesKommandoAntwort(
                rohdaten="",
                erfolgreich=False,
            )
        return self._antworten[anfrage.kommandocode]
