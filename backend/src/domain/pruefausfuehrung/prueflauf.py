"""Prüfausführung — Aggregate Prueflauf.

Fachliche Referenz: docs/domain-model.md §4.15–§4.18
ADR: docs/adr/0003-routine-nachweis-wellen.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from domain.shared.errors import InvariantViolation


class PrueflaufStatus(str, Enum):
    GESTARTET = "gestartet"
    IN_BEARBEITUNG = "in_bearbeitung"
    ABGESCHLOSSEN_GUELTIG = "abgeschlossen_gueltig"
    ABGESCHLOSSEN_UNGUELTIG = "abgeschlossen_ungueltig"


class NachweisArt(str, Enum):
    MESSWERT = "messwert"
    FOTO = "foto"
    KOMMENTAR = "kommentar"
    MANUELLE_EINGABE = "manuelle_eingabe"
    ROHANTWORT = "rohantwort"
    EXTRAHIERTER_WERT = "extrahierter_wert"
    ERGAENZUNG = "ergaenzung"
    KOMPONENTENERFASSUNG = "komponentenerfassung"


class BeurteilungErgebnis(str, Enum):
    BESTANDEN = "bestanden"
    NICHT_BESTANDEN = "nicht_bestanden"
    BESTANDEN_MIT_KOMMENTAR = "bestanden_mit_kommentar"


@dataclass(frozen=True)
class Nachweis:
    """Domain Model §4.17 — automatische Nachweise unveränderlich."""

    nachweis_id: str
    art: NachweisArt
    erfasst_am: datetime
    payload: dict[str, Any]
    bezug_nachweis_id: str | None = None
    ist_automatisch: bool = False


@dataclass
class Beurteilung:
    """Domain Model §4.18 — änderbar solange Prüflauf offen."""

    ergebnis: BeurteilungErgebnis
    festgelegt_am: datetime
    kommentar: str | None = None


@dataclass
class PruefschrittDurchfuehrung:
    """Domain Model §4.16 — eine Durchführung pro ProzedurSchritt, Nachweis-Wellen."""

    prozedur_schritt_id: str
    nachweise: list[Nachweis] = field(default_factory=list)
    beurteilung: Beurteilung | None = None

    def add_nachweis(self, nachweis: Nachweis) -> None:
        self.nachweise.append(nachweis)

    def ist_abgeschlossen(self) -> bool:
        return self.beurteilung is not None


@dataclass
class Prueflauf:
    """Aggregate Root Prüfausführung (Domain Model §4.15)."""

    prueflauf_id: str
    version_id: str
    pruefobjekt_kennung: str
    produktkodierung: str
    pruefer_id: str
    gestartet_am: datetime
    status: PrueflaufStatus = PrueflaufStatus.GESTARTET
    durchfuehrungen: dict[str, PruefschrittDurchfuehrung] = field(default_factory=dict)
    abgeschlossen_am: datetime | None = None

    @classmethod
    def starten(
        cls,
        *,
        version_id: str,
        pruefobjekt_kennung: str,
        produktkodierung: str,
        pruefer_id: str,
        prozedur_schritt_ids: list[str],
    ) -> Prueflauf:
        prueflauf = cls(
            prueflauf_id=str(uuid4()),
            version_id=version_id,
            pruefobjekt_kennung=pruefobjekt_kennung,
            produktkodierung=produktkodierung,
            pruefer_id=pruefer_id,
            gestartet_am=_utcnow(),
            status=PrueflaufStatus.GESTARTET,
        )
        for schritt_id in prozedur_schritt_ids:
            prueflauf.durchfuehrungen[schritt_id] = PruefschrittDurchfuehrung(
                prozedur_schritt_id=schritt_id
            )
        return prueflauf

    def _ensure_offen(self) -> None:
        if self.status in (
            PrueflaufStatus.ABGESCHLOSSEN_GUELTIG,
            PrueflaufStatus.ABGESCHLOSSEN_UNGUELTIG,
        ):
            raise InvariantViolation("Abgeschlossener Prüflauf ist unveränderlich")

    def add_nachweis(
        self,
        prozedur_schritt_id: str,
        art: NachweisArt,
        payload: dict[str, Any],
        *,
        ist_automatisch: bool = False,
        bezug_nachweis_id: str | None = None,
    ) -> Nachweis:
        self._ensure_offen()
        if prozedur_schritt_id not in self.durchfuehrungen:
            raise InvariantViolation(f"Unbekannter ProzedurSchritt: {prozedur_schritt_id}")
        if self.status == PrueflaufStatus.GESTARTET:
            self.status = PrueflaufStatus.IN_BEARBEITUNG

        nachweis = Nachweis(
            nachweis_id=str(uuid4()),
            art=art,
            erfasst_am=_utcnow(),
            payload=payload,
            ist_automatisch=ist_automatisch,
            bezug_nachweis_id=bezug_nachweis_id,
        )
        self.durchfuehrungen[prozedur_schritt_id].add_nachweis(nachweis)
        return nachweis

    def set_beurteilung(
        self,
        prozedur_schritt_id: str,
        ergebnis: BeurteilungErgebnis,
        kommentar: str | None = None,
    ) -> None:
        self._ensure_offen()
        d = self.durchfuehrungen.get(prozedur_schritt_id)
        if d is None:
            raise InvariantViolation(f"Unbekannter ProzedurSchritt: {prozedur_schritt_id}")
        if d.beurteilung is not None:
            raise InvariantViolation("Beurteilung bereits festgelegt — neue Beurteilung nur via Korrektur V2")
        d.beurteilung = Beurteilung(ergebnis=ergebnis, festgelegt_am=_utcnow(), kommentar=kommentar)

    def abschliessen(self, pflicht_schritt_ids: set[str]) -> None:
        self._ensure_offen()
        ungueltig = False
        for schritt_id in pflicht_schritt_ids:
            d = self.durchfuehrungen.get(schritt_id)
            if d is None or d.beurteilung is None:
                ungueltig = True
                continue
            if d.beurteilung.ergebnis == BeurteilungErgebnis.NICHT_BESTANDEN:
                ungueltig = True

        self.abgeschlossen_am = _utcnow()
        self.status = (
            PrueflaufStatus.ABGESCHLOSSEN_UNGUELTIG
            if ungueltig
            else PrueflaufStatus.ABGESCHLOSSEN_GUELTIG
        )

    def ist_abgeschlossen(self) -> bool:
        return self.status in (
            PrueflaufStatus.ABGESCHLOSSEN_GUELTIG,
            PrueflaufStatus.ABGESCHLOSSEN_UNGUELTIG,
        )

    def ist_gueltig(self) -> bool:
        return self.status == PrueflaufStatus.ABGESCHLOSSEN_GUELTIG


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
