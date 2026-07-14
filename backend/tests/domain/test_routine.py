"""Domain-Tests — Routine (Katalog-Bibliothek)."""

import pytest

from domain.katalog.errors import (
    AutomatisierungDoppeltZugewiesen,
    ExternesKommandoNichtGefunden,
    KommandoInRoutineNichtGefunden,
    LeereRoutine,
    RoutineNichtGefunden,
    UngueltigeAktionsreihenfolge,
)
from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from domain.katalog.routine import (
    MaterialisierteRoutine,
    MaterialisierteRoutineHerkunft,
    Routine,
    RoutineAktion,
    RoutineAktionsart,
)
from domain.shared.errors import InvariantViolation


def _kommando(bezeichnung: str = "Test", code: str = "CMD") -> ExternesKommando:
    return ExternesKommando.anlegen(bezeichnung=bezeichnung, kommandocode=code)


def _aktion(kommando_id: str, position: int = 1) -> RoutineAktion:
    return RoutineAktion(
        aktionsart=RoutineAktionsart.EXTERNES_KOMMANDO_AUSFUEHREN,
        kommando_id=kommando_id,
        position=position,
    )


def test_gueltige_routine_mit_einer_kommando_aktion():
    kommando = _kommando()
    routine = Routine.anlegen(bezeichnung="Messroutine", aktionen=(_aktion(kommando.kommando_id),))
    assert routine.routine_id
    assert routine.bezeichnung == "Messroutine"
    assert len(routine.aktionen) == 1


def test_routine_ohne_aktionen_wird_abgelehnt():
    with pytest.raises(LeereRoutine):
        Routine.anlegen(bezeichnung="Leer", aktionen=())


def test_leere_bezeichnung_ist_ungueltig():
    kommando = _kommando()
    with pytest.raises(InvariantViolation, match="Bezeichnung"):
        Routine.anlegen(bezeichnung="  ", aktionen=(_aktion(kommando.kommando_id),))


def test_geordnete_aktionen():
    k1, k2 = _kommando("A", "A"), _kommando("B", "B")
    routine = Routine.anlegen(
        bezeichnung="Zwei Schritte",
        aktionen=(
            _aktion(k1.kommando_id, 1),
            _aktion(k2.kommando_id, 2),
        ),
    )
    assert [a.position for a in routine.aktionen] == [1, 2]


def test_doppelte_aktionsposition_wird_abgelehnt():
    kommando = _kommando()
    with pytest.raises(UngueltigeAktionsreihenfolge, match="eindeutig"):
        Routine.anlegen(
            bezeichnung="Duplikat",
            aktionen=(
                _aktion(kommando.kommando_id, 1),
                _aktion(kommando.kommando_id, 1),
            ),
        )


def test_luecke_in_aktionsposition_wird_abgelehnt():
    k1, k2 = _kommando("A", "A"), _kommando("B", "B")
    with pytest.raises(UngueltigeAktionsreihenfolge, match="fortlaufend"):
        Routine.anlegen(
            bezeichnung="Lücke",
            aktionen=(
                _aktion(k1.kommando_id, 1),
                _aktion(k2.kommando_id, 3),
            ),
        )


def test_entwurfsregel_kommando_xor_routine():
    schritt = ProzedurSchrittEntwurf(
        schritt_id="s1",
        vorlage_id="v1",
        ist_pflicht=True,
        reihenfolge=1,
        kommando_id="k1",
        routine_id="r1",
    )
    with pytest.raises(AutomatisierungDoppeltZugewiesen):
        schritt.validiere_automatisierung()


def test_manueller_schritt_ohne_automatisierung_erlaubt():
    schritt = ProzedurSchrittEntwurf(
        schritt_id="s1",
        vorlage_id="v1",
        ist_pflicht=True,
        reihenfolge=1,
    )
    schritt.validiere_automatisierung()


def test_direkte_kommando_zuweisung_materialisiert_ein_aktions_routine():
    kommando = _kommando(bezeichnung="Reset", code="RST")
    entwurf = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                kommando_id=kommando.kommando_id,
            ),
        ],
    )
    version = entwurf.veroeffentlichen(externe_kommandos={kommando.kommando_id: kommando})
    schritt = version.schritt_by_id("s1")
    assert schritt is not None
    mr = schritt.materialisierte_routine
    assert mr is not None
    assert mr.herkunft == MaterialisierteRoutineHerkunft.EINZELKOMMANDO
    assert mr.routine_id is None
    assert len(mr.aktionen) == 1
    assert mr.aktionen[0].kommandocode == "RST"
    assert schritt.externes_kommando is not None
    assert schritt.externes_kommando.kommandocode == "RST"


