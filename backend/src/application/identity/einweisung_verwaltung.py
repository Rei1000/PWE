"""Use Cases — Einweisungsnachweis (Gate 8.1b)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from domain.identity.einweisungsnachweis import (
    EinweisungBereitsGueltig,
    Einweisungsnachweis,
)
from domain.identity.typen import BenutzerStatus, EinweisungsStatus
from domain.shared.errors import DomainError, InvariantViolation
from ports.benutzer_repository import BenutzerRepository
from ports.einweisungsnachweis_repository import EinweisungsnachweisRepository
from ports.identity_audit_repository import IdentityAuditRepository
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
    audit: IdentityAuditRepository | None = None

    def execute(
        self,
        *,
        benutzer_id: str,
        version_id: str,
        eingewiesen_durch: str,
        gueltig_bis: date | None = None,
        bemerkung: str | None = None,
        akteur_id: str | None = None,
    ) -> Einweisungsnachweis:
        ziel = self.benutzer.get(benutzer_id)
        if ziel is None:
            raise BenutzerNichtGefundenFuerEinweisung(f"Benutzer {benutzer_id} nicht gefunden")
        if ziel.status != BenutzerStatus.AKTIV:
            raise InvariantViolation("Einweisung nur für aktive Benutzer")
        if self.katalog.get_version(version_id) is None:
            raise VersionNichtGefundenFuerEinweisung(f"Version {version_id} nicht gefunden")

        # Gültige Einweisung blockiert; abgelaufene (Status noch GUELTIG) lazy markieren
        if self.einweisungen.get_gueltige(benutzer_id=benutzer_id, version_id=version_id) is not None:
            raise EinweisungBereitsGueltig(
                "Es existiert bereits eine gültige Einweisung für Benutzer und Version"
            )
        for existing in self.einweisungen.list_fuer_benutzer_version(
            benutzer_id=benutzer_id, version_id=version_id
        ):
            if existing.status == EinweisungsStatus.GUELTIG and not existing.ist_gueltig():
                self.einweisungen.save(existing.als_abgelaufen())

        neu = Einweisungsnachweis.anlegen(
            benutzer_id=benutzer_id,
            version_id=version_id,
            eingewiesen_durch=eingewiesen_durch,
            gueltig_bis=gueltig_bis,
            bemerkung=bemerkung,
            datum=datetime.now(UTC),
        )
        self.einweisungen.save(neu)
        if self.audit and akteur_id:
            from domain.identity.identity_audit import IdentityAuditEintrag

            self.audit.append(
                IdentityAuditEintrag.erzeugen(
                    akteur_benutzer_id=akteur_id,
                    aktion="einweisung_angelegt",
                    ziel_benutzer_id=benutzer_id,
                    referenz_id=neu.einweisung_id,
                    details={"version_id": version_id},
                )
            )
        return neu


@dataclass
class EinweisungWiderrufen:
    einweisungen: EinweisungsnachweisRepository
    audit: IdentityAuditRepository | None = None

    def execute(
        self, einweisung_id: str, *, akteur_id: str | None = None
    ) -> Einweisungsnachweis:
        existing = self.einweisungen.get(einweisung_id)
        if existing is None:
            raise EinweisungNichtGefunden(f"Einweisung {einweisung_id} nicht gefunden")
        widerrufen = existing.widerrufen()
        self.einweisungen.save(widerrufen)
        if self.audit and akteur_id:
            from domain.identity.identity_audit import IdentityAuditEintrag

            self.audit.append(
                IdentityAuditEintrag.erzeugen(
                    akteur_benutzer_id=akteur_id,
                    aktion="einweisung_widerrufen",
                    ziel_benutzer_id=widerrufen.benutzer_id,
                    referenz_id=widerrufen.einweisung_id,
                )
            )
        return widerrufen


@dataclass
class EinweisungLesen:
    einweisungen: EinweisungsnachweisRepository

    def execute(self, einweisung_id: str) -> Einweisungsnachweis:
        e = self.einweisungen.get(einweisung_id)
        if e is None:
            raise EinweisungNichtGefunden(f"Einweisung {einweisung_id} nicht gefunden")
        return e


@dataclass
class EinweisungenFuerBenutzerListen:
    einweisungen: EinweisungsnachweisRepository

    def execute(self, *, benutzer_id: str, version_id: str | None = None) -> list:
        if version_id:
            return self.einweisungen.list_fuer_benutzer_version(
                benutzer_id=benutzer_id, version_id=version_id
            )
        return self.einweisungen.list_fuer_benutzer(benutzer_id)
