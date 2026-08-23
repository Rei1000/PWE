"""Use Case: Foto-Nachweis mit Binärdatei erfassen (ADR-0022)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from uuid import uuid4

from domain.pruefausfuehrung.datei_verweis import DateiVerweis
from domain.pruefausfuehrung.errors import (
    DateiSpeicherungFehlgeschlagen,
    DateiZuGross,
    PrueflaufNichtGefunden,
    UngueltigerDateityp,
)
from domain.pruefausfuehrung.foto_regeln import (
    MAX_FOTO_GROESSE_BYTES,
    erlaubter_mime_type,
    ist_erlaubte_groesse,
    magic_bytes_passen,
)
from domain.pruefausfuehrung.prueflauf import Nachweis, NachweisArt, Prueflauf
from domain.shared.errors import DomainError, InvariantViolation
from ports.datei_speicher_port import DateiSpeicherPort
from ports.prueflauf_repository import PrueflaufRepository

from ports.datei_speicher_port import DateiSpeicherFehler

logger = logging.getLogger(__name__)


@dataclass
class FotoNachweisErfassen:
    prueflauf_repo: PrueflaufRepository
    datei_speicher: DateiSpeicherPort

    def execute(
        self,
        prueflauf_id: str,
        prozedur_schritt_id: str,
        inhalt: bytes,
        mime_type: str,
        *,
        dateiname: str | None = None,
    ) -> Nachweis:
        prueflauf = self._lade_prueflauf(prueflauf_id)
        self._pruefe_vorbedingungen(prueflauf, prozedur_schritt_id, inhalt, mime_type)

        datei_id = str(uuid4())
        self._speichere_datei(datei_id, inhalt, mime_type)

        try:
            verweis = DateiVerweis(
                datei_id=datei_id,
                mime_type=mime_type,
                groesse_bytes=len(inhalt),
                dateiname=dateiname,
            )
            nachweis = prueflauf.add_nachweis(
                prozedur_schritt_id,
                NachweisArt.FOTO,
                verweis.to_payload(),
            )
            self.prueflauf_repo.save(prueflauf)
            return nachweis
        except (DomainError, InvariantViolation):
            self._compensate(datei_id)
            raise
        except Exception:
            self._compensate(datei_id)
            raise DateiSpeicherungFehlgeschlagen(
                "Nachweis konnte nach Dateispeicherung nicht persistiert werden"
            ) from None

    def _lade_prueflauf(self, prueflauf_id: str) -> Prueflauf:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(prueflauf_id)
        return prueflauf

    def _pruefe_vorbedingungen(
        self,
        prueflauf: Prueflauf,
        prozedur_schritt_id: str,
        inhalt: bytes,
        mime_type: str,
    ) -> None:
        prueflauf.stelle_offen_sicher()
        if prozedur_schritt_id not in prueflauf.durchfuehrungen:
            raise InvariantViolation(f"Unbekannter ProzedurSchritt: {prozedur_schritt_id}")
        if not inhalt:
            raise UngueltigerDateityp("Leere Datei ist nicht erlaubt")
        if not erlaubter_mime_type(mime_type):
            raise UngueltigerDateityp(f"Nicht unterstützter MIME-Typ: {mime_type}")
        if not ist_erlaubte_groesse(len(inhalt)):
            raise DateiZuGross(
                f"Dateigröße überschreitet das Maximum von {MAX_FOTO_GROESSE_BYTES} Bytes"
            )
        if not magic_bytes_passen(inhalt, mime_type):
            raise UngueltigerDateityp("Dateiinhalt entspricht nicht dem angegebenen Bildtyp")

    def _speichere_datei(self, datei_id: str, inhalt: bytes, mime_type: str) -> None:
        try:
            self.datei_speicher.speichern(datei_id, inhalt, mime_type)
        except DateiSpeicherFehler as exc:
            raise DateiSpeicherungFehlgeschlagen(
                "Datei konnte nicht gespeichert werden"
            ) from exc

    def _compensate(self, datei_id: str) -> None:
        try:
            self.datei_speicher.loeschen(datei_id)
        except DateiSpeicherFehler:
            logger.exception(
                "Compensation fehlgeschlagen für datei_id=%s nach Nachweis-Fehler",
                datei_id,
            )
