"""DateiVerweis — Value Object für Foto-Nachweis-Payload (ADR-0022)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain.pruefausfuehrung.foto_regeln import (
    MAX_FOTO_GROESSE_BYTES,
    erlaubter_mime_type,
    ist_erlaubte_groesse,
)
from domain.shared.errors import InvariantViolation


@dataclass(frozen=True)
class DateiVerweis:
    datei_id: str
    mime_type: str
    groesse_bytes: int
    dateiname: str | None = None

    def __post_init__(self) -> None:
        if not self.datei_id or not self.datei_id.strip():
            raise InvariantViolation("datei_id darf nicht leer sein")
        if not erlaubter_mime_type(self.mime_type):
            raise InvariantViolation(f"Nicht unterstützter MIME-Typ: {self.mime_type}")
        if self.groesse_bytes <= 0:
            raise InvariantViolation("Dateigröße muss größer als 0 sein")
        if not ist_erlaubte_groesse(self.groesse_bytes):
            raise InvariantViolation(
                f"Dateigröße überschreitet das Maximum von {MAX_FOTO_GROESSE_BYTES} Bytes"
            )

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "datei_id": self.datei_id,
            "mime_type": self.mime_type,
            "groesse_bytes": self.groesse_bytes,
        }
        if self.dateiname is not None:
            payload["dateiname"] = self.dateiname
        return payload

    @classmethod
    def from_payload(cls, data: dict[str, Any]) -> DateiVerweis:
        return cls(
            datei_id=str(data["datei_id"]),
            mime_type=str(data["mime_type"]),
            groesse_bytes=int(data["groesse_bytes"]),
            dateiname=data.get("dateiname"),
        )
