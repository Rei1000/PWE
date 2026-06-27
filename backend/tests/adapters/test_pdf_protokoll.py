"""Tests — PDF-Adapter für ProtokollErzeugungPort."""

from datetime import datetime, timezone

from adapters.pdf.protokoll_erzeugung import PdfProtokollErzeugungAdapter
from domain.protokoll.snapshot import ProtokollSnapshot
from domain.pruefausfuehrung.abschluss_view import PrueflaufAbschlussView, SchrittAbschlussView
from domain.pruefausfuehrung.typen import BeurteilungErgebnis

_NOW = datetime(2026, 6, 27, 14, 0, tzinfo=timezone.utc)


def _snapshot() -> ProtokollSnapshot:
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
    return ProtokollSnapshot.aus_abschluss("snap-1", view)


def test_pdf_adapter_erzeugt_gueltiges_pdf():
    dokument = PdfProtokollErzeugungAdapter().erzeugen(_snapshot())

    assert dokument.inhalt.startswith(b"%PDF")
    assert dokument.medientyp == "application/pdf"
    assert dokument.dateiname == "protokoll-lauf-1.pdf"


def test_pdf_enthaelt_inhalt_aus_snapshot():
    dokument = PdfProtokollErzeugungAdapter().erzeugen(_snapshot())

    assert len(dokument.inhalt) > 200
    assert dokument.medientyp == "application/pdf"
