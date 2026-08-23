"""Use Case: Foto-Datei eines Nachweises lesen (ADR-0022)."""

from __future__ import annotations

from dataclasses import dataclass

from domain.pruefausfuehrung.datei_verweis import DateiVerweis
from domain.pruefausfuehrung.errors import (
    DateiNichtGefunden,
    DateiSpeicherungFehlgeschlagen,
    NachweisKeinFoto,
    NachweisNichtGefunden,
    PrueflaufNichtGefunden,
)
from domain.pruefausfuehrung.typen import Nachweis, NachweisArt
from domain.shared.errors import InvariantViolation
from ports.datei_speicher_port import DateiSpeicherPort
from ports.prueflauf_repository import PrueflaufRepository

from ports.datei_speicher_port import DateiSpeicherFehler


@dataclass(frozen=True)
class NachweisDateiInhalt:
    inhalt: bytes
    mime_type: str
    dateiname: str | None


@dataclass
class NachweisDateiLesen:
    prueflauf_repo: PrueflaufRepository
    datei_speicher: DateiSpeicherPort

    def execute(self, prueflauf_id: str, nachweis_id: str) -> NachweisDateiInhalt:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(prueflauf_id)

        nachweis = self._finde_nachweis(prueflauf, nachweis_id)
        if nachweis.art != NachweisArt.FOTO:
            raise NachweisKeinFoto(nachweis_id)

        try:
            verweis = DateiVerweis.from_payload(nachweis.payload)
        except (KeyError, TypeError, ValueError, InvariantViolation) as exc:
            raise NachweisKeinFoto(nachweis_id) from exc

        try:
            inhalt, gespeichertes_mime = self.datei_speicher.lesen(verweis.datei_id)
        except DateiSpeicherFehler as exc:
            raise DateiNichtGefunden(verweis.datei_id) from exc

        mime_type = verweis.mime_type or gespeichertes_mime
        return NachweisDateiInhalt(
            inhalt=inhalt,
            mime_type=mime_type,
            dateiname=verweis.dateiname,
        )

    def _finde_nachweis(self, prueflauf, nachweis_id: str) -> Nachweis:
        for durchfuehrung in prueflauf.durchfuehrungen.values():
            for nachweis in durchfuehrung.nachweise:
                if nachweis.nachweis_id == nachweis_id:
                    return nachweis
        for nachweis in prueflauf.bestueckung_nachweise:
            if nachweis.nachweis_id == nachweis_id:
                return nachweis
        raise NachweisNichtGefunden(nachweis_id)
