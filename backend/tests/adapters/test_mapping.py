"""Mapping-Roundtrip-Tests ohne Datenbank."""

from datetime import datetime, timezone

from domain.katalog.externes_kommando import ExternesKommando, MaterialisiertesExternesKommando
from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.protokoll.snapshot import ProtokollSnapshot
from domain.pruefausfuehrung.abschluss_view import PrueflaufAbschlussView, SchrittAbschlussView
from domain.pruefausfuehrung.prueflauf import NachweisArt, Prueflauf
from domain.pruefausfuehrung.typen import BeurteilungErgebnis
from adapters.persistence.postgresql.mapping import (
    entwurf_from_payload,
    entwurf_to_payload,
    prueflauf_from_payload,
    prueflauf_to_payload,
    snapshot_from_payload,
    snapshot_to_payload,
    version_from_payload,
    version_to_payload,
)

_NOW = datetime(2026, 6, 27, 12, 0, tzinfo=timezone.utc)


def test_version_mapping_roundtrip_mit_kommando_snapshot():
    kommando = ExternesKommando.anlegen(bezeichnung="Reset", kommandocode="RST")
    snapshot = MaterialisiertesExternesKommando.aus(kommando)
    original = ProduktdefinitionsVersion(
        version_id="ver-kommando",
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=(
            MaterialisierterProzedurSchritt(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                externes_kommando=snapshot,
            ),
        ),
    )
    restored = version_from_payload(version_to_payload(original))
    assert restored == original


def test_entwurf_mapping_roundtrip_mit_kommando_id():
    original = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                kommando_id="kommando-1",
            ),
        ],
    )
    restored = entwurf_from_payload(entwurf_to_payload(original))
    assert restored.prozedur_schritte[0].kommando_id == "kommando-1"


def test_version_mapping_roundtrip():
    original = ProduktdefinitionsVersion(
        version_id="ver-1",
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=(
            MaterialisierterProzedurSchritt(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"spannung": {"min": 220, "max": 240}},
            ),
        ),
        sollbestueckung=("mainboard",),
    )
    restored = version_from_payload(version_to_payload(original))
    assert restored == original


def test_entwurf_mapping_roundtrip():
    original = Produktdefinition(
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ],
        aktive_version_id="ver-1",
    )
    restored = entwurf_from_payload(entwurf_to_payload(original))
    assert restored.produktdefinition_id == original.produktdefinition_id
    assert restored.aktive_version_id == "ver-1"


def test_prueflauf_mapping_roundtrip():
    prueflauf = Prueflauf.starten(
        version_id="ver-1",
        pruefobjekt_kennung="GER-1",
        produktkodierung="1234567890",
        pruefer_id="pruefer-1",
        prozedur_schritt_ids=["schritt-a"],
    )
    prueflauf.add_nachweis("schritt-a", NachweisArt.MESSWERT, {"spannung": 230})
    prueflauf.erfasse_komponente("mainboard", "MB-1")

    restored = prueflauf_from_payload(prueflauf_to_payload(prueflauf))
    assert restored.prueflauf_id == prueflauf.prueflauf_id
    assert restored.durchfuehrungen["schritt-a"].nachweise[0].payload == {"spannung": 230}
    assert "mainboard" in restored.erfasste_komponenten


def test_snapshot_mapping_roundtrip():
    view = PrueflaufAbschlussView(
        prueflauf_id="lauf-1",
        version_id="ver-1",
        pruefobjekt_kennung="GER-1",
        produktkodierung="1234567890",
        pruefer_id="pruefer-1",
        gestartet_am=_NOW,
        abgeschlossen_am=_NOW,
        ist_gueltig=True,
        schritte=(
            SchrittAbschlussView(
                prozedur_schritt_id="schritt-a",
                ist_pflicht=True,
                beurteilung=BeurteilungErgebnis.BESTANDEN,
                nachweis_ids=("nw-1",),
            ),
        ),
    )
    original = ProtokollSnapshot.aus_abschluss("snap-1", view)
    restored = snapshot_from_payload(snapshot_to_payload(original))
    assert restored.snapshot_id == original.snapshot_id
    assert restored.schritte[0].beurteilung == BeurteilungErgebnis.BESTANDEN
