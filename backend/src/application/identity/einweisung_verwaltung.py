"""Use Cases — Einweisungsnachweis (Gate 8.1b)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from domain.identity.einweisungsnachweis import (
    EinweisungBereitsGueltig,
    Einweisungsnachweis,
)
from domain.identity.typen import EinweisungsStatus
from domain.shared.errors import DomainError
from ports.benutzer_repository import BenutzerRepository
from ports.einweisungsnachweis_repository import EinweisungsnachweisRepository
from ports.katalog_repository import KatalogRepository


class EinweisungNichtGefunden(DomainError):
    pass


class VersionNichtGefundenFuerEinweisung(DomainError):
    pass


class BenutzerNichtGefundenFuerEinweisung(DomainError):
    pass


@dataclass
class EinweisungAnlegen:
    einweisungen: EinweisungsnachweisRepository
    benutzer: BenutzerRepository
    katalog: KatalogRepository

    def execute(
        self,
        *,
        benutzer_id: str,
        version_id: str,
        eingewiesen_durch: str,
        gueltig_bis: date | None = None,
        bemerkung: str | None = None,
    ) -> Einweisungsnachweis:
        if self.benutzer.get(benutzer_id) is None:
            raise BenutzerNichtGefundenFuerEinweisung(f"Benutzer {benutzer_id} nicht gefunden")
        if self.katalog.get_version(version_id) is None:
            raise VersionNichtGefundenFuerEinweisung(f"Version {version_id} nicht gefunden")

        # Abgelaufene gültige Records lazy markieren
        existing_gueltig = self.einweisungen.get_gueltige(
            benutzer_id=benutzer_id, version_id=version_id
        )
        if existing_gueltig is not None:
            if existing_gueltig.ist_gueltig():
                raise EinweisungBereitsGueltig(
                    "Es existiert bereits eine gültige Einweisung für Benutzer und Version"
                )
            # Status war GUELTIG aber Datum abgelaufen → markieren und Slot freigeben
            self.einweisungen.save(existing_gueltig.als_abgelaufen())

        neu = Einweisungsnachweis.anlegen(
            benutzer_id=benutzer_id,
            version_id=version_id,
            eingewiesen_durch=eingewiesen_durch,
            gueltig_bis=gueltig_bis,
            bemerkung=bemerkung,
            datum=datetime.now(UTC),
        )
        self.einweisungen.save(neu)
        return neu


@dataclass
class EinweisungWiderrufen:
    einweisungen: EinweisungsnachweisRepository

    def execute(self, einweisung_id: str) -> Einweisungsnachweis:
        existing = self.einweisungen.get(einweisung_id)
        if existing is None:
            raise EinweisungNichtGefunden(f"Einweisung {einweisung_id} nicht gefunden")
        widerrufen = existing.widerrufen()
        self.einweisungen.save(widerrufen)
        return widerrufen


@dataclass
class EinweisungLesen:
    einweisungen: EinweisungsnachweisRepository

    def execute(self, einweisung_id: str) -> Einweisungsnachweis:
        e = self.einweisungen.get(einweisung_id)
        if e is None:
            raise EinweisungNichtGefunden(f"Einweisung {einweisung_id} nicht gefunden")
        return e
