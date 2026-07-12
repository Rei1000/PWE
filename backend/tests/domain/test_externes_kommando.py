"""Domain-Tests — ExternesKommando (Katalog-Bibliothek)."""

import pytest

from domain.katalog.errors import ExternesKommandoNichtGefunden
from domain.katalog.externes_kommando import ExternesKommando, MaterialisiertesExternesKommando
from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from domain.shared.errors import InvariantViolation


def test_gueltiges_externes_kommando():
    kommando = ExternesKommando.anlegen(bezeichnung="Spannung messen", kommandocode="MEAS:V")
    assert kommando.kommando_id
    assert kommando.bezeichnung == "Spannung messen"
    assert kommando.kommandocode == "MEAS:V"


def test_leere_bezeichnung_ist_ungueltig():
    with pytest.raises(InvariantViolation, match="Bezeichnung"):
        ExternesKommando.anlegen(bezeichnung="  ", kommandocode="MEAS:V")


def test_leerer_kommandocode_ist_ungueltig():
    with pytest.raises(InvariantViolation, match="Kommandocode"):
        ExternesKommando.anlegen(bezeichnung="Spannung messen", kommandocode="")


def test_materialisierung_erzeugt_snapshot():
    kommando = ExternesKommando.anlegen(bezeichnung="Reset", kommandocode="RST")
    snapshot = MaterialisiertesExternesKommando.aus(kommando)
    assert snapshot.kommando_id == kommando.kommando_id
    assert snapshot.bezeichnung == "Reset"
    assert snapshot.kommandocode == "RST"


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


def test_bibliotheksaenderung_aendert_veroeffentlichte_version_nicht():
    kommando = ExternesKommando.anlegen(bezeichnung="Alt", kommandocode="OLD")
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
    assert schritt.externes_kommando is not None
    assert schritt.externes_kommando.bezeichnung == "Alt"
    assert schritt.externes_kommando.kommandocode == "OLD"

    geaendert = ExternesKommando(
        kommando_id=kommando.kommando_id,
        bezeichnung="Neu",
        kommandocode="NEW",
    )
    assert geaendert.kommando_id == kommando.kommando_id
    assert schritt.externes_kommando.bezeichnung == "Alt"
    assert schritt.externes_kommando.kommandocode == "OLD"
