"""Protokoll — ProtokollSnapshot.

Fachliche Referenz: docs/domain-model.md §4.19
ADR: docs/adr/0004-protokollsnapshot-mindestinhalt.md, ADR-0008
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.pruefausfuehrung.abschluss_view import PrueflaufAbschlussView, SchrittAbschlussView
from domain.shared.errors import InvariantViolation


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
    schritte: tuple[SchrittAbschlussView, ...]
    fehlende_sollbestueckung: tuple[str, ...] = ()

    @classmethod
    def aus_abschluss(cls, snapshot_id: str, view: PrueflaufAbschlussView) -> ProtokollSnapshot:
        if view.abgeschlossen_am is None:
            raise InvariantViolation("ProtokollSnapshot nur für abgeschlossenen Prüflauf")

        return cls(
            snapshot_id=snapshot_id,
            prueflauf_id=view.prueflauf_id,
            version_id=view.version_id,
            pruefobjekt_kennung=view.pruefobjekt_kennung,
            produktkodierung=view.produktkodierung,
            pruefer_id=view.pruefer_id,
            gestartet_am=view.gestartet_am,
            abgeschlossen_am=view.abgeschlossen_am,
            ist_gueltig=view.ist_gueltig,
            schritte=view.schritte,
            fehlende_sollbestueckung=view.fehlende_sollbestueckung,
        )
