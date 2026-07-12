"""Katalog — Produktdefinition (Entwurf).

Fachliche Referenz: docs/domain-model.md §4.4
Materialisierung: docs/adr/0005-sollvorgaben-materialisierung.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from domain.katalog.externes_kommando import ExternesKommando, MaterialisiertesExternesKommando
from domain.katalog.errors import ExternesKommandoNichtGefunden
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
    kommando_id: str | None = None


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

    def veroeffentlichen(
        self,
        *,
        externe_kommandos: dict[str, ExternesKommando] | None = None,
    ) -> ProduktdefinitionsVersion:
        if not self.prozedur_schritte:
            raise InvariantViolation("Veröffentlichen erfordert mindestens einen ProzedurSchritt")

        aufgeloeste = externe_kommandos or {}
        materialisierte: list[MaterialisierterProzedurSchritt] = []
        for schritt in self.prozedur_schritte:
            kommando_snapshot: MaterialisiertesExternesKommando | None = None
            if schritt.kommando_id is not None:
                kommando = aufgeloeste.get(schritt.kommando_id)
                if kommando is None:
                    raise ExternesKommandoNichtGefunden(
                        f"Externes Kommando {schritt.kommando_id} nicht gefunden"
                    )
                kommando_snapshot = MaterialisiertesExternesKommando.aus(kommando)
            materialisierte.append(
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
                    externes_kommando=kommando_snapshot,
                )
            )
        materialisierte_tuple = tuple(materialisierte)

        version = ProduktdefinitionsVersion(
            version_id=str(uuid4()),
            produktdefinition_id=self.produktdefinition_id,
            produktkodierung=self.produktkodierung,
            prozedur_schritte=materialisierte_tuple,
            sollbestueckung=self.sollbestueckung,
        )
        self.aktive_version_id = version.version_id
        return version
