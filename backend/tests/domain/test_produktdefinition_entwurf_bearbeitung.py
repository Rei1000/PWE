"""Domain-Tests — Entwurfs-Schrittbearbeitung (Gate 8.2b2)."""

import pytest

from domain.katalog.errors import (
    ProzedurSchrittNichtGefunden,
    SchrittIdBereitsVorhanden,
    UngueltigeSchrittReihenfolge,
)
from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from domain.shared.errors import InvariantViolation
from helpers import vorlage_map


def _entwurf_mit_schritten(*schritte: ProzedurSchrittEntwurf) -> Produktdefinition:
    entwurf = Produktdefinition.anlegen(produktkodierung="1234567890")
    entwurf.prozedur_schritte = list(schritte)
    return entwurf


def _schritt(schritt_id: str, reihenfolge: int, **kwargs) -> ProzedurSchrittEntwurf:
    defaults = dict(
        vorlage_id="vorlage-a",
        ist_pflicht=True,
        reihenfolge=reihenfolge,
    )
    defaults.update(kwargs)
    return ProzedurSchrittEntwurf(schritt_id=schritt_id, **defaults)


def test_schritt_hinzufuegen_am_ende():
    entwurf = _entwurf_mit_schritten(_schritt("s1", 1))
    neu = entwurf.schritt_hinzufuegen(
        ProzedurSchrittEntwurf(
            schritt_id="s2",
            vorlage_id="vorlage-b",
            ist_pflicht=False,
            reihenfolge=99,
        )
    )
    assert neu.reihenfolge == 2
    assert [s.schritt_id for s in entwurf.prozedur_schritte] == ["s1", "s2"]


def test_schritt_hinzufuegen_doppelte_id_abgewiesen():
    entwurf = _entwurf_mit_schritten(_schritt("s1", 1))
    with pytest.raises(SchrittIdBereitsVorhanden):
        entwurf.schritt_hinzufuegen(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=2,
            )
        )


def test_schritt_hinzufuegen_leere_id_abgewiesen():
    entwurf = Produktdefinition.anlegen(produktkodierung="1234567890")
    with pytest.raises(InvariantViolation):
        entwurf.schritt_hinzufuegen(
            ProzedurSchrittEntwurf(
                schritt_id="  ",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            )
        )


def test_schritt_aktualisieren_erhaelt_automatisierung():
    entwurf = _entwurf_mit_schritten(
        _schritt("s1", 1, kommando_id="k1", sollvorgaben={"a": 1})
    )
    aktualisiert = entwurf.schritt_aktualisieren(
        "s1",
        vorlage_id="vorlage-b",
        ist_pflicht=False,
        sollvorgaben={"b": 2},
    )
    assert aktualisiert.kommando_id == "k1"
    assert aktualisiert.routine_id is None
    assert aktualisiert.vorlage_id == "vorlage-b"
    assert aktualisiert.ist_pflicht is False
    assert aktualisiert.sollvorgaben == {"b": 2}
    assert aktualisiert.reihenfolge == 1


def test_schritt_entfernen_normalisiert_reihenfolge():
    entwurf = _entwurf_mit_schritten(
        _schritt("s1", 1),
        _schritt("s2", 2),
        _schritt("s3", 3),
    )
    entwurf.schritt_entfernen("s2")
    assert [s.schritt_id for s in entwurf.prozedur_schritte] == ["s1", "s3"]
    assert [s.reihenfolge for s in entwurf.prozedur_schritte] == [1, 2]


def test_entwurf_darf_leer_sein_bis_publish():
    entwurf = Produktdefinition.anlegen(produktkodierung="1234567890")
    assert entwurf.prozedur_schritte == []
    with pytest.raises(InvariantViolation):
        entwurf.veroeffentlichen(vorlagen=vorlage_map("vorlage-a"))


def test_schritte_neu_ordnen_vollstaendig():
    entwurf = _entwurf_mit_schritten(
        _schritt("s1", 1),
        _schritt("s2", 2),
        _schritt("s3", 3),
    )
    entwurf.schritte_neu_ordnen(["s3", "s1", "s2"])
    assert [(s.schritt_id, s.reihenfolge) for s in entwurf.prozedur_schritte] == [
        ("s3", 1),
        ("s1", 2),
        ("s2", 3),
    ]


def test_schritte_neu_ordnen_doppelte_id():
    entwurf = _entwurf_mit_schritten(_schritt("s1", 1), _schritt("s2", 2))
    with pytest.raises(UngueltigeSchrittReihenfolge):
        entwurf.schritte_neu_ordnen(["s1", "s1"])


def test_schritte_neu_ordnen_fehlende_id():
    entwurf = _entwurf_mit_schritten(_schritt("s1", 1), _schritt("s2", 2))
    with pytest.raises(UngueltigeSchrittReihenfolge):
        entwurf.schritte_neu_ordnen(["s1"])


def test_schritte_neu_ordnen_unbekannte_id():
    entwurf = _entwurf_mit_schritten(_schritt("s1", 1))
    with pytest.raises(ProzedurSchrittNichtGefunden):
        entwurf.schritte_neu_ordnen(["s9"])


def test_schritt_aktualisieren_nicht_gefunden():
    entwurf = _entwurf_mit_schritten(_schritt("s1", 1))
    with pytest.raises(ProzedurSchrittNichtGefunden):
        entwurf.schritt_aktualisieren(
            "s9",
            vorlage_id="vorlage-a",
            ist_pflicht=True,
            sollvorgaben={},
        )
