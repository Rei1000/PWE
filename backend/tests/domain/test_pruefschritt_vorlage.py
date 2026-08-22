"""Domain-Tests — PrüfschrittVorlage (Gate 8.2b1, ADR-0020)."""

import pytest

from domain.katalog.errors import VorlageNichtGefunden
from domain.katalog.pruefschritt_vorlage import (
    MaterialisiertePruefschrittVorlage,
    PruefschrittVorlage,
)
from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from domain.shared.errors import InvariantViolation


def test_gueltige_pruefschritt_vorlage():
    vorlage = PruefschrittVorlage.anlegen(bezeichnung="Spannungsmessung", beschreibung="Manuell")
    assert vorlage.vorlage_id
    assert vorlage.bezeichnung == "Spannungsmessung"
    assert vorlage.beschreibung == "Manuell"


def test_leere_bezeichnung_ist_ungueltig():
    with pytest.raises(InvariantViolation, match="Bezeichnung"):
        PruefschrittVorlage.anlegen(bezeichnung="  ")


def test_snapshot_materialisierung():
    vorlage = PruefschrittVorlage.anlegen(bezeichnung="A", beschreibung="B")
    snapshot = MaterialisiertePruefschrittVorlage.aus(vorlage)
    assert snapshot.vorlage_id == vorlage.vorlage_id
    assert snapshot.bezeichnung == "A"
    assert snapshot.beschreibung == "B"


def test_veroeffentlichen_materialisiert_vorlage_snapshot():
    vorlage = PruefschrittVorlage(vorlage_id="v1", bezeichnung="Alt", beschreibung=None)
    entwurf = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ],
    )
    version = entwurf.veroeffentlichen(vorlagen={"v1": vorlage})
    schritt = version.schritt_by_id("s1")
    assert schritt is not None
    assert schritt.materialisierte_vorlage is not None
    assert schritt.materialisierte_vorlage.bezeichnung == "Alt"

    geaendert = vorlage.aktualisieren(bezeichnung="Neu")
    assert schritt.materialisierte_vorlage.bezeichnung == "Alt"
    assert geaendert.bezeichnung == "Neu"


def test_altversion_ohne_snapshot_bleibt_gueltig():
    from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion

    version = ProduktdefinitionsVersion(
        version_id="ver-legacy",
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=(
            MaterialisierterProzedurSchritt(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                materialisierte_vorlage=None,
            ),
        ),
    )
    schritt = version.schritt_by_id("s1")
    assert schritt is not None
    assert schritt.vorlage_id == "v1"
    assert schritt.materialisierte_vorlage is None


def test_unbekannte_vorlage_beim_veroeffentlichen():
    entwurf = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="fehlend",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ],
    )
    with pytest.raises(VorlageNichtGefunden):
        entwurf.veroeffentlichen(vorlagen={})
