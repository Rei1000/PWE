"""Katalog — Produktdefinition (Entwurf).

Fachliche Referenz: docs/domain-model.md §4.4
Materialisierung: docs/adr/0005-sollvorgaben-materialisierung.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from domain.katalog.materialisierung import materialisiere_sollvorgaben
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.shared.errors import InvariantViolation


@dataclass
class ProzedurSchrittEntwurf:
    """ProzedurSchritt im Entwurf — noch nicht materialisiert."""

    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any] = field(default_factory=dict)


@dataclass
class Produktdefinition:
    """Editierbarer Entwurf — wird durch Veröffentlichen zur Version."""

    produktdefinition_id: str
    produktkodierung: str
    basisprodukt_sollvorgaben: dict[str, Any] = field(default_factory=dict)
    kundenprofil_sollvorgaben: dict[str, Any] = field(default_factory=dict)
    definition_sollvorgaben: dict[str, Any] = field(default_factory=dict)
    prozedur_schritte: list[ProzedurSchrittEntwurf] = field(default_factory=list)
    sollbestueckung: tuple[str, ...] = ()
    aktive_version_id: str | None = None

    @classmethod
    def anlegen(cls, *, produktkodierung: str) -> Produktdefinition:
        return cls(
            produktdefinition_id=str(uuid4()),
            produktkodierung=produktkodierung,
        )

    def veroeffentlichen(self) -> ProduktdefinitionsVersion:
        if not self.prozedur_schritte:
            raise InvariantViolation("Veröffentlichen erfordert mindestens einen ProzedurSchritt")

        materialisierte = tuple(
            MaterialisierterProzedurSchritt(
                schritt_id=schritt.schritt_id,
                vorlage_id=schritt.vorlage_id,
                ist_pflicht=schritt.ist_pflicht,
                reihenfolge=schritt.reihenfolge,
                sollvorgaben=materialisiere_sollvorgaben(
                    self.basisprodukt_sollvorgaben,
                    self.kundenprofil_sollvorgaben,
                    self.definition_sollvorgaben,
                    schritt.sollvorgaben,
                ),
            )
            for schritt in self.prozedur_schritte
        )

        version = ProduktdefinitionsVersion(
            version_id=str(uuid4()),
            produktdefinition_id=self.produktdefinition_id,
            produktkodierung=self.produktkodierung,
            prozedur_schritte=materialisierte,
            sollbestueckung=self.sollbestueckung,
        )
        self.aktive_version_id = version.version_id
        return version
