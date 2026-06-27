"""Domain-Tests — Beurteilung mit extrahierten Werten."""

from datetime import datetime, timezone

from domain.pruefausfuehrung.beurteilung_service import BeurteilungService
from domain.pruefausfuehrung.typen import BeurteilungErgebnis, Nachweis, NachweisArt

_NOW = datetime(2026, 6, 27, 12, 0, tzinfo=timezone.utc)


def test_beurteilung_nutzt_extrahierten_wert():
    nachweise = [
        Nachweis(
            nachweis_id="n1",
            art=NachweisArt.ROHANTWORT,
            erfasst_am=_NOW,
            payload={"rohdaten": "RAW:230"},
            ist_automatisch=True,
        ),
        Nachweis(
            nachweis_id="n2",
            art=NachweisArt.EXTRAHIERTER_WERT,
            erfasst_am=_NOW,
            payload={"feld": "spannung", "wert": 230},
            ist_automatisch=True,
            bezug_nachweis_id="n1",
        ),
    ]

    ergebnis = BeurteilungService.aus_soll_und_nachweisen(
        nachweise,
        {"spannung": {"min": 220, "max": 240}},
    )

    assert ergebnis == BeurteilungErgebnis.BESTANDEN
