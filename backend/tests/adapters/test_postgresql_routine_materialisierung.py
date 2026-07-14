"""PostgreSQL-Tests — Routine-Materialisierung (Gate 7.3d)."""

import json

import pytest

from adapters.persistence.postgresql.mapping import (
    entwurf_from_payload,
    entwurf_to_payload,
    version_from_payload,
    version_to_payload,
)
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.routine_anlegen import RoutineAnlegen
from application.katalog.routine_zuweisen import RoutineProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.errors import MaterialisierteAutomatisierungInkonsistent
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.routine import MaterialisierteRoutineHerkunft

pytestmark = pytest.mark.postgresql


def test_postgresql_entwurf_roundtrip_mit_routine_id(pg_repos):
    katalog, bibliothek, _, _ = pg_repos
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Reset",
        kommandocode="RST",
    )
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Reset-Routine",
        kommando_ids=(kommando.kommando_id,),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="7777777771",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        routine.routine_id,
    )
    gespeichert = katalog.get_entwurf(entwurf.produktdefinition_id)
    assert gespeichert is not None
    assert gespeichert.prozedur_schritte[0].routine_id == routine.routine_id

    restored = entwurf_from_payload(entwurf_to_payload(gespeichert))
    assert restored.prozedur_schritte[0].routine_id == routine.routine_id


def test_postgresql_version_roundtrip_materialisierte_routine(pg_repos, pg_session):
    katalog, bibliothek, _, _ = pg_repos
    k1 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="A", kommandocode="CMD1")
    k2 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="B", kommandocode="CMD2")
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Zweistufig",
        kommando_ids=(k1.kommando_id, k2.kommando_id),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="7777777772",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        routine.routine_id,
    )
    version = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    pg_session.commit()

    stored = katalog.get_version(version.version_id)
    assert stored is not None
    schritt = stored.schritt_by_id("schritt-a")
    assert schritt is not None
    mr = schritt.materialisierte_routine
    assert mr is not None
    assert mr.herkunft == MaterialisierteRoutineHerkunft.BIBLIOTHEK
    assert len(mr.aktionen) == 2

    restored = version_from_payload(version_to_payload(stored))
    assert restored == stored


def test_postgresql_legacy_externes_kommando_mapping(pg_repos, pg_session):
    katalog, _, _, _ = pg_repos
    legacy_payload = json.dumps(
        {
            "version_id": "ver-legacy",
            "produktdefinition_id": "pd-legacy",
            "produktkodierung": "7777777773",
            "prozedur_schritte": [
                {
                    "schritt_id": "schritt-a",
                    "vorlage_id": "vorlage-a",
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                    "externes_kommando": {
                        "kommando_id": "k1",
                        "bezeichnung": "Legacy",
                        "kommandocode": "LEG",
                    },
                }
            ],
            "sollbestueckung": [],
        }
    )
    version = version_from_payload(legacy_payload)
    schritt = version.schritt_by_id("schritt-a")
    assert schritt is not None
    assert schritt.externes_kommando is not None
    assert schritt.materialisierte_routine is None

    katalog.save_version(version, commit=True)
    pg_session.commit()

    stored = katalog.get_version("ver-legacy")
    assert stored is not None
    assert stored.schritt_by_id("schritt-a").externes_kommando.kommandocode == "LEG"


def test_postgresql_inkonsistente_automatisierung_wird_abgelehnt():
    inkonsistent = json.dumps(
        {
            "version_id": "ver-bad",
            "produktdefinition_id": "pd-bad",
            "produktkodierung": "7777777774",
            "prozedur_schritte": [
                {
                    "schritt_id": "schritt-a",
                    "vorlage_id": "vorlage-a",
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                    "materialisierte_routine": {
                        "herkunft": "einzelkommando",
                        "bezeichnung": "A",
                        "aktionen": [
                            {
                                "position": 1,
                                "kommando_id": "k1",
                                "bezeichnung": "A",
                                "kommandocode": "CMD1",
                            }
                        ],
                    },
                    "externes_kommando": {
                        "kommando_id": "k1",
                        "bezeichnung": "Abweichend",
                        "kommandocode": "CMD2",
                    },
                }
            ],
            "sollbestueckung": [],
        }
    )
    with pytest.raises(MaterialisierteAutomatisierungInkonsistent):
        version_from_payload(inkonsistent)


def test_postgresql_materialisierung_einzelkommando_und_routine(pg_repos, pg_session):
    katalog, bibliothek, _, _ = pg_repos
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Einzel",
        kommandocode="ONE",
    )
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Bibliothek",
        kommando_ids=(kommando.kommando_id,),
    )

    entwurf_kommando = EntwurfAnlegen(katalog).execute(
        produktkodierung="7777777775",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-k",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf_kommando.produktdefinition_id,
        "schritt-k",
        kommando.kommando_id,
    )
    version_k = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf_kommando.produktdefinition_id
    )

    entwurf_routine = EntwurfAnlegen(katalog).execute(
        produktkodierung="7777777776",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-r",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf_routine.produktdefinition_id,
        "schritt-r",
        routine.routine_id,
    )
    version_r = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf_routine.produktdefinition_id
    )
    pg_session.commit()

    sk = katalog.get_version(version_k.version_id).schritt_by_id("schritt-k")
    sr = katalog.get_version(version_r.version_id).schritt_by_id("schritt-r")
    assert sk.materialisierte_routine.herkunft == MaterialisierteRoutineHerkunft.EINZELKOMMANDO
    assert sk.externes_kommando.kommandocode == "ONE"
    assert sr.materialisierte_routine.herkunft == MaterialisierteRoutineHerkunft.BIBLIOTHEK
    assert sr.externes_kommando is None
