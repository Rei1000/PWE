"""Domain-Tests — zentrale Normalisierung materialisierter Routinen (Gate 7.3e)."""

import pytest

from domain.katalog.errors import MaterialisierteAutomatisierungInkonsistent
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.materialisierung import aufgeloeste_materialisierte_routine
from domain.katalog.routine import (
    MaterialisierteKommandoAktion,
    MaterialisierteRoutine,
    MaterialisierteRoutineHerkunft,
)
from domain.katalog.version import MaterialisierterProzedurSchritt
from domain.pruefausfuehrung.errors import KeineAutomatisierungAmSchritt


def _schritt(**kwargs) -> MaterialisierterProzedurSchritt:
    defaults = {
        "schritt_id": "s1",
        "vorlage_id": "v1",
        "ist_pflicht": True,
        "reihenfolge": 1,
    }
    defaults.update(kwargs)
    return MaterialisierterProzedurSchritt(**defaults)


def test_neues_modell_materialisierte_routine():
    mr = MaterialisierteRoutine(
        herkunft=MaterialisierteRoutineHerkunft.BIBLIOTHEK,
        routine_id="r1",
        bezeichnung="Test",
        aktionen=(
            MaterialisierteKommandoAktion(
                position=1,
                kommando_id="k1",
                bezeichnung="A",
                kommandocode="CMD1",
            ),
        ),
    )
    schritt = _schritt(materialisierte_routine=mr, externes_kommando=None)
    aufgeloest = aufgeloeste_materialisierte_routine(schritt)
    assert aufgeloest is mr


def test_legacy_nur_externes_kommando():
    ek = MaterialisiertesExternesKommando(
        kommando_id="k-legacy",
        bezeichnung="Legacy",
        kommandocode="LEG",
    )
    schritt = _schritt(externes_kommando=ek)
    aufgeloest = aufgeloeste_materialisierte_routine(schritt)
    assert aufgeloest.herkunft == MaterialisierteRoutineHerkunft.EINZELKOMMANDO
    assert aufgeloest.routine_id is None
    assert len(aufgeloest.aktionen) == 1
    assert aufgeloest.aktionen[0].position == 1
    assert aufgeloest.aktionen[0].kommando_id == "k-legacy"
    assert aufgeloest.aktionen[0].kommandocode == "LEG"


def test_inkonsistente_doppeldaten():
    mr = MaterialisierteRoutine(
        herkunft=MaterialisierteRoutineHerkunft.EINZELKOMMANDO,
        routine_id=None,
        bezeichnung="A",
        aktionen=(
            MaterialisierteKommandoAktion(
                position=1,
                kommando_id="k1",
                bezeichnung="A",
                kommandocode="A",
            ),
        ),
    )
    schritt = _schritt(
        materialisierte_routine=mr,
        externes_kommando=MaterialisiertesExternesKommando(
            kommando_id="k1",
            bezeichnung="Abweichend",
            kommandocode="DIFF",
        ),
    )
    with pytest.raises(MaterialisierteAutomatisierungInkonsistent):
        aufgeloeste_materialisierte_routine(schritt)


def test_schritt_ohne_automatisierung():
    schritt = _schritt()
    with pytest.raises(KeineAutomatisierungAmSchritt):
        aufgeloeste_materialisierte_routine(schritt)
