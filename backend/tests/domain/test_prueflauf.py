"""Domain-Tests Prueflauf-Aggregate und BeurteilungService."""

import pytest

from domain.pruefausfuehrung.beurteilung_service import BeurteilungService
from domain.pruefausfuehrung.prueflauf import (
    BeurteilungErgebnis,
    Nachweis,
    NachweisArt,
    Prueflauf,
    PrueflaufStatus,
)
from domain.shared.errors import InvariantViolation


def _nachweis(art: NachweisArt, payload: dict) -> Nachweis:
    from datetime import datetime, timezone

    return Nachweis(
        nachweis_id="n1",
        art=art,
        erfasst_am=datetime.now(timezone.utc),
        payload=payload,
    )


def test_beurteilung_service_bestanden_bei_soll_erfuellt():
    ergebnis = BeurteilungService.aus_soll_und_nachweisen(
        [_nachweis(NachweisArt.MESSWERT, {"spannung": 230})],
        {"spannung": {"min": 220, "max": 240}},
    )
    assert ergebnis == BeurteilungErgebnis.BESTANDEN


def test_beurteilung_service_nicht_bestanden_bei_soll_verletzt():
    ergebnis = BeurteilungService.aus_soll_und_nachweisen(
        [_nachweis(NachweisArt.MESSWERT, {"spannung": 200})],
        {"spannung": {"min": 220, "max": 240}},
    )
    assert ergebnis == BeurteilungErgebnis.NICHT_BESTANDEN


def test_prueflauf_beurteilen_schritt_aus_soll():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.add_nachweis("s1", NachweisArt.MESSWERT, {"spannung": 230})
    b = p.beurteilen_schritt("s1", {"spannung": {"min": 220, "max": 240}})
    assert b.ergebnis == BeurteilungErgebnis.BESTANDEN


def test_beurteilung_aenderbar_vor_laufabschluss():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.add_nachweis("s1", NachweisArt.MESSWERT, {"spannung": 200})
    p.beurteilen_schritt("s1", {"spannung": {"min": 220, "max": 240}})
    p.add_nachweis("s1", NachweisArt.MESSWERT, {"spannung": 230})
    b = p.beurteilen_schritt("s1", {"spannung": {"min": 220, "max": 240}})
    assert b.ergebnis == BeurteilungErgebnis.BESTANDEN


def test_nachweis_wellen_akkumulieren():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.add_nachweis("s1", NachweisArt.ROHANTWORT, {"raw": "fail"}, ist_automatisch=True)
    p.add_nachweis("s1", NachweisArt.MESSWERT, {"spannung": 42}, ist_automatisch=True)
    assert len(p.durchfuehrungen["s1"].nachweise) == 2


def test_pflichtschritt_nicht_bestanden_macht_lauf_ungueltig():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["pflicht"],
    )
    p.add_nachweis("pflicht", NachweisArt.MESSWERT, {"wert": 1})
    p.beurteilen_schritt("pflicht", {"wert": {"min": 10, "max": 20}})
    p.abschliessen(frozenset({"pflicht"}))
    assert p.status == PrueflaufStatus.ABGESCHLOSSEN_UNGUELTIG


def test_fehlende_sollbestueckung_macht_lauf_ungueltig():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.beurteilen_schritt("s1", {})
    p.add_nachweis("s1", NachweisArt.KOMMENTAR, {"text": "dummy"})
    p.beurteilen_schritt("s1", {})
    p.abschliessen(frozenset(), ("mainboard",))
    assert p.status == PrueflaufStatus.ABGESCHLOSSEN_UNGUELTIG
    assert p.fehlende_sollbestueckung_snapshot == ("mainboard",)


def test_komponente_erfassen_reduziert_fehlende_sollbestueckung():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.erfasse_komponente("mainboard", "MB-123")
    assert p.fehlende_sollbestueckung(("mainboard",)) == ()


def test_abgeschlossener_prueflauf_unveraenderlich():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.add_nachweis("s1", NachweisArt.KOMMENTAR, {"text": "ok"})
    p.beurteilen_schritt("s1", {})
    p.abschliessen(frozenset())
    with pytest.raises(InvariantViolation):
        p.add_nachweis("s1", NachweisArt.KOMMENTAR, {"text": "zu spät"})


def test_protokollsnapshot_aus_abschluss_view():
    p = Prueflauf.starten(
        version_id="v1",
        pruefobjekt_kennung="SN-001",
        produktkodierung="ART-001",
        pruefer_id="user-1",
        prozedur_schritt_ids=["s1"],
    )
    p.add_nachweis("s1", NachweisArt.MESSWERT, {"x": 1})
    p.beurteilen_schritt("s1", {})
    p.abschliessen(frozenset({"s1"}))
    view = p.to_abschluss_view({"s1": True})
    from domain.protokoll.snapshot import ProtokollSnapshot

    snap = ProtokollSnapshot.aus_abschluss("snap-1", view)
    assert snap.ist_gueltig is True
    assert snap.prueflauf_id == p.prueflauf_id
