"""COM-Adapter für ExternesKommandoPort.

Erste Anwendung: serielle Gerätekommunikation. Protokoll-Details nur hier.
Hardware-Transport wird injiziert (Tests: InMemorySeriellerTransport).
"""

from __future__ import annotations

import re
from typing import Callable

from adapters.com.transport import SeriellerTransport
from domain.pruefausfuehrung.kommando_ausfuehrung import (
    ExternesKommandoAnfrage,
    ExternesKommandoAntwort,
)

_WERT_PATTERN = re.compile(r"(\w+)=([\d.]+)")


def standard_wert_extractor(rohdaten: str) -> dict[str, float | int]:
    """Parst key=number-Paare aus Geräteantworten (V1, konfigurierbar später)."""
    werte: dict[str, float | int] = {}
    for match in _WERT_PATTERN.finditer(rohdaten):
        key = match.group(1)
        raw = match.group(2)
        werte[key] = int(raw) if raw.isdigit() else float(raw)
    return werte


class ComExternesKommandoPort:
    def __init__(
        self,
        transport: SeriellerTransport,
        wert_extractor: Callable[[str], dict[str, float | int]] | None = None,
    ) -> None:
        self._transport = transport
        self._wert_extractor = wert_extractor or standard_wert_extractor

    def ausfuehren(self, anfrage: ExternesKommandoAnfrage) -> ExternesKommandoAntwort:
        wire = f"{anfrage.kommandocode}\r\n".encode("utf-8")
        roh_bytes = self._transport.send_and_receive(wire)
        rohdaten = roh_bytes.decode("utf-8").strip()
        erfolgreich = not rohdaten.upper().startswith("ERR")

        extrahierte: dict[str, float | int] = {}
        if erfolgreich:
            extrahierte = dict(self._wert_extractor(rohdaten))

        return ExternesKommandoAntwort(
            rohdaten=rohdaten,
            erfolgreich=erfolgreich,
            extrahierte_werte=extrahierte,
        )
