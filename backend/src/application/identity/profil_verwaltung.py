"""Use Cases — Berechtigungsprofil (Gate 8.1b)."""

from __future__ import annotations

from dataclasses import dataclass

from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.shared.errors import DomainError
from ports.benutzer_repository import BenutzerRepository
from ports.berechtigungsprofil_repository import BerechtigungsprofilRepository


class ProfilNichtGefunden(DomainError):
    pass


class BenutzerNichtGefunden(DomainError):
    pass


@dataclass
class ProfilAnlegen:
    profile: BerechtigungsprofilRepository

    def execute(
        self,
        *,
        bezeichnung: str,
        beschreibung: str | None = None,
        produktdefinition_ids: list[str] | None = None,
    ) -> Berechtigungsprofil:
        profil = Berechtigungsprofil.anlegen(
            bezeichnung=bezeichnung,
            beschreibung=beschreibung,
            produktdefinition_ids=set(produktdefinition_ids or ()),
        )
        self.profile.save(profil)
        return profil


@dataclass
class ProfilAktualisieren:
    profile: BerechtigungsprofilRepository

    def execute(
        self,
        *,
        profil_id: str,
        bezeichnung: str,
        beschreibung: str | None = None,
        produktdefinition_ids: list[str] | None = None,
    ) -> Berechtigungsprofil:
        existing = self.profile.get(profil_id)
        if existing is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        updated = existing.mit_bezeichnung(bezeichnung, beschreibung)
        if produktdefinition_ids is not None:
            updated = updated.mit_produktdefinitionen(set(produktdefinition_ids))
        self.profile.save(updated)
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
class ProfilBenutzerZuordnen:
    profile: BerechtigungsprofilRepository
    benutzer: BenutzerRepository

    def execute(self, *, profil_id: str, benutzer_id: str) -> None:
        if self.profile.get(profil_id) is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        if self.benutzer.get(benutzer_id) is None:
            raise BenutzerNichtGefunden(f"Benutzer {benutzer_id} nicht gefunden")
        self.profile.benutzer_zuordnen(profil_id=profil_id, benutzer_id=benutzer_id)


@dataclass
class ProfilBenutzerEntfernen:
    profile: BerechtigungsprofilRepository

    def execute(self, *, profil_id: str, benutzer_id: str) -> None:
        if self.profile.get(profil_id) is None:
            raise ProfilNichtGefunden(f"Profil {profil_id} nicht gefunden")
        self.profile.benutzer_entfernen(profil_id=profil_id, benutzer_id=benutzer_id)
