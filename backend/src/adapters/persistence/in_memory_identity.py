"""In-Memory Identity-Adapter (Tests / Dev ohne DB)."""

from __future__ import annotations

from datetime import datetime

from domain.identity.benutzer import Benutzer
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import EinweisungBereitsGueltig, Einweisungsnachweis
from domain.identity.typen import EinweisungsStatus
from ports.session_store import SessionDaten


class InMemoryBenutzerRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, Benutzer] = {}
        self._by_login: dict[str, str] = {}

    def save(self, benutzer: Benutzer) -> None:
        self._by_id[benutzer.benutzer_id] = benutzer
        self._by_login[benutzer.login.lower()] = benutzer.benutzer_id

    def get(self, benutzer_id: str) -> Benutzer | None:
        return self._by_id.get(benutzer_id)

    def get_by_login(self, login: str) -> Benutzer | None:
        bid = self._by_login.get(login.strip().lower())
        if bid is None:
            return None
        return self._by_id.get(bid)


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionDaten] = {}

    def speichern(self, session: SessionDaten) -> None:
        self._sessions[session.session_id] = session

    def laden(self, session_id: str) -> SessionDaten | None:
        return self._sessions.get(session_id)

    def aktualisieren_zuletzt_gesehen(self, session_id: str, zeitpunkt: datetime) -> None:
        alt = self._sessions.get(session_id)
        if alt is None:
            return
        self._sessions[session_id] = SessionDaten(
            session_id=alt.session_id,
            benutzer_id=alt.benutzer_id,
            csrf_token=alt.csrf_token,
            erzeugt_am=alt.erzeugt_am,
            zuletzt_gesehen_am=zeitpunkt,
        )

    def loeschen(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def loeschen_alle_fuer_benutzer(self, benutzer_id: str) -> None:
        for sid, s in list(self._sessions.items()):
            if s.benutzer_id == benutzer_id:
                del self._sessions[sid]


class InMemoryBerechtigungsprofilRepository:
    def __init__(self) -> None:
        self._profile: dict[str, Berechtigungsprofil] = {}
        self._benutzer_profile: dict[str, set[str]] = {}  # benutzer_id -> profil_ids

    def save(self, profil: Berechtigungsprofil) -> None:
        self._profile[profil.profil_id] = profil

    def get(self, profil_id: str) -> Berechtigungsprofil | None:
        return self._profile.get(profil_id)

    def list_all(self) -> list[Berechtigungsprofil]:
        return list(self._profile.values())

    def delete(self, profil_id: str) -> None:
        self._profile.pop(profil_id, None)
        for bid, pids in list(self._benutzer_profile.items()):
            pids.discard(profil_id)
            if not pids:
                del self._benutzer_profile[bid]

    def profil_ids_fuer_benutzer(self, benutzer_id: str) -> frozenset[str]:
        return frozenset(self._benutzer_profile.get(benutzer_id, ()))

    def benutzer_zuordnen(self, *, profil_id: str, benutzer_id: str) -> None:
        self._benutzer_profile.setdefault(benutzer_id, set()).add(profil_id)

    def benutzer_entfernen(self, *, profil_id: str, benutzer_id: str) -> None:
        pids = self._benutzer_profile.get(benutzer_id)
        if pids is None:
            return
        pids.discard(profil_id)
        if not pids:
            del self._benutzer_profile[benutzer_id]

    def profile_fuer_benutzer(self, benutzer_id: str) -> list[Berechtigungsprofil]:
        return [
            self._profile[pid]
            for pid in self._benutzer_profile.get(benutzer_id, ())
            if pid in self._profile
        ]


class InMemoryEinweisungsnachweisRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, Einweisungsnachweis] = {}

    def save(self, einweisung: Einweisungsnachweis) -> None:
        if einweisung.status == EinweisungsStatus.GUELTIG:
            for existing in self._by_id.values():
                if (
                    existing.einweisung_id != einweisung.einweisung_id
                    and existing.benutzer_id == einweisung.benutzer_id
                    and existing.version_id == einweisung.version_id
                    and existing.status == EinweisungsStatus.GUELTIG
                ):
                    raise EinweisungBereitsGueltig(
                        "Es existiert bereits eine gültige Einweisung für Benutzer und Version"
                    )
        self._by_id[einweisung.einweisung_id] = einweisung

    def get(self, einweisung_id: str) -> Einweisungsnachweis | None:
        return self._by_id.get(einweisung_id)

    def get_gueltige(
        self, *, benutzer_id: str, version_id: str
    ) -> Einweisungsnachweis | None:
        """Status GUELTIG für (Benutzer, Version); abgelaufen nach Datum → None."""
        for e in self._by_id.values():
            if (
                e.benutzer_id == benutzer_id
                and e.version_id == version_id
                and e.status == EinweisungsStatus.GUELTIG
            ):
                if e.ist_gueltig():
                    return e
                return None
        return None

    def list_gueltige_fuer_version(self, version_id: str) -> list[Einweisungsnachweis]:
        return [
            e
            for e in self._by_id.values()
            if e.version_id == version_id
            and e.status == EinweisungsStatus.GUELTIG
            and e.ist_gueltig()
        ]

    def list_fuer_benutzer_version(
        self, *, benutzer_id: str, version_id: str
    ) -> list[Einweisungsnachweis]:
        return [
            e
            for e in self._by_id.values()
            if e.benutzer_id == benutzer_id and e.version_id == version_id
        ]
