"""Gemeinsame Qualifikationsprüfung für Start und Discovery (Polish A)."""

from __future__ import annotations

from datetime import UTC, datetime

from domain.identity.start_qualifikation import (
    QualifikationUnzureichend,
    StartQualifikationKontext,
    start_qualifikation_erlaubt,
)
from domain.identity.typen import EinweisungsStatus
from domain.katalog.version import ProduktdefinitionsVersion
from ports.benutzer_repository import BenutzerRepository
from ports.berechtigungsprofil_repository import BerechtigungsprofilRepository
from ports.einweisungsnachweis_repository import EinweisungsnachweisRepository


def abgelaufene_einweisungen_markieren(
    einweisungen: EinweisungsnachweisRepository,
    *,
    benutzer_id: str,
    version_id: str,
    jetzt: datetime,
) -> None:
    for existing in einweisungen.list_fuer_benutzer_version(
        benutzer_id=benutzer_id, version_id=version_id
    ):
        if (
            existing.status == EinweisungsStatus.GUELTIG
            and not existing.ist_gueltig(jetzt=jetzt)
        ):
            einweisungen.save(existing.als_abgelaufen())


def ist_start_qualifiziert_fuer_version(
    *,
    benutzer_repo: BenutzerRepository,
    profile: BerechtigungsprofilRepository,
    einweisungen: EinweisungsnachweisRepository,
    benutzer_id: str,
    version: ProduktdefinitionsVersion,
    jetzt: datetime | None = None,
) -> bool:
    """True, wenn die Startregel für die Version erfüllt ist."""
    jetzt = jetzt or datetime.now(UTC)
    benutzer = benutzer_repo.get(benutzer_id)
    if benutzer is None:
        return False

    abgelaufene_einweisungen_markieren(
        einweisungen,
        benutzer_id=benutzer_id,
        version_id=version.version_id,
        jetzt=jetzt,
    )
    profile_des_benutzers = tuple(profile.profile_fuer_benutzer(benutzer_id))
    gueltige_einweisung = einweisungen.get_gueltige(
        benutzer_id=benutzer_id, version_id=version.version_id
    )

    try:
        start_qualifikation_erlaubt(
            StartQualifikationKontext(
                benutzer=benutzer,
                produktdefinition_id=version.produktdefinition_id,
                version_id=version.version_id,
                version_ist_aktive_veroeffentlichte=True,
                profile_des_benutzers=profile_des_benutzers,
                gueltige_einweisung=gueltige_einweisung,
                jetzt=jetzt,
            )
        )
        return True
    except QualifikationUnzureichend:
        return False


def pruefe_start_qualifikation_fuer_version(
    *,
    benutzer_repo: BenutzerRepository,
    profile: BerechtigungsprofilRepository,
    einweisungen: EinweisungsnachweisRepository,
    benutzer_id: str,
    version: ProduktdefinitionsVersion,
    jetzt: datetime | None = None,
) -> None:
    """Wirft QualifikationUnzureichend, wenn die Startregel nicht erfüllt ist."""
    if not ist_start_qualifiziert_fuer_version(
        benutzer_repo=benutzer_repo,
        profile=profile,
        einweisungen=einweisungen,
        benutzer_id=benutzer_id,
        version=version,
        jetzt=jetzt,
    ):
        raise QualifikationUnzureichend("Qualifikation unzureichend")
