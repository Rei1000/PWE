"""Use Cases — Benutzerverwaltung (Gate 8.1c1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from domain.identity.benutzer import Benutzer
from domain.identity.identity_audit import IdentityAuditEintrag
from domain.identity.letzter_administrator import assert_mutation_behaelt_aktiven_administrator
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.shared.errors import DomainError, InvariantViolation
from ports.benutzer_repository import BenutzerRepository
from ports.identity_audit_repository import IdentityAuditRepository
from ports.passwort_hasher import PasswortHasher
from ports.session_store import SessionStore


class BenutzerNichtGefunden(DomainError):
    pass


class LoginBereitsVergeben(DomainError):
    pass


def _audit(
    audit: IdentityAuditRepository,
    *,
    akteur_id: str,
    aktion: str,
    ziel: Benutzer,
    details: dict | None = None,
) -> None:
    audit.append(
        IdentityAuditEintrag.erzeugen(
            akteur_benutzer_id=akteur_id,
            aktion=aktion,
            ziel_benutzer_id=ziel.benutzer_id,
            details=details or {},
        )
    )


def _status_mutation(
    *,
    benutzer_repo: BenutzerRepository,
    sessions: SessionStore,
    audit: IdentityAuditRepository,
    akteur_id: str,
    benutzer_id: str,
    aktion: str,
    invalidate_sessions: bool,
    transform: Callable[[Benutzer], Benutzer],
) -> Benutzer:
    alle = benutzer_repo.list_all(for_update=True)
    existing = next((b for b in alle if b.benutzer_id == benutzer_id), None)
    if existing is None:
        raise BenutzerNichtGefunden(f"Benutzer {benutzer_id} nicht gefunden")
    vorher = existing.status.value
    geaendert = transform(existing)
    assert_mutation_behaelt_aktiven_administrator(
        alle_benutzer=alle, geaenderter=geaendert
    )
    benutzer_repo.save(geaendert)
    if invalidate_sessions:
        sessions.loeschen_alle_fuer_benutzer(benutzer_id)
    _audit(
        audit,
        akteur_id=akteur_id,
        aktion=aktion,
        ziel=geaendert,
        details={"vorher": {"status": vorher}, "nachher": {"status": geaendert.status.value}},
    )
    return geaendert


@dataclass
class BenutzerAnlegen:
    benutzer: BenutzerRepository
    hasher: PasswortHasher
    audit: IdentityAuditRepository

    def execute(
        self,
        *,
        akteur_id: str,
        login: str,
        anzeigename: str,
        passwort_klartext: str,
        rollen: set[Systemrolle] | frozenset[Systemrolle],
    ) -> Benutzer:
        if not passwort_klartext or not passwort_klartext.strip():
            raise InvariantViolation("Passwort darf nicht leer sein")
        if self.benutzer.get_by_login(login) is not None:
            raise LoginBereitsVergeben(f"Login bereits vergeben: {login.strip()}")
        neu = Benutzer.anlegen(
            login=login,
            anzeigename=anzeigename,
            passwort_hash=self.hasher.hash(passwort_klartext),
            rollen=frozenset(rollen),
            status=BenutzerStatus.NEU,
            passwortwechsel_erforderlich=True,
        )
        self.benutzer.save(neu)
        _audit(
            self.audit,
            akteur_id=akteur_id,
            aktion="benutzer_angelegt",
            ziel=neu,
            details={
                "login": neu.login,
                "status": neu.status.value,
                "rollen": sorted(r.value for r in neu.rollen),
            },
        )
        return neu


@dataclass
class BenutzerLesen:
    benutzer: BenutzerRepository

    def execute(self, benutzer_id: str) -> Benutzer:
        b = self.benutzer.get(benutzer_id)
        if b is None:
            raise BenutzerNichtGefunden(f"Benutzer {benutzer_id} nicht gefunden")
        return b


@dataclass
class BenutzerListen:
    benutzer: BenutzerRepository

    def execute(self) -> list[Benutzer]:
        return self.benutzer.list_all()


@dataclass
class BenutzerAktivieren:
    benutzer: BenutzerRepository
    sessions: SessionStore
    audit: IdentityAuditRepository

    def execute(self, *, akteur_id: str, benutzer_id: str) -> Benutzer:
        return _status_mutation(
            benutzer_repo=self.benutzer,
            sessions=self.sessions,
            audit=self.audit,
            akteur_id=akteur_id,
            benutzer_id=benutzer_id,
            aktion="benutzer_aktiviert",
            invalidate_sessions=False,
            transform=lambda b: b.aktivieren(),
        )


@dataclass
class BenutzerSperren:
    benutzer: BenutzerRepository
    sessions: SessionStore
    audit: IdentityAuditRepository

    def execute(self, *, akteur_id: str, benutzer_id: str) -> Benutzer:
        return _status_mutation(
            benutzer_repo=self.benutzer,
            sessions=self.sessions,
            audit=self.audit,
            akteur_id=akteur_id,
            benutzer_id=benutzer_id,
            aktion="benutzer_gesperrt",
            invalidate_sessions=True,
            transform=lambda b: b.sperren(),
        )


@dataclass
class BenutzerEntsperren:
    benutzer: BenutzerRepository
    sessions: SessionStore
    audit: IdentityAuditRepository

    def execute(self, *, akteur_id: str, benutzer_id: str) -> Benutzer:
        return _status_mutation(
            benutzer_repo=self.benutzer,
            sessions=self.sessions,
            audit=self.audit,
            akteur_id=akteur_id,
            benutzer_id=benutzer_id,
            aktion="benutzer_entsperrt",
            invalidate_sessions=False,
            transform=lambda b: b.entsperren(),
        )


@dataclass
class BenutzerArchivieren:
    benutzer: BenutzerRepository
    sessions: SessionStore
    audit: IdentityAuditRepository

    def execute(self, *, akteur_id: str, benutzer_id: str) -> Benutzer:
        return _status_mutation(
            benutzer_repo=self.benutzer,
            sessions=self.sessions,
            audit=self.audit,
            akteur_id=akteur_id,
            benutzer_id=benutzer_id,
            aktion="benutzer_archiviert",
            invalidate_sessions=True,
            transform=lambda b: b.archivieren(),
        )


@dataclass
class BenutzerWiederherstellen:
    benutzer: BenutzerRepository
    sessions: SessionStore
    audit: IdentityAuditRepository

    def execute(self, *, akteur_id: str, benutzer_id: str) -> Benutzer:
        return _status_mutation(
            benutzer_repo=self.benutzer,
            sessions=self.sessions,
            audit=self.audit,
            akteur_id=akteur_id,
            benutzer_id=benutzer_id,
            aktion="benutzer_wiederhergestellt",
            invalidate_sessions=False,
            transform=lambda b: b.wiederherstellen(),
        )


@dataclass
class BenutzerRollenSetzen:
    benutzer: BenutzerRepository
    audit: IdentityAuditRepository

    def execute(
        self,
        *,
        akteur_id: str,
        benutzer_id: str,
        rollen: set[Systemrolle] | frozenset[Systemrolle],
    ) -> Benutzer:
        alle = self.benutzer.list_all(for_update=True)
        existing = next((b for b in alle if b.benutzer_id == benutzer_id), None)
        if existing is None:
            raise BenutzerNichtGefunden(f"Benutzer {benutzer_id} nicht gefunden")
        if existing.status == BenutzerStatus.ARCHIVIERT:
            raise InvariantViolation("Rollen archivierter Benutzer können nicht geändert werden")
        vorher = sorted(r.value for r in existing.rollen)
        geaendert = existing.mit_rollen(rollen)
        assert_mutation_behaelt_aktiven_administrator(
            alle_benutzer=alle, geaenderter=geaendert
        )
        self.benutzer.save(geaendert)
        _audit(
            self.audit,
            akteur_id=akteur_id,
            aktion="rollen_geaendert",
            ziel=geaendert,
            details={
                "vorher": {"rollen": vorher},
                "nachher": {"rollen": sorted(r.value for r in geaendert.rollen)},
            },
        )
        return geaendert
