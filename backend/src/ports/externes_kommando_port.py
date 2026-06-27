"""Port — Externes Kommando an Prüfobjekte."""

from __future__ import annotations

from typing import Protocol

from domain.pruefausfuehrung.kommando_ausfuehrung import (
    ExternesKommandoAnfrage,
    ExternesKommandoAntwort,
)


class ExternesKommandoPort(Protocol):
    def ausfuehren(self, anfrage: ExternesKommandoAnfrage) -> ExternesKommandoAntwort: ...
