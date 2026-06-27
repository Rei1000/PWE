"""Domain-Tests — Produktdefinition (Entwurf) und Veröffentlichen."""

import pytest

from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from domain.shared.errors import InvariantViolation


def _schritt_a(**kwargs) -> ProzedurSchrittEntwurf:
    defaults = dict(
        schritt_id="schritt-a",
        vorlage_id="vorlage-a",
        ist_pflicht=True,
        reihenfolge=1,
    )
    defaults.update(kwargs)
    return ProzedurSchrittEntwurf(**defaults)


def test_veroeffentlichen_materialisiert_sollvorgaben():
    entwurf = Produktdefinition.anlegen(produktkodierung="1234567890")
    entwurf.basisprodukt_sollvorgaben = {"spannung": {"min": 200, "max": 250}}
    entwurf.kundenprofil_sollvorgaben = {"spannung": {"min": 220, "max": 240}}
    entwurf.prozedur_schritte = [
        _schritt_a(sollvorgaben={"spannung": {"min": 225, "max": 235}}),
    ]
    entwurf.sollbestueckung = ("mainboard",)

    version = entwurf.veroeffentlichen()

    assert version.produktkodierung == "1234567890"
    assert version.produktdefinition_id == entwurf.produktdefinition_id
    assert entwurf.aktive_version_id == version.version_id
    assert version.sollbestueckung == ("mainboard",)
    schritt = version.schritt_by_id("schritt-a")
    assert schritt is not None
    assert schritt.sollvorgaben["spannung"] == {"min": 225, "max": 235}


def test_veroeffentlichen_ohne_schritte_verboten():
    entwurf = Produktdefinition.anlegen(produktkodierung="1234567890")

    with pytest.raises(InvariantViolation):
        entwurf.veroeffentlichen()


def test_neue_version_ersetzt_aktive_referenz_im_entwurf():
    entwurf = Produktdefinition.anlegen(produktkodierung="1234567890")
    entwurf.prozedur_schritte = [_schritt_a()]

    v1 = entwurf.veroeffentlichen()
    v2 = entwurf.veroeffentlichen()

    assert v1.version_id != v2.version_id
    assert entwurf.aktive_version_id == v2.version_id
