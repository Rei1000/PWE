"""Application-Tests — Bibliothek CRUD und Automatisierung entfernen (Gate 8.2a)."""

import pytest

from adapters.persistence.in_memory import InMemoryBibliothekRepository, InMemoryKatalogRepository
from application.katalog.automatisierung_entfernen import AutomatisierungEntfernen
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externe_kommandos_listen import ExterneKommandosListen
from application.katalog.externes_kommando_aktualisieren import ExternesKommandoAktualisieren
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.externes_kommando_lesen import ExternesKommandoLesen
from application.katalog.externes_kommando_loeschen import ExternesKommandoLoeschen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.routine_anlegen import RoutineAnlegen
from application.katalog.routine_aktualisieren import RoutineAktualisieren
from application.katalog.routine_lesen import RoutineLesen
from application.katalog.routine_loeschen import RoutineLoeschen
from application.katalog.routine_zuweisen import RoutineProzedurSchrittZuweisen
from application.katalog.routinen_listen import RoutinenListen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.errors import (
    ExternesKommandoNichtGefunden,
    KommandoInVerwendung,
    RoutineInVerwendung,
    RoutineNichtGefunden,
)
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from helpers import registriere_standard_vorlagen


def _setup():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    registriere_standard_vorlagen(bibliothek, "vorlage-a", "v")
    return katalog, bibliothek


def _schritt() -> ProzedurSchrittEntwurf:
    return ProzedurSchrittEntwurf(
        schritt_id="schritt-a",
        vorlage_id="vorlage-a",
        ist_pflicht=True,
        reihenfolge=1,
    )


def test_externe_kommandos_listen():
    _, bibliothek = _setup()
    ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="A", kommandocode="A")
    ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="B", kommandocode="B")
    result = ExterneKommandosListen(bibliothek).execute()
    assert len(result) == 2
    assert {k.bezeichnung for k in result} == {"A", "B"}


def test_externes_kommando_lesen_und_aktualisieren():
    _, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="Alt", kommandocode="OLD")
    gelesen = ExternesKommandoLesen(bibliothek).execute(kommando.kommando_id)
    assert gelesen.kommandocode == "OLD"

    aktualisiert = ExternesKommandoAktualisieren(bibliothek).execute(
        kommando.kommando_id,
        bezeichnung="Neu",
        kommandocode="NEW",
    )
    assert aktualisiert.bezeichnung == "Neu"
    assert ExternesKommandoLesen(bibliothek).execute(kommando.kommando_id).kommandocode == "NEW"


def test_externes_kommando_lesen_nicht_gefunden():
    _, bibliothek = _setup()
    with pytest.raises(ExternesKommandoNichtGefunden):
        ExternesKommandoLesen(bibliothek).execute("fehlend")


def test_externes_kommando_loeschen_happy_path():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="X", kommandocode="X")
    ExternesKommandoLoeschen(katalog, bibliothek).execute(kommando.kommando_id)
    assert bibliothek.get_externes_kommando(kommando.kommando_id) is None


def test_externes_kommando_loeschen_in_entwurf_verwendet():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="X", kommandocode="X")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
        prozedur_schritte=(_schritt(),),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    with pytest.raises(KommandoInVerwendung):
        ExternesKommandoLoeschen(katalog, bibliothek).execute(kommando.kommando_id)


def test_externes_kommando_loeschen_in_routine_verwendet():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="X", kommandocode="X")
    RoutineAnlegen(bibliothek).execute(bezeichnung="R", kommando_ids=(kommando.kommando_id,))
    with pytest.raises(KommandoInVerwendung):
        ExternesKommandoLoeschen(katalog, bibliothek).execute(kommando.kommando_id)


def test_externes_kommando_loeschen_nach_veroeffentlichung_erlaubt():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="X", kommandocode="X")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
        prozedur_schritte=(_schritt(),),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)
    AutomatisierungEntfernen(katalog).execute(entwurf.produktdefinition_id, "schritt-a")
    ExternesKommandoLoeschen(katalog, bibliothek).execute(kommando.kommando_id)
    assert bibliothek.get_externes_kommando(kommando.kommando_id) is None


def test_routinen_listen_lesen_aktualisieren_loeschen():
    katalog, bibliothek = _setup()
    k1 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="K1", kommandocode="K1")
    k2 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="K2", kommandocode="K2")
    routine = RoutineAnlegen(bibliothek).execute(bezeichnung="R", kommando_ids=(k1.kommando_id,))
    assert len(RoutinenListen(bibliothek).execute()) == 1

    gelesen = RoutineLesen(bibliothek).execute(routine.routine_id)
    assert gelesen.bezeichnung == "R"

    aktualisiert = RoutineAktualisieren(bibliothek).execute(
        routine.routine_id,
        bezeichnung="R2",
        kommando_ids=(k2.kommando_id,),
    )
    assert aktualisiert.bezeichnung == "R2"
    assert aktualisiert.aktionen[0].kommando_id == k2.kommando_id

    RoutineLoeschen(katalog, bibliothek).execute(routine.routine_id)
    with pytest.raises(RoutineNichtGefunden):
        RoutineLesen(bibliothek).execute(routine.routine_id)


def test_routine_loeschen_in_entwurf_verwendet():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="K", kommandocode="K")
    routine = RoutineAnlegen(bibliothek).execute(bezeichnung="R", kommando_ids=(kommando.kommando_id,))
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
        prozedur_schritte=(_schritt(),),
    )
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        routine.routine_id,
    )
    with pytest.raises(RoutineInVerwendung):
        RoutineLoeschen(katalog, bibliothek).execute(routine.routine_id)


def test_automatisierung_entfernen():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="K", kommandocode="K")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
        prozedur_schritte=(_schritt(),),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    entwurf = AutomatisierungEntfernen(katalog).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
    )
    schritt = entwurf.prozedur_schritte[0]
    assert schritt.kommando_id is None
    assert schritt.routine_id is None
