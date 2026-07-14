"""Interne Kommando-Kernlogik — Port, Nachweise, Audit (ADR-0015).

Kein Repository-Zugriff, kein Speichern — nur Orchestrierung innerhalb eines geöffneten Prüflaufs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from application.pruefausfuehrung.automatisierung_audit import (
    AutomatisierungAuditKontext,
    nachweis_payload_mit_audit,
)
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAnfrage
from domain.pruefausfuehrung.prueflauf import Nachweis, NachweisArt, Prueflauf
from ports.externes_kommando_port import ExternesKommandoPort


class KommandoFehlerart(str, Enum):
    KEINE_GERAETEANTWORT = "keine_geraeteantwort"
    GERAETEFEHLSCHLAG = "geraetefehlschlag"
    UNGUELTIGE_ANTWORT = "ungueltige_antwort"


@dataclass(frozen=True)
class KommandoAusfuehrungKernErgebnis:
    nachweise: list[Nachweis]
    fehlgeschlagen: bool
    fehlerart: KommandoFehlerart | None = None


def kommandoausfuehrung_kern(
    prueflauf: Prueflauf,
    prozedur_schritt_id: str,
    snapshot: MaterialisiertesExternesKommando,
    port: ExternesKommandoPort,
    audit: AutomatisierungAuditKontext,
) -> KommandoAusfuehrungKernErgebnis:
    prueflauf.stelle_offen_sicher()
    antwort = port.ausfuehren(
        ExternesKommandoAnfrage(kommandocode=snapshot.kommandocode)
    )

    if not _hat_audit_relevante_rohantwort(antwort):
        return KommandoAusfuehrungKernErgebnis(
            nachweise=[],
            fehlgeschlagen=True,
            fehlerart=KommandoFehlerart.KEINE_GERAETEANTWORT,
        )

    roh_nachweis = prueflauf.add_nachweis(
        prozedur_schritt_id,
        NachweisArt.ROHANTWORT,
        nachweis_payload_mit_audit(
            {
                "kommando_id": snapshot.kommando_id,
                "kommandocode": snapshot.kommandocode,
                "rohdaten": antwort.rohdaten,
                "erfolgreich": antwort.erfolgreich,
            },
            audit,
        ),
        ist_automatisch=True,
    )
    nachweise: list[Nachweis] = [roh_nachweis]

    if antwort.erfolgreich:
        for feld, wert in antwort.extrahierte_werte.items():
            nachweise.append(
                prueflauf.add_nachweis(
                    prozedur_schritt_id,
                    NachweisArt.EXTRAHIERTER_WERT,
                    nachweis_payload_mit_audit(
                        {
                            "kommando_id": snapshot.kommando_id,
                            "feld": feld,
                            "wert": wert,
                        },
                        audit,
                    ),
                    ist_automatisch=True,
                    bezug_nachweis_id=roh_nachweis.nachweis_id,
                )
            )
        return KommandoAusfuehrungKernErgebnis(
            nachweise=nachweise,
            fehlgeschlagen=False,
        )

    fehlerart = _klassifiziere_fehler(antwort)
    return KommandoAusfuehrungKernErgebnis(
        nachweise=nachweise,
        fehlgeschlagen=True,
        fehlerart=fehlerart,
    )


def _klassifiziere_fehler(antwort) -> KommandoFehlerart:
    if antwort.extrahierte_werte:
        return KommandoFehlerart.UNGUELTIGE_ANTWORT
    return KommandoFehlerart.GERAETEFEHLSCHLAG


def _hat_audit_relevante_rohantwort(antwort) -> bool:
    return bool(antwort.rohdaten.strip())
