"""PDF-Adapter für ProtokollErzeugungPort."""

from __future__ import annotations

from fpdf import FPDF

from domain.protokoll.dokument import ProtokollDokument
from domain.protokoll.snapshot import ProtokollSnapshot


class PdfProtokollErzeugungAdapter:
    """Erzeugt ein minimales PDF aus ProtokollSnapshot (ADR-0004 Mindestinhalt)."""

    def erzeugen(self, snapshot: ProtokollSnapshot) -> ProtokollDokument:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(text="PWE Prüfprotokoll")
        pdf.ln(10)

        pdf.set_font("Helvetica", size=10)
        zeilen = [
            f"Prüflauf: {snapshot.prueflauf_id}",
            f"Version: {snapshot.version_id}",
            f"Produktkodierung: {snapshot.produktkodierung}",
            f"Prüfobjekt: {snapshot.pruefobjekt_kennung}",
            f"Prüfer: {snapshot.pruefer_id}",
            f"Gestartet: {snapshot.gestartet_am.isoformat()}",
            f"Abgeschlossen: {snapshot.abgeschlossen_am.isoformat()}",
            f"Gültig: {'ja' if snapshot.ist_gueltig else 'nein'}",
        ]
        if snapshot.fehlende_sollbestueckung:
            zeilen.append(
                f"Fehlende Sollbestückung: {', '.join(snapshot.fehlende_sollbestueckung)}"
            )

        for zeile in zeilen:
            pdf.cell(text=zeile)
            pdf.ln(6)

        pdf.ln(4)
        pdf.cell(text="Schritte:")
        pdf.ln(6)
        for schritt in snapshot.schritte:
            beurteilung = schritt.beurteilung.value if schritt.beurteilung else "offen"
            pdf.cell(
                text=(
                    f"- {schritt.prozedur_schritt_id} "
                    f"(Pflicht: {'ja' if schritt.ist_pflicht else 'nein'}) "
                    f"Beurteilung: {beurteilung}"
                )
            )
            pdf.ln(5)

        inhalt = pdf.output()
        return ProtokollDokument(
            inhalt=inhalt,
            medientyp="application/pdf",
            dateiname=f"protokoll-{snapshot.prueflauf_id}.pdf",
        )
