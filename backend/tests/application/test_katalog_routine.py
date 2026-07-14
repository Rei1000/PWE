"""Application-Tests — Katalog Routine."""

import pytest

from adapters.persistence.in_memory import InMemoryBibliothekRepository, InMemoryKatalogRepository
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.routine_anlegen import RoutineAnlegen
from application.katalog.routine_zuweisen import RoutineProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.errors import (
    AutomatisierungDoppeltZugewiesen,
    ExternesKommandoNichtGefunden,
    RoutineNichtGefunden,
)
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.routine import MaterialisierteRoutineHerkunft


def _setup():
    return InMemoryKatalogRepository(), InMemoryBibliothekRepository()


def test_routine_anlegen():
    _, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Messung",
        kommandocode="MEAS",
    )
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Messroutine",
        kommando_ids=(kommando.kommando_id,),
    )
    gespeichert = bibliothek.get_routine(routine.routine_id)
    assert gespeichert == routine


def test_routine_anlegen_mit_unbekanntem_kommando():
    _, bibliothek = _setup()
    with pytest.raises(ExternesKommandoNichtGefunden):
        RoutineAnlegen(bibliothek).execute(
            bezeichnung="Leer",
            kommando_ids=("fehlend",),
        )


def test_routine_einem_schritt_zuweisen():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Reset",
        kommandocode="RST",
    )
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Reset-Routine",
        kommando_ids=(kommando.kommando_id,),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
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
    schritt = gespeichert.prozedur_schritte[0]
    assert schritt.routine_id == routine.routine_id
    assert schritt.kommando_id is None


def test_routine_zuweisen_bei_vorhandenem_kommando_schlaegt_fehl():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Reset",
        kommandocode="RST",
    )
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Reset-Routine",
        kommando_ids=(kommando.kommando_id,),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="2222222222",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    with pytest.raises(AutomatisierungDoppeltZugewiesen):
        RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
            entwurf.produktdefinition_id,
            "schritt-a",
            routine.routine_id,
        )


def test_wechsel_kommando_zu_routine_erfordert_zwei_schritte():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Reset",
        kommandocode="RST",
    )
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Reset-Routine",
        kommando_ids=(kommando.kommando_id,),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="2222222222",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        None,
    )
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        routine.routine_id,
    )
    gespeichert = katalog.get_entwurf(entwurf.produktdefinition_id)
    assert gespeichert is not None
    schritt = gespeichert.prozedur_schritte[0]
    assert schritt.routine_id == routine.routine_id
    assert schritt.kommando_id is None


def test_kommando_zuweisen_bei_vorhandener_routine_schlaegt_fehl():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Reset",
        kommandocode="RST",
    )
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Reset-Routine",
        kommando_ids=(kommando.kommando_id,),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="3333333333",
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
    with pytest.raises(AutomatisierungDoppeltZugewiesen):
        KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
            entwurf.produktdefinition_id,
            "schritt-a",
            kommando.kommando_id,
        )


def test_wechsel_routine_zu_kommando_erfordert_zwei_schritte():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Reset",
        kommandocode="RST",
    )
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Reset-Routine",
        kommando_ids=(kommando.kommando_id,),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="3333333333",
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
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        None,
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    gespeichert = katalog.get_entwurf(entwurf.produktdefinition_id)
    assert gespeichert is not None
    schritt = gespeichert.prozedur_schritte[0]
    assert schritt.kommando_id == kommando.kommando_id
    assert schritt.routine_id is None


def test_routine_zuweisen_unbekannte_routine():
    katalog, bibliothek = _setup()
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="4444444444",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    with pytest.raises(RoutineNichtGefunden):
        RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
            entwurf.produktdefinition_id,
            "schritt-a",
            "fehlend",
        )


def test_veroeffentlichen_mit_bibliotheksroutine():
    katalog, bibliothek = _setup()
    k1 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="A", kommandocode="CMD1")
    k2 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="B", kommandocode="CMD2")
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Zweistufig",
        kommando_ids=(k1.kommando_id, k2.kommando_id),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="5555555555",
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
    schritt = version.schritt_by_id("schritt-a")
    assert schritt is not None
    mr = schritt.materialisierte_routine
    assert mr is not None
    assert mr.herkunft == MaterialisierteRoutineHerkunft.BIBLIOTHEK
    assert mr.routine_id == routine.routine_id
    assert len(mr.aktionen) == 2


def test_einzelkommando_pfad_bleibt_funktionsfaehig():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Reset",
        kommandocode="RST",
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="6666666666",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    version = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    schritt = version.schritt_by_id("schritt-a")
    assert schritt is not None
    assert schritt.externes_kommando is not None
    assert schritt.externes_kommando.kommandocode == "RST"
    mr = schritt.materialisierte_routine
    assert mr is not None
    assert mr.herkunft == MaterialisierteRoutineHerkunft.EINZELKOMMANDO
    assert mr.routine_id is None


def test_entwurf_mit_doppelter_zuweisung_wird_bei_veroeffentlichen_abgelehnt():
    katalog, bibliothek = _setup()
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="7777777777",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                kommando_id="k1",
                routine_id="r1",
            ),
        ),
    )
    with pytest.raises(AutomatisierungDoppeltZugewiesen):
        ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
            entwurf.produktdefinition_id
        )
