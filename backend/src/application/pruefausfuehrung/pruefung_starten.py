"""Use Case-Erweiterung — Qualifikation vor Prüflauf-Start (Gate 8.1b)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from domain.identity.start_qualifikation import (
    QualifikationUnzureichend,
    StartQualifikationKontext,
    start_qualifikation_erlaubt,
)
from domain.identity.typen import EinweisungsStatus
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

        benutzer = self.benutzer_repo.get(pruefer_id)
        if benutzer is None:
            raise QualifikationUnzureichend("Qualifikation unzureichend")

        profile = tuple(self.profile.profile_fuer_benutzer(pruefer_id))
        jetzt = datetime.now(UTC)
        for existing in self.einweisungen.list_fuer_benutzer_version(
            benutzer_id=pruefer_id, version_id=version.version_id
        ):
            if (
                existing.status == EinweisungsStatus.GUELTIG
                and not existing.ist_gueltig(jetzt=jetzt)
            ):
                self.einweisungen.save(existing.als_abgelaufen())
        einweisung = self.einweisungen.get_gueltige(
            benutzer_id=pruefer_id, version_id=version.version_id
        )

        start_qualifikation_erlaubt(
            StartQualifikationKontext(
                benutzer=benutzer,
                produktdefinition_id=version.produktdefinition_id,
                version_id=version.version_id,
                version_ist_aktive_veroeffentlichte=True,
                profile_des_benutzers=profile,
                gueltige_einweisung=einweisung,
                jetzt=jetzt,
            )
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