def test_bibliotheksroutine_wird_vollstaendig_materialisiert():
    k1, k2 = _kommando("A", "CMD1"), _kommando("B", "CMD2")
    routine = Routine.anlegen(
        bezeichnung="Zweistufig",
        aktionen=(
            _aktion(k1.kommando_id, 1),
            _aktion(k2.kommando_id, 2),
        ),
    )
    entwurf = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                routine_id=routine.routine_id,
            ),
        ],
    )
    version = entwurf.veroeffentlichen(
        externe_kommandos={
            k1.kommando_id: k1,
            k2.kommando_id: k2,
        },
        routinen={routine.routine_id: routine},
    )
    schritt = version.schritt_by_id("s1")
    assert schritt is not None
    mr = schritt.materialisierte_routine
    assert mr is not None
    assert mr.herkunft == MaterialisierteRoutineHerkunft.BIBLIOTHEK
    assert mr.routine_id == routine.routine_id
    assert len(mr.aktionen) == 2
    assert mr.aktionen[0].kommandocode == "CMD1"
    assert mr.aktionen[1].kommandocode == "CMD2"
    assert schritt.externes_kommando is None


def test_unbekannte_routine_schlaegt_fachlich_fehl():
    entwurf = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                routine_id="unbekannt",
            ),
        ],
    )
    with pytest.raises(RoutineNichtGefunden):
        entwurf.veroeffentlichen(routinen={})


def test_unbekanntes_kommando_in_routine_schlaegt_fachlich_fehl():
    kommando = _kommando()
    routine = Routine.anlegen(
        bezeichnung="Mit fehlendem Kommando",
        aktionen=(_aktion("fehlend", 1),),
    )
    entwurf = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                routine_id=routine.routine_id,
            ),
        ],
    )
    with pytest.raises(KommandoInRoutineNichtGefunden):
        entwurf.veroeffentlichen(
            externe_kommandos={kommando.kommando_id: kommando},
            routinen={routine.routine_id: routine},
        )


def test_bibliotheksaenderung_aendert_veroeffentlichte_version_nicht():
    kommando = _kommando(bezeichnung="Alt", code="OLD")
    routine = Routine.anlegen(
        bezeichnung="Alt-Routine",
        aktionen=(_aktion(kommando.kommando_id),),
    )
    entwurf = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                routine_id=routine.routine_id,
            ),
        ],
    )
    version = entwurf.veroeffentlichen(
        externe_kommandos={kommando.kommando_id: kommando},
        routinen={routine.routine_id: routine},
    )

    geaendertes_kommando = ExternesKommando(
        kommando_id=kommando.kommando_id,
        bezeichnung="Neu",
        kommandocode="NEW",
    )
    geaenderte_routine = Routine(
        routine_id=routine.routine_id,
        bezeichnung="Neu-Routine",
        aktionen=(_aktion(kommando.kommando_id),),
    )

    schritt = version.schritt_by_id("s1")
    assert schritt is not None
    mr = schritt.materialisierte_routine
    assert mr is not None
    assert mr.bezeichnung == "Alt-Routine"
    assert mr.aktionen[0].kommandocode == "OLD"
    assert geaendertes_kommando.kommandocode == "NEW"
    assert geaenderte_routine.bezeichnung == "Neu-Routine"


def test_veroeffentlichen_mit_unbekannter_kommando_id_schlaegt_fehl():
    entwurf = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                kommando_id="unbekannt",
            ),
        ],
    )
    with pytest.raises(ExternesKommandoNichtGefunden):
        entwurf.veroeffentlichen(externe_kommandos={})


def test_materialisierte_routine_aus_einzelkommando_hat_keine_routine_id():
    kommando = _kommando()
    mr = MaterialisierteRoutine.aus_einzelkommando(kommando=kommando)
    assert mr.routine_id is None
    assert mr.herkunft == MaterialisierteRoutineHerkunft.EINZELKOMMANDO
