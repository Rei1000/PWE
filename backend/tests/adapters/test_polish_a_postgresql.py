"""PostgreSQL Repository-Integration — V1 Operational Polish A."""

from __future__ import annotations

import uuid

import pytest

from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.startbare_pruefungen_listen import StartbarePruefungenListen
from domain.identity.benutzer import Benutzer, PasswortHash
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import Einweisungsnachweis
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from helpers import registriere_standard_vorlagen
from adapters.persistence.postgresql.identity_repository import PostgresBenutzerRepository
from adapters.persistence.postgresql.qualification_repository import (
    PostgresBerechtigungsprofilRepository,
    PostgresEinweisungsnachweisRepository,
)

pytestmark = pytest.mark.postgresql


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


def test_postgresql_aktive_produkte_nach_publish(pg_repos, pg_session):
    katalog, bibliothek, _, _ = pg_repos
    registriere_standard_vorlagen(bibliothek, "vorlage-a")
    kodierung = _unique_kodierung()
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung=kodierung,
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    v1 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    v2 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    pg_session.commit()

    aktiv = katalog.list_aktive_versionen()
    codes = {v.produktkodierung for v in aktiv}
    assert kodierung in codes
    match = next(v for v in aktiv if v.produktkodierung == kodierung)
    assert match.version_id == v2.version_id
    assert katalog.get_version(v1.version_id) is not None


def test_postgresql_profil_ids_und_startbare(pg_repos, pg_session):
    katalog, bibliothek, _, _ = pg_repos
    benutzer_repo = PostgresBenutzerRepository(pg_session)
    profile_repo = PostgresBerechtigungsprofilRepository(pg_session)
    einweisung_repo = PostgresEinweisungsnachweisRepository(pg_session)
    registriere_standard_vorlagen(bibliothek, "vorlage-a")

    pruefer = Benutzer.anlegen(
        login=f"pruefer-{uuid.uuid4().hex[:8]}",
        anzeigename="Prüfer PG",
        passwort_hash=PasswortHash("hash"),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
    )
    benutzer_repo.save(pruefer)

    kodierung = _unique_kodierung()
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung=kodierung,
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    version = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )

    profil = Berechtigungsprofil.anlegen(
        bezeichnung="PG-Profil",
        produktdefinition_ids={entwurf.produktdefinition_id},
    )
    profile_repo.save(profil)
    profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id=pruefer.benutzer_id)
    einweisung_repo.save(
        Einweisungsnachweis.anlegen(
            benutzer_id=pruefer.benutzer_id,
            version_id=version.version_id,
            eingewiesen_durch="admin",
        )
    )
    pg_session.commit()

    assert profile_repo.profil_ids_fuer_benutzer(pruefer.benutzer_id) == frozenset(
        {profil.profil_id}
    )

    profile_repo.save(profil.deaktivieren())
    pg_session.commit()
    assert profile_repo.profil_ids_fuer_benutzer(pruefer.benutzer_id) == frozenset(
        {profil.profil_id}
    )

    listen = StartbarePruefungenListen(
        katalog, benutzer_repo, profile_repo, einweisung_repo
    )
    assert kodierung not in {r.produktkodierung for r in listen.execute(benutzer_id=pruefer.benutzer_id)}

    profile_repo.save(profil.aktivieren())
    pg_session.commit()
    result = listen.execute(benutzer_id=pruefer.benutzer_id)
    assert [r.produktkodierung for r in result if r.produktkodierung == kodierung] == [kodierung]
