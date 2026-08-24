"""Use Case — Startbare Prüfungen für Benutzer (Polish A)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from application.pruefausfuehrung.start_qualifikation_hilfe import (
    ist_start_qualifiziert_fuer_version,
)
from ports.benutzer_repository import BenutzerRepository
from ports.berechtigungsprofil_repository import BerechtigungsprofilRepository
from ports.einweisungsnachweis_repository import EinweisungsnachweisRepository
from ports.katalog_repository import KatalogRepository


@dataclass(frozen=True)
class StartbarePruefung:
    produktkodierung: str


@dataclass
class StartbarePruefungenListen:
    katalog: KatalogRepository
    benutzer_repo: BenutzerRepository
    profile: BerechtigungsprofilRepository
    einweisungen: EinweisungsnachweisRepository

    def execute(self, *, benutzer_id: str) -> list[StartbarePruefung]:
        jetzt = datetime.now(UTC)
        result: list[StartbarePruefung] = []
        for version in self.katalog.list_aktive_versionen():
            if ist_start_qualifiziert_fuer_version(
                benutzer_repo=self.benutzer_repo,
                profile=self.profile,
                einweisungen=self.einweisungen,
                benutzer_id=benutzer_id,
                version=version,
                jetzt=jetzt,
            ):
                result.append(StartbarePruefung(produktkodierung=version.produktkodierung))
        return sorted(result, key=lambda item: item.produktkodierung)
