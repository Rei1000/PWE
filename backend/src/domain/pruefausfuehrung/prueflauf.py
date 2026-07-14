"""Prüfausführung — Aggregate Prueflauf."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from domain.pruefausfuehrung.abschluss_view import PrueflaufAbschlussView, SchrittAbschlussView
from domain.pruefausfuehrung.beurteilung_service import BeurteilungService
from domain.pruefausfuehrung.typen import (
    Beurteilung,
    BeurteilungErgebnis,
    Nachweis,
    NachweisArt,
    PrueflaufStatus,
)
from domain.shared.errors import InvariantViolation


@dataclass
class PruefschrittDurchfuehrung:
    prozedur_schritt_id: str
    nachweise: list[Nachweis] = field(default_factory=list)
    beurteilung: Beurteilung | None = None

    def add_nachweis(self, nachweis: Nachweis) -> None:
        self.nachweise.append(nachweis)


@dataclass
class Prueflauf:
    prueflauf_id: str
    version_id: str
    pruefobjekt_kennung: str
    produktkodierung: str
    pruefer_id: str
    gestartet_am: datetime
    status: PrueflaufStatus = PrueflaufStatus.GESTARTET
    durchfuehrungen: dict[str, PruefschrittDurchfuehrung] = field(default_factory=dict)
    abgeschlossen_am: datetime | None = None
    erfasste_komponenten: set[str] = field(default_factory=set)
    bestueckung_nachweise: list[Nachweis] = field(default_factory=list)
    fehlende_sollbestueckung_snapshot: tuple[str, ...] = ()

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

    def stelle_offen_sicher(self) -> None:
        """Prüft vor externen Seiteneffekten, dass der Lauf noch bearbeitbar ist."""
        if self.status in (
            PrueflaufStatus.ABGESCHLOSSEN_GUELTIG,
            PrueflaufStatus.ABGESCHLOSSEN_UNGUELTIG,
        ):
            raise InvariantViolation("Abgeschlossener Prüflauf ist unveränderlich")

    def _ensure_offen(self) -> None:
        self.stelle_offen_sicher()

    def _touch_bearbeitung(self) -> None:
        if self.status == PrueflaufStatus.GESTARTET:
            self.status = PrueflaufStatus.IN_BEARBEITUNG

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
        self._touch_bearbeitung()

        nachweis = Nachweis(
            nachweis_id=str(uuid4()),
            art=art,
            erfasst_am=_utcnow(),
            payload=dict(payload),
            ist_automatisch=ist_automatisch,
            bezug_nachweis_id=bezug_nachweis_id,
        )
        self.durchfuehrungen[prozedur_schritt_id].add_nachweis(nachweis)
        return nachweis

    def erfasse_komponente(self, komponenten_typ: str, seriennummer: str) -> Nachweis:
        self._ensure_offen()
        self._touch_bearbeitung()
        self.erfasste_komponenten.add(komponenten_typ)
        nachweis = Nachweis(
            nachweis_id=str(uuid4()),
            art=NachweisArt.KOMPONENTENERFASSUNG,
            erfasst_am=_utcnow(),
            payload={"komponenten_typ": komponenten_typ, "seriennummer": seriennummer},
        )
        self.bestueckung_nachweise.append(nachweis)
        return nachweis

    def fehlende_sollbestueckung(self, soll: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(typ for typ in soll if typ not in self.erfasste_komponenten)

    def beurteilen_schritt(self, prozedur_schritt_id: str, sollvorgaben: dict[str, Any]) -> Beurteilung:
        self._ensure_offen()
        d = self.durchfuehrungen.get(prozedur_schritt_id)
        if d is None:
            raise InvariantViolation(f"Unbekannter ProzedurSchritt: {prozedur_schritt_id}")
        self._touch_bearbeitung()

        ergebnis = BeurteilungService.aus_soll_und_nachweisen(d.nachweise, sollvorgaben)
        beurteilung = Beurteilung(ergebnis=ergebnis, festgelegt_am=_utcnow())
        d.beurteilung = beurteilung
        return beurteilung

    def abschliessen(
        self,
        pflicht_schritt_ids: frozenset[str],
        sollbestueckung: tuple[str, ...] = (),
    ) -> None:
        self._ensure_offen()
        ungueltig = False

        fehlend = self.fehlende_sollbestueckung(sollbestueckung)
        self.fehlende_sollbestueckung_snapshot = fehlend
        if fehlend:
            ungueltig = True

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

    def to_abschluss_view(self, pflicht_map: dict[str, bool]) -> PrueflaufAbschlussView:
        if not self.ist_abgeschlossen() or self.abgeschlossen_am is None:
            raise InvariantViolation("Abschluss-View nur für abgeschlossenen Prüflauf")

        schritte: list[SchrittAbschlussView] = []
        for schritt_id in sorted(self.durchfuehrungen.keys()):
            d = self.durchfuehrungen[schritt_id]
            ergebnis = d.beurteilung.ergebnis if d.beurteilung else None
            schritte.append(
                SchrittAbschlussView(
                    prozedur_schritt_id=schritt_id,
                    ist_pflicht=pflicht_map.get(schritt_id, False),
                    beurteilung=ergebnis,
                    nachweis_ids=tuple(n.nachweis_id for n in d.nachweise),
                )
            )

        return PrueflaufAbschlussView(
            prueflauf_id=self.prueflauf_id,
            version_id=self.version_id,
            pruefobjekt_kennung=self.pruefobjekt_kennung,
            produktkodierung=self.produktkodierung,
            pruefer_id=self.pruefer_id,
            gestartet_am=self.gestartet_am,
            abgeschlossen_am=self.abgeschlossen_am,
            ist_gueltig=self.ist_gueltig(),
            schritte=tuple(schritte),
            fehlende_sollbestueckung=self.fehlende_sollbestueckung_snapshot,
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


# Re-export für bestehende Imports
__all__ = [
    "Beurteilung",
    "BeurteilungErgebnis",
    "Nachweis",
    "NachweisArt",
    "Prueflauf",
    "PrueflaufStatus",
    "PruefschrittDurchfuehrung",
]
