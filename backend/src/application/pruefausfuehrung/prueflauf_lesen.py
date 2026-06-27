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

        schritte: list[SchrittDurchfuehrungAnsicht] = []
        for materialisiert in version.aktive_schritte():
            durchfuehrung = prueflauf.durchfuehrungen.get(materialisiert.schritt_id)
            nachweise = durchfuehrung.nachweise if durchfuehrung else []
            beurteilung = durchfuehrung.beurteilung if durchfuehrung else None

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
                )
            )

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
        )
