"""Test-Hilfe — Qualifikation für Prüflauf-Start (Gate 8.1b)."""

from __future__ import annotations

from adapters.persistence.in_memory_identity import (
    InMemoryBenutzerRepository,
    InMemoryBerechtigungsprofilRepository,
    InMemoryEinweisungsnachweisRepository,
)
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from domain.identity.benutzer import Benutzer, PasswortHash
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import Einweisungsnachweis
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.katalog.version import ProduktdefinitionsVersion


def qualify_benutzer_for_kodierung(
    deps,
    *,
    benutzer_id: str,
    produktkodierung: str,
    eingewiesen_durch: str = "admin",
):
    """Creates/updates profile covering PD of active version and valid einweisung.

    Idempotent: bestehende gültige Einweisung / passendes Profil werden wiederverwendet.
    """
    version = deps.katalog.get_aktive_version_fuer_kodierung(produktkodierung)
    if version is None:
        raise ValueError(f"Keine aktive Version für {produktkodierung}")

    vorhandene = deps.profile_repo.profile_fuer_benutzer(benutzer_id)
    profil = next(
        (p for p in vorhandene if version.produktdefinition_id in p.produktdefinition_ids),
        None,
    )
    if profil is None:
        profil = Berechtigungsprofil.anlegen(
            bezeichnung=f"Profil {produktkodierung}",
            produktdefinition_ids={version.produktdefinition_id},
        )
        deps.profile_repo.save(profil)
        deps.profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id=benutzer_id)

    einweisung = deps.einweisung_repo.get_gueltige(
        benutzer_id=benutzer_id, version_id=version.version_id
    )
    if einweisung is None:
        einweisung = Einweisungsnachweis.anlegen(
            benutzer_id=benutzer_id,
            version_id=version.version_id,
            eingewiesen_durch=eingewiesen_durch,
        )
        deps.einweisung_repo.save(einweisung)
    return profil, einweisung


def qualify_client_for_kodierung(client, produktkodierung: str):
    """Qualifiziert den Session-Benutzer der TestClient-App für die Produktkodierung."""
    me = client.get("/auth/me")
    assert me.status_code == 200, me.text
    benutzer_id = me.json()["benutzer_id"]

    deps = getattr(client.app.state, "deps", None)
    if deps is not None:
        return qualify_benutzer_for_kodierung(
            deps,
            benutzer_id=benutzer_id,
            produktkodierung=produktkodierung,
        )

    # PostgreSQL: Request-scoped Deps — eigene Session für Qualifikation committen
    from api.persistence import postgres_deps

    session = client.app.state.session_factory()
    try:
        deps = postgres_deps(session, client.app.state.datei_speicher)
        result = qualify_benutzer_for_kodierung(
            deps,
            benutzer_id=benutzer_id,
            produktkodierung=produktkodierung,
        )
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _aktive_versionen(katalog) -> list[ProduktdefinitionsVersion]:
    interne = getattr(katalog, "_aktive_versionen", None)
    if isinstance(interne, dict) and interne:
        return list(interne.values())
    return []


def _ensure_benutzer_qualified(
    *,
    benutzer_repo: InMemoryBenutzerRepository,
    profile_repo: InMemoryBerechtigungsprofilRepository,
    einweisung_repo: InMemoryEinweisungsnachweisRepository,
    katalog,
    benutzer_id: str,
    anzeigename: str,
    produktkodierung: str | None = None,
) -> None:
    if benutzer_repo.get(benutzer_id) is None:
        benutzer_repo.save(
            Benutzer.anlegen(
                login=benutzer_id,
                anzeigename=anzeigename,
                passwort_hash=PasswortHash("test-hash"),
                rollen=frozenset({Systemrolle.PRUEFER}),
                status=BenutzerStatus.AKTIV,
                benutzer_id=benutzer_id,
            )
        )

    versionen = _aktive_versionen(katalog)
    if not versionen and produktkodierung:
        v = katalog.get_aktive_version_fuer_kodierung(produktkodierung)
        if v is not None:
            versionen = [v]
    if not versionen:
        return

    pd_ids = {v.produktdefinition_id for v in versionen}
    vorhandene = profile_repo.profile_fuer_benutzer(benutzer_id)
    deckt_alle = any(pd_ids <= set(p.produktdefinition_ids) for p in vorhandene)
    if not deckt_alle:
        profil = Berechtigungsprofil.anlegen(
            bezeichnung=f"Test-Profil-{benutzer_id}",
            produktdefinition_ids=pd_ids,
        )
        profile_repo.save(profil)
        profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id=benutzer_id)

    for version in versionen:
        if (
            einweisung_repo.get_gueltige(
                benutzer_id=benutzer_id, version_id=version.version_id
            )
            is None
        ):
            einweisung_repo.save(
                Einweisungsnachweis.anlegen(
                    benutzer_id=benutzer_id,
                    version_id=version.version_id,
                    eingewiesen_durch="admin",
                )
            )


class _QualifiedPruefungStarten(PruefungStarten):
    """PruefungStarten, das den angefragten pruefer_id vor dem Start qualifiziert."""

    def __init__(
        self,
        katalog,
        prueflauf_repo,
        benutzer_repo,
        profile_repo,
        einweisung_repo,
        *,
        anzeigename: str = "P",
    ) -> None:
        super().__init__(katalog, prueflauf_repo, benutzer_repo, profile_repo, einweisung_repo)
        self._anzeigename = anzeigename

    def execute(
        self,
        *,
        produktkodierung: str,
        pruefobjekt_kennung: str,
        pruefer_id: str,
    ):
        _ensure_benutzer_qualified(
            benutzer_repo=self.benutzer_repo,  # type: ignore[arg-type]
            profile_repo=self.profile,  # type: ignore[arg-type]
            einweisung_repo=self.einweisungen,  # type: ignore[arg-type]
            katalog=self.katalog,
            benutzer_id=pruefer_id,
            anzeigename=self._anzeigename,
            produktkodierung=produktkodierung,
        )
        return super().execute(
            produktkodierung=produktkodierung,
            pruefobjekt_kennung=pruefobjekt_kennung,
            pruefer_id=pruefer_id,
        )


def make_pruefung_starten(
    katalog,
    prueflauf_repo,
    *,
    benutzer_id: str = "pruefer-1",
    anzeigename: str = "P",
) -> PruefungStarten:
    """Returns PruefungStarten with in-memory identity; creates qualified Benutzer.

    Introspektiert InMemoryKatalogRepository._aktive_versionen; bei execute() wird
    zusätzlich über get_aktive_version_fuer_kodierung qualifiziert (Postgres-Repos).
    """
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()

    _ensure_benutzer_qualified(
        benutzer_repo=benutzer_repo,
        profile_repo=profile_repo,
        einweisung_repo=einweisung_repo,
        katalog=katalog,
        benutzer_id=benutzer_id,
        anzeigename=anzeigename,
    )

    return _QualifiedPruefungStarten(
        katalog,
        prueflauf_repo,
        benutzer_repo,
        profile_repo,
        einweisung_repo,
        anzeigename=anzeigename,
    )
