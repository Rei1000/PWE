"""Protokoll — ProtokollSnapshot.

Fachliche Referenz: docs/domain-model.md §4.19
ADR: docs/adr/0004-protokollsnapshot-mindestinhalt.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.pruefausfuehrung.prueflauf import BeurteilungErgebnis, Prueflauf


@dataclass(frozen=True)
class SchrittSnapshot:
    prozedur_schritt_id: str
    ist_pflicht: bool
    beurteilung: BeurteilungErgebnis | None
    nachweis_ids: tuple[str, ...]


@dataclass(frozen=True)
class ProtokollSnapshot:
    """Unveränderlicher Abschlussnachweis (Domain Model §4.19)."""

    snapshot_id: str
    prueflauf_id: str
    version_id: str
    pruefobjekt_kennung: str
    produktkodierung: str
    pruefer_id: str
    gestartet_am: datetime
    abgeschlossen_am: datetime
    ist_gueltig: bool
    schritte: tuple[SchrittSnapshot, ...]

    @classmethod
    def aus_prueflauf(
        cls,
        snapshot_id: str,
        prueflauf: Prueflauf,
        pflicht_map: dict[str, bool],
    ) -> ProtokollSnapshot:
        if not prueflauf.ist_abgeschlossen() or prueflauf.abgeschlossen_am is None:
            raise ValueError("ProtokollSnapshot nur für abgeschlossenen Prüflauf")

        schritte: list[SchrittSnapshot] = []
        for schritt_id, d in prueflauf.durchfuehrungen.items():
            ergebnis = d.beurteilung.ergebnis if d.beurteilung else None
            schritte.append(
                SchrittSnapshot(
                    prozedur_schritt_id=schritt_id,
                    ist_pflicht=pflicht_map.get(schritt_id, False),
                    beurteilung=ergebnis,
                    nachweis_ids=tuple(n.nachweis_id for n in d.nachweise),
                )
            )

        return cls(
            snapshot_id=snapshot_id,
            prueflauf_id=prueflauf.prueflauf_id,
            version_id=prueflauf.version_id,
            pruefobjekt_kennung=prueflauf.pruefobjekt_kennung,
            produktkodierung=prueflauf.produktkodierung,
            pruefer_id=prueflauf.pruefer_id,
            gestartet_am=prueflauf.gestartet_am,
            abgeschlossen_am=prueflauf.abgeschlossen_am,
            ist_gueltig=prueflauf.ist_gueltig(),
            schritte=tuple(schritte),
        )
