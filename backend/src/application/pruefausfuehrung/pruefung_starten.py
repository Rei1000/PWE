"""Use Case-Erweiterung — Qualifikation vor Prüflauf-Start (Gate 8.1b)."""

from __future__ import annotations

from dataclasses import dataclass

from application.pruefausfuehrung.start_qualifikation_hilfe import (
    pruefe_start_qualifikation_fuer_version,
)
from domain.identity.start_qualifikation import QualifikationUnzureichend
from domain.pruefausfuehrung.prueflauf import Prueflauf
from domain.shared.errors import DomainError
from ports.benutzer_repository import BenutzerRepository
from ports.berechtigungsprofil_repository import BerechtigungsprofilRepository
from ports.einweisungsnachweis_repository import EinweisungsnachweisRepository
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_repository import PrueflaufRepository


class VersionNichtGefunden(DomainError):
    pass


@dataclass
class PruefungStarten:
    """Application-Orchestrierung: Katalog + Identity Startregel + Prüflauf (Gate 8.1b)."""

    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository
    benutzer_repo: BenutzerRepository
    profile: BerechtigungsprofilRepository
    einweisungen: EinweisungsnachweisRepository

    def execute(
        self,
        *,
        produktkodierung: str,
        pruefobjekt_kennung: str,
        pruefer_id: str,
    ) -> Prueflauf:
        version = self.katalog.get_aktive_version_fuer_kodierung(produktkodierung)
        if version is None:
            raise VersionNichtGefunden(f"Keine aktive Version für {produktkodierung}")

        if self.benutzer_repo.get(pruefer_id) is None:
            raise QualifikationUnzureichend("Qualifikation unzureichend")

        pruefe_start_qualifikation_fuer_version(
            benutzer_repo=self.benutzer_repo,
            profile=self.profile,
            einweisungen=self.einweisungen,
            benutzer_id=pruefer_id,
            version=version,
        )

        schritt_ids = [s.schritt_id for s in version.aktive_schritte()]
        prueflauf = Prueflauf.starten(
            version_id=version.version_id,
            pruefobjekt_kennung=pruefobjekt_kennung,
            produktkodierung=produktkodierung,
            pruefer_id=pruefer_id,
            prozedur_schritt_ids=schritt_ids,
        )
        self.prueflauf_repo.save(prueflauf)
        return prueflauf
