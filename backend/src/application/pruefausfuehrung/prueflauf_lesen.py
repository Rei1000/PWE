"""Use Case: Prüflauf lesen (Read Model für UI/API)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from domain.shared.errors import DomainError
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_repository import PrueflaufRepository


class PrueflaufNichtGefunden(DomainError):
    pass


class VersionNichtGefunden(DomainError):
    pass


@dataclass(frozen=True)
class NachweisAnsicht:
    nachweis_id: str
    art: str
    erfasst_am: datetime
    payload: dict[str, Any]
    ist_automatisch: bool


@dataclass(frozen=True)
class BeurteilungAnsicht:
    ergebnis: str
    festgelegt_am: datetime
    kommentar: str | None


@dataclass(frozen=True)
class SchrittDurchfuehrungAnsicht:
    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any]
    nachweise: tuple[NachweisAnsicht, ...]
    beurteilung: BeurteilungAnsicht | None
    kann_nachweis_erfassen: bool
    kann_beurteilt_werden: bool


@dataclass(frozen=True)
class PrueflaufDetailAnsicht:
    prueflauf_id: str
    version_id: str
    produktkodierung: str
    pruefobjekt_kennung: str
    pruefer_id: str
    status: str
    gestartet_am: datetime
    abgeschlossen_am: datetime | None
    schritte: tuple[SchrittDurchfuehrungAnsicht, ...]
    sollbestueckung: tuple[str, ...]
    erfasste_komponenten: tuple[str, ...]
    ist_abgeschlossen: bool
    fehlende_komponenten: tuple[str, ...]
    kann_komponente_erfassen: bool
    kann_abgeschlossen_werden: bool


@dataclass
class PrueflaufLesen:
    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository

    def execute(self, prueflauf_id: str) -> PrueflaufDetailAnsicht:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(f"Kein Prüflauf: {prueflauf_id}")

        version = self.katalog.get_version(prueflauf.version_id)
        if version is None:
            raise VersionNichtGefunden(
                f"Keine Version {prueflauf.version_id} für Prüflauf {prueflauf_id}"
            )

        ist_abgeschlossen = prueflauf.ist_abgeschlossen()
        fehlende = prueflauf.fehlende_sollbestueckung(version.sollbestueckung)
        kann_komponente = not ist_abgeschlossen and len(fehlende) > 0

        schritte: list[SchrittDurchfuehrungAnsicht] = []
        alle_beurteilt = True
        for materialisiert in version.aktive_schritte():
            durchfuehrung = prueflauf.durchfuehrungen.get(materialisiert.schritt_id)
            nachweise = durchfuehrung.nachweise if durchfuehrung else []
            beurteilung = durchfuehrung.beurteilung if durchfuehrung else None
            if beurteilung is None:
                alle_beurteilt = False

            schritte_offen = not ist_abgeschlossen and len(fehlende) == 0
            kann_nachweis = schritte_offen and beurteilung is None and len(nachweise) == 0
            kann_beurteilung = schritte_offen and beurteilung is None and len(nachweise) > 0

            schritte.append(
                SchrittDurchfuehrungAnsicht(
                    schritt_id=materialisiert.schritt_id,
                    vorlage_id=materialisiert.vorlage_id,
                    ist_pflicht=materialisiert.ist_pflicht,
                    reihenfolge=materialisiert.reihenfolge,
                    sollvorgaben=dict(materialisiert.sollvorgaben),
                    nachweise=tuple(
                        NachweisAnsicht(
                            nachweis_id=n.nachweis_id,
                            art=n.art.value,
                            erfasst_am=n.erfasst_am,
                            payload=dict(n.payload),
                            ist_automatisch=n.ist_automatisch,
                        )
                        for n in nachweise
                    ),
                    beurteilung=(
                        BeurteilungAnsicht(
                            ergebnis=beurteilung.ergebnis.value,
                            festgelegt_am=beurteilung.festgelegt_am,
                            kommentar=beurteilung.kommentar,
                        )
                        if beurteilung
                        else None
                    ),
                    kann_nachweis_erfassen=kann_nachweis,
                    kann_beurteilt_werden=kann_beurteilung,
                )
            )

        kann_abgeschlossen = not ist_abgeschlossen and len(fehlende) == 0 and alle_beurteilt

        return PrueflaufDetailAnsicht(
            prueflauf_id=prueflauf.prueflauf_id,
            version_id=prueflauf.version_id,
            produktkodierung=prueflauf.produktkodierung,
            pruefobjekt_kennung=prueflauf.pruefobjekt_kennung,
            pruefer_id=prueflauf.pruefer_id,
            status=prueflauf.status.value,
            gestartet_am=prueflauf.gestartet_am,
            abgeschlossen_am=prueflauf.abgeschlossen_am,
            schritte=tuple(schritte),
            sollbestueckung=version.sollbestueckung,
            erfasste_komponenten=tuple(sorted(prueflauf.erfasste_komponenten)),
            ist_abgeschlossen=ist_abgeschlossen,
            fehlende_komponenten=fehlende,
            kann_komponente_erfassen=kann_komponente,
            kann_abgeschlossen_werden=kann_abgeschlossen,
        )
