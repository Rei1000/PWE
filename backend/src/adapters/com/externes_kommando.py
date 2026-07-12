"""COM-Adapter für ExternesKommandoPort.

Erste Anwendung: serielle Gerätekommunikation. Protokoll-Details nur hier.
Hardware-Transport wird injiziert (Tests: InMemorySeriellerTransport).
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable

from adapters.com.errors import (
    TransportConnectionError,
    TransportIOError,
    TransportTimeout,
)
from adapters.com.transport import SeriellerTransport
from domain.pruefausfuehrung.kommando_ausfuehrung import (
    ExternesKommandoAnfrage,
    ExternesKommandoAntwort,
)

logger = logging.getLogger(__name__)

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
        logger.debug("COM command execute code_len=%s", len(anfrage.kommandocode))
        try:
            roh_bytes = self._transport.send_and_receive(wire)
        except TransportTimeout:
            logger.warning(
                "COM command timeout code=%s error_class=TransportTimeout",
                anfrage.kommandocode,
            )
            return ExternesKommandoAntwort(rohdaten="", erfolgreich=False)
        except TransportConnectionError:
            logger.warning(
                "COM command connection error code=%s error_class=TransportConnectionError",
                anfrage.kommandocode,
            )
            return ExternesKommandoAntwort(rohdaten="", erfolgreich=False)
        except TransportIOError:
            logger.warning(
                "COM command io error code=%s error_class=TransportIOError",
                anfrage.kommandocode,
            )
            return ExternesKommandoAntwort(rohdaten="", erfolgreich=False)

        try:
            rohdaten = roh_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            logger.warning(
                "COM command decode error code=%s received_bytes=%s",
                anfrage.kommandocode,
                len(roh_bytes),
            )
            return ExternesKommandoAntwort(rohdaten="", erfolgreich=False)

        erfolgreich = not rohdaten.upper().startswith("ERR")
        if not erfolgreich:
            logger.info(
                "COM command device error code=%s rohdaten_len=%s",
                anfrage.kommandocode,
                len(rohdaten),
            )
            return ExternesKommandoAntwort(
                rohdaten=rohdaten,
                erfolgreich=False,
            )

        try:
            extrahierte = dict(self._wert_extractor(rohdaten))
        except Exception:
            logger.warning(
                "COM command parse error code=%s rohdaten_len=%s",
                anfrage.kommandocode,
                len(rohdaten),
            )
            return ExternesKommandoAntwort(
                rohdaten=rohdaten,
                erfolgreich=False,
            )

        return ExternesKommandoAntwort(
            rohdaten=rohdaten,
            erfolgreich=True,
            extrahierte_werte=extrahierte,
        )
