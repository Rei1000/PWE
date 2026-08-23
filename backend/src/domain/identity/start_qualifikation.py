"""Identity — Domain Service StartQualifikation (Gate 8.1b, ADR-0026)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from domain.identity.benutzer import Benutzer
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import Einweisungsnachweis
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.shared.errors import DomainError


class QualifikationUnzureichend(DomainError):
    """Startregel nicht erfüllt — generische fachliche Ablehnung."""


@dataclass(frozen=True)
class StartQualifikationKontext:
    """Eingaben für die Startregel — nur IDs/Values, keine Katalog-Aggregate."""

    benutzer: Benutzer
    produktdefinition_id: str
    version_id: str
    version_ist_aktive_veroeffentlichte: bool
    profile_des_benutzers: tuple[Berechtigungsprofil, ...]
    gueltige_einweisung: Einweisungsnachweis | None
    jetzt: datetime | None = None


def start_qualifikation_erlaubt(ctx: StartQualifikationKontext) -> None:
    """Wirft QualifikationUnzureichend, wenn Start nicht erlaubt."""
    jetzt = ctx.jetzt or datetime.now(UTC)

    if ctx.benutzer.status != BenutzerStatus.AKTIV:
        raise QualifikationUnzureichend("Qualifikation unzureichend")
    if Systemrolle.PRUEFER not in ctx.benutzer.rollen:
        raise QualifikationUnzureichend("Qualifikation unzureichend")
    if not ctx.version_ist_aktive_veroeffentlichte:
        raise QualifikationUnzureichend("Qualifikation unzureichend")

    profil_ok = any(
        p.deckt_produktdefinition(ctx.produktdefinition_id) for p in ctx.profile_des_benutzers
    )
    if not profil_ok:
        raise QualifikationUnzureichend("Qualifikation unzureichend")

    if ctx.gueltige_einweisung is None:
        raise QualifikationUnzureichend("Qualifikation unzureichend")
    if ctx.gueltige_einweisung.version_id != ctx.version_id:
        raise QualifikationUnzureichend("Qualifikation unzureichend")
    if ctx.gueltige_einweisung.benutzer_id != ctx.benutzer.benutzer_id:
        raise QualifikationUnzureichend("Qualifikation unzureichend")
    if not ctx.gueltige_einweisung.ist_gueltig(jetzt=jetzt):
        raise QualifikationUnzureichend("Qualifikation unzureichend")
