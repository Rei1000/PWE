"""Domain-Tests Prueflauf-Aggregate."""

from domain.pruefausfuehrung.prueflauf import (
    BeurteilungErgebnis,
    NachweisArt,
    Prueflauf,
    PrueflaufStatus,
)
from domain.shared.errors import InvariantViolation
import pytest


def test_prueflauf_starten_legt_durchfuehrungen_an():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1", "s2"],
    )
    assert p.status == PrueflaufStatus.GESTARTET
    assert set(p.durchfuehrungen) == {"s1", "s2"}


def test_nachweis_wellen_akkumulieren():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    n1 = p.add_nachweis("s1", NachweisArt.ROHANTWORT, {"raw": "fail"}, ist_automatisch=True)
    n2 = p.add_nachweis("s1", NachweisArt.MESSWERT, {"value": 42}, ist_automatisch=True)
    assert len(p.durchfuehrungen["s1"].nachweise) == 2
    assert p.durchfuehrungen["s1"].nachweise[0].nachweis_id == n1.nachweis_id


def test_pflichtschritt_nicht_bestanden_macht_lauf_ungueltig():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["pflicht"],
    )
    p.add_nachweis("pflicht", NachweisArt.MESSWERT, {"v": 1})
    p.set_beurteilung("pflicht", BeurteilungErgebnis.NICHT_BESTANDEN)
    p.abschliessen({"pflicht"})
    assert p.status == PrueflaufStatus.ABGESCHLOSSEN_UNGUELTIG


def test_abgeschlossener_prueflauf_unveraenderlich():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.set_beurteilung("s1", BeurteilungErgebnis.BESTANDEN)
    p.abschliessen(set())
    with pytest.raises(InvariantViolation):
        p.add_nachweis("s1", NachweisArt.KOMMENTAR, {"text": "zu spät"})


def test_gueltiger_lauf_bei_bestandenen_pflichtschritten():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.set_beurteilung("s1", BeurteilungErgebnis.BESTANDEN)
    p.abschliessen({"s1"})
    assert p.ist_gueltig()
