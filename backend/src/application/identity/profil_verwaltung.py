"""Use Cases — Berechtigungsprofil (Gate 8.1b/8.1c1)."""

from __future__ import annotations

from dataclasses import dataclass

from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.identity_audit import IdentityAuditEintrag
from domain.shared.errors import DomainError
from ports.benutzer_repository import BenutzerRepository
from ports.berechtigungsprofil_repository import BerechtigungsprofilRepository
from ports.identity_audit_repository import IdentityAuditRepository


class ProfilNichtGefunden(DomainError):
    pass


class BenutzerNichtGefunden(DomainError):
    pass


def _audit_profil(
    audit: IdentityAuditRepository | None,
    *,
    akteur_id: str | None,
    aktion: str,
    profil: Berechtigungsprofil,
    details: dict | None = None,
) -> None:
    if audit is None or not akteur_id:
        return
    audit.append(
        IdentityAuditEintrag.erzeugen(
            akteur_benutzer_id=akteur_id,
            aktion=aktion,
            referenz_id=profil.profil_id,
            details=details or {"bezeichnung": profil.bezeichnung, "aktiv": profil.aktiv},
        )
    )


@dataclass
class ProfilAnlegen:
    profile: BerechtigungsprofilRepository
    audit: IdentityAuditRepository | None = None

    def execute(
        self,
        *,
        bezeichnung: str,
        beschreibung: str | None = None,
        produktdefinition_ids: list[str] | None = None,
        akteur_id: str | None = None,
    ) -> Berechtigungsprofil:
        profil = Berechtigungsprofil.anlegen(
            bezeichnung=bezeichnung,
            beschreibung=beschreibung,
            produktdefinition_ids=set(produktdefinition_ids or ()),
        )
        self.profile.save(profil)
        _audit_profil(
            self.audit,
            akteur_id=akteur_id,
            aktion="profil_angelegt",
            profil=profil,
        )
        return profil


@dataclass
class ProfilAktualisieren:
    profile: BerechtigungsprofilRepository
    audit: IdentityAuditRepository | None = None

    def execute(
        self,
        *,
        profil_id: str,
        bezeichnung: str,
        beschreibung: str | None = None,
        produktdefinition_ids: list[str] | None = None,
        akteur_id: str | None = None,
    ) -> Berechtigungsprofil:
        existing = self.profile.get(profil_id)
        if existing is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        updated = existing.mit_bezeichnung(bezeichnung, beschreibung)
        if produktdefinition_ids is not None:
            updated = updated.mit_produktdefinitionen(set(produktdefinition_ids))
        self.profile.save(updated)
        _audit_profil(
            self.audit,
            akteur_id=akteur_id,
            aktion="profil_aktualisiert",
            profil=updated,
        )
        return updated


@dataclass
class ProfilLesen:
    profile: BerechtigungsprofilRepository

    def execute(self, profil_id: str) -> Berechtigungsprofil:
        profil = self.profile.get(profil_id)
        if profil is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        return profil


@dataclass
class ProfileListen:
    profile: BerechtigungsprofilRepository

    def execute(self) -> list[Berechtigungsprofil]:
        return self.profile.list_all()


@dataclass
class ProfilDeaktivieren:
    profile: BerechtigungsprofilRepository
    audit: IdentityAuditRepository | None = None

    def execute(self, *, profil_id: str, akteur_id: str | None = None) -> Berechtigungsprofil:
        existing = self.profile.get(profil_id)
        if existing is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        updated = existing.deaktivieren()
        self.profile.save(updated)
        _audit_profil(
            self.audit, akteur_id=akteur_id, aktion="profil_deaktiviert", profil=updated
        )
        return updated


@dataclass
class ProfilAktivieren:
    profile: BerechtigungsprofilRepository
    audit: IdentityAuditRepository | None = None

    def execute(self, *, profil_id: str, akteur_id: str | None = None) -> Berechtigungsprofil:
        existing = self.profile.get(profil_id)
        if existing is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        updated = existing.aktivieren()
        self.profile.save(updated)
        _audit_profil(
            self.audit, akteur_id=akteur_id, aktion="profil_aktiviert", profil=updated
        )
        return updated


@dataclass
class ProfilBenutzerZuordnen:
    profile: BerechtigungsprofilRepository
    benutzer: BenutzerRepository
    audit: IdentityAuditRepository | None = None

    def execute(
        self, *, profil_id: str, benutzer_id: str, akteur_id: str | None = None
    ) -> None:
        if self.profile.get(profil_id) is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        if self.benutzer.get(benutzer_id) is None:
            raise BenutzerNichtGefunden(f"Benutzer {benutzer_id} nicht gefunden")
        self.profile.benutzer_zuordnen(profil_id=profil_id, benutzer_id=benutzer_id)
        if self.audit and akteur_id:
            self.audit.append(
                IdentityAuditEintrag.erzeugen(
                    akteur_benutzer_id=akteur_id,
                    aktion="profil_benutzer_zugeordnet",
                    ziel_benutzer_id=benutzer_id,
                    referenz_id=profil_id,
                )
            )


@dataclass
class ProfilBenutzerEntfernen:
    profile: BerechtigungsprofilRepository
    audit: IdentityAuditRepository | None = None

    def execute(
        self, *, profil_id: str, benutzer_id: str, akteur_id: str | None = None
    ) -> None:
        if self.profile.get(profil_id) is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        self.profile.benutzer_entfernen(profil_id=profil_id, benutzer_id=benutzer_id)
        if self.audit and akteur_id:
            self.audit.append(
                IdentityAuditEintrag.erzeugen(
                    akteur_benutzer_id=akteur_id,
                    aktion="profil_benutzer_entfernt",
                    ziel_benutzer_id=benutzer_id,
                    referenz_id=profil_id,
                )
            )
