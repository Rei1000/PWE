"""Soll/Ist-Beurteilung — Domain Model §4.18, ADR-0007."""

from __future__ import annotations

from typing import Any

from domain.pruefausfuehrung.typen import BeurteilungErgebnis, Nachweis, NachweisArt


class BeurteilungService:
    @staticmethod
    def aus_soll_und_nachweisen(
        nachweise: list[Nachweis],
        sollvorgaben: dict[str, Any],
    ) -> BeurteilungErgebnis:
        if not sollvorgaben:
            return (
                BeurteilungErgebnis.BESTANDEN
                if nachweise
                else BeurteilungErgebnis.NICHT_BESTANDEN
            )

        for feld, regel in sollvorgaben.items():
            wert = _messwert_fuer_feld(nachweise, feld)
            if wert is None:
                return BeurteilungErgebnis.NICHT_BESTANDEN
            if not _regel_erfuellt(wert, regel):
                return BeurteilungErgebnis.NICHT_BESTANDEN

        return BeurteilungErgebnis.BESTANDEN


def _messwert_fuer_feld(nachweise: list[Nachweis], feld: str) -> float | int | None:
    for n in reversed(nachweise):
        if n.art != NachweisArt.MESSWERT:
            continue
        if feld in n.payload:
            raw = n.payload[feld]
            if isinstance(raw, (int, float)):
                return raw
    return None


def _regel_erfuellt(wert: float | int, regel: Any) -> bool:
    if not isinstance(regel, dict):
        return False
    min_val = regel.get("min")
    max_val = regel.get("max")
    if min_val is not None and wert < min_val:
        return False
    if max_val is not None and wert > max_val:
        return False
    return True
