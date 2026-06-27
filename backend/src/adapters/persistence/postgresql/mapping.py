"""Domain ↔ JSON-Mapping — nur im Adapter."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.protokoll.snapshot import ProtokollSnapshot
from domain.pruefausfuehrung.abschluss_view import PrueflaufAbschlussView, SchrittAbschlussView
from domain.pruefausfuehrung.prueflauf import Prueflauf, PruefschrittDurchfuehrung
from domain.pruefausfuehrung.typen import (
    Beurteilung,
    BeurteilungErgebnis,
    Nachweis,
    NachweisArt,
    PrueflaufStatus,
)


def _dt_to_str(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _dt_from_str(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _dump(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False)


def _load(raw: str) -> dict[str, Any]:
    return json.loads(raw)


def entwurf_to_payload(entwurf: Produktdefinition) -> str:
    return _dump(
        {
            "produktdefinition_id": entwurf.produktdefinition_id,
            "produktkodierung": entwurf.produktkodierung,
            "basisprodukt_sollvorgaben": entwurf.basisprodukt_sollvorgaben,
            "kundenprofil_sollvorgaben": entwurf.kundenprofil_sollvorgaben,
            "definition_sollvorgaben": entwurf.definition_sollvorgaben,
            "prozedur_schritte": [
                {
                    "schritt_id": s.schritt_id,
                    "vorlage_id": s.vorlage_id,
                    "ist_pflicht": s.ist_pflicht,
                    "reihenfolge": s.reihenfolge,
                    "sollvorgaben": s.sollvorgaben,
                }
                for s in entwurf.prozedur_schritte
            ],
            "sollbestueckung": list(entwurf.sollbestueckung),
            "aktive_version_id": entwurf.aktive_version_id,
        }
    )


def entwurf_from_payload(raw: str) -> Produktdefinition:
    data = _load(raw)
    return Produktdefinition(
        produktdefinition_id=data["produktdefinition_id"],
        produktkodierung=data["produktkodierung"],
        basisprodukt_sollvorgaben=data.get("basisprodukt_sollvorgaben", {}),
        kundenprofil_sollvorgaben=data.get("kundenprofil_sollvorgaben", {}),
        definition_sollvorgaben=data.get("definition_sollvorgaben", {}),
        prozedur_schritte=[
            ProzedurSchrittEntwurf(
                schritt_id=s["schritt_id"],
                vorlage_id=s["vorlage_id"],
                ist_pflicht=s["ist_pflicht"],
                reihenfolge=s["reihenfolge"],
                sollvorgaben=s.get("sollvorgaben", {}),
            )
            for s in data.get("prozedur_schritte", [])
        ],
        sollbestueckung=tuple(data.get("sollbestueckung", [])),
        aktive_version_id=data.get("aktive_version_id"),
    )


def version_to_payload(version: ProduktdefinitionsVersion) -> str:
    return _dump(
        {
            "version_id": version.version_id,
            "produktdefinition_id": version.produktdefinition_id,
            "produktkodierung": version.produktkodierung,
            "prozedur_schritte": [
                {
                    "schritt_id": s.schritt_id,
                    "vorlage_id": s.vorlage_id,
                    "ist_pflicht": s.ist_pflicht,
                    "reihenfolge": s.reihenfolge,
                    "sollvorgaben": s.sollvorgaben,
                }
                for s in version.prozedur_schritte
            ],
            "sollbestueckung": list(version.sollbestueckung),
        }
    )


def version_from_payload(raw: str) -> ProduktdefinitionsVersion:
    data = _load(raw)
    return ProduktdefinitionsVersion(
        version_id=data["version_id"],
        produktdefinition_id=data["produktdefinition_id"],
        produktkodierung=data["produktkodierung"],
        prozedur_schritte=tuple(
            MaterialisierterProzedurSchritt(
                schritt_id=s["schritt_id"],
                vorlage_id=s["vorlage_id"],
                ist_pflicht=s["ist_pflicht"],
                reihenfolge=s["reihenfolge"],
                sollvorgaben=s.get("sollvorgaben", {}),
            )
            for s in data.get("prozedur_schritte", [])
        ),
        sollbestueckung=tuple(data.get("sollbestueckung", [])),
    )


def _nachweis_to_dict(n: Nachweis) -> dict[str, Any]:
    return {
        "nachweis_id": n.nachweis_id,
        "art": n.art.value,
        "erfasst_am": _dt_to_str(n.erfasst_am),
        "payload": n.payload,
        "bezug_nachweis_id": n.bezug_nachweis_id,
        "ist_automatisch": n.ist_automatisch,
    }


def _nachweis_from_dict(data: dict[str, Any]) -> Nachweis:
    return Nachweis(
        nachweis_id=data["nachweis_id"],
        art=NachweisArt(data["art"]),
        erfasst_am=_dt_from_str(data["erfasst_am"]),
        payload=data.get("payload", {}),
        bezug_nachweis_id=data.get("bezug_nachweis_id"),
        ist_automatisch=data.get("ist_automatisch", False),
    )


def prueflauf_to_payload(prueflauf: Prueflauf) -> str:
    durchfuehrungen = {}
    for schritt_id, d in prueflauf.durchfuehrungen.items():
        beurteilung = None
        if d.beurteilung is not None:
            beurteilung = {
                "ergebnis": d.beurteilung.ergebnis.value,
                "festgelegt_am": _dt_to_str(d.beurteilung.festgelegt_am),
                "kommentar": d.beurteilung.kommentar,
            }
        durchfuehrungen[schritt_id] = {
            "prozedur_schritt_id": d.prozedur_schritt_id,
            "nachweise": [_nachweis_to_dict(n) for n in d.nachweise],
            "beurteilung": beurteilung,
        }

    return _dump(
        {
            "prueflauf_id": prueflauf.prueflauf_id,
            "version_id": prueflauf.version_id,
            "pruefobjekt_kennung": prueflauf.pruefobjekt_kennung,
            "produktkodierung": prueflauf.produktkodierung,
            "pruefer_id": prueflauf.pruefer_id,
            "gestartet_am": _dt_to_str(prueflauf.gestartet_am),
            "status": prueflauf.status.value,
            "durchfuehrungen": durchfuehrungen,
            "abgeschlossen_am": _dt_to_str(prueflauf.abgeschlossen_am)
            if prueflauf.abgeschlossen_am
            else None,
            "erfasste_komponenten": sorted(prueflauf.erfasste_komponenten),
            "bestueckung_nachweise": [_nachweis_to_dict(n) for n in prueflauf.bestueckung_nachweise],
            "fehlende_sollbestueckung_snapshot": list(prueflauf.fehlende_sollbestueckung_snapshot),
        }
    )


def prueflauf_from_payload(raw: str) -> Prueflauf:
    data = _load(raw)
    durchfuehrungen: dict[str, PruefschrittDurchfuehrung] = {}
    for schritt_id, d in data.get("durchfuehrungen", {}).items():
        beurteilung = None
        if d.get("beurteilung"):
            b = d["beurteilung"]
            beurteilung = Beurteilung(
                ergebnis=BeurteilungErgebnis(b["ergebnis"]),
                festgelegt_am=_dt_from_str(b["festgelegt_am"]),
                kommentar=b.get("kommentar"),
            )
        durchfuehrungen[schritt_id] = PruefschrittDurchfuehrung(
            prozedur_schritt_id=d["prozedur_schritt_id"],
            nachweise=[_nachweis_from_dict(n) for n in d.get("nachweise", [])],
            beurteilung=beurteilung,
        )

    abgeschlossen_raw = data.get("abgeschlossen_am")
    return Prueflauf(
        prueflauf_id=data["prueflauf_id"],
        version_id=data["version_id"],
        pruefobjekt_kennung=data["pruefobjekt_kennung"],
        produktkodierung=data["produktkodierung"],
        pruefer_id=data["pruefer_id"],
        gestartet_am=_dt_from_str(data["gestartet_am"]),
        status=PrueflaufStatus(data["status"]),
        durchfuehrungen=durchfuehrungen,
        abgeschlossen_am=_dt_from_str(abgeschlossen_raw) if abgeschlossen_raw else None,
        erfasste_komponenten=set(data.get("erfasste_komponenten", [])),
        bestueckung_nachweise=[_nachweis_from_dict(n) for n in data.get("bestueckung_nachweise", [])],
        fehlende_sollbestueckung_snapshot=tuple(data.get("fehlende_sollbestueckung_snapshot", [])),
    )


def snapshot_to_payload(snapshot: ProtokollSnapshot) -> str:
    return _dump(
        {
            "snapshot_id": snapshot.snapshot_id,
            "prueflauf_id": snapshot.prueflauf_id,
            "version_id": snapshot.version_id,
            "pruefobjekt_kennung": snapshot.pruefobjekt_kennung,
            "produktkodierung": snapshot.produktkodierung,
            "pruefer_id": snapshot.pruefer_id,
            "gestartet_am": _dt_to_str(snapshot.gestartet_am),
            "abgeschlossen_am": _dt_to_str(snapshot.abgeschlossen_am),
            "ist_gueltig": snapshot.ist_gueltig,
            "schritte": [
                {
                    "prozedur_schritt_id": s.prozedur_schritt_id,
                    "ist_pflicht": s.ist_pflicht,
                    "beurteilung": s.beurteilung.value if s.beurteilung else None,
                    "nachweis_ids": list(s.nachweis_ids),
                }
                for s in snapshot.schritte
            ],
            "fehlende_sollbestueckung": list(snapshot.fehlende_sollbestueckung),
        }
    )


def snapshot_from_payload(raw: str) -> ProtokollSnapshot:
    data = _load(raw)
    schritte = tuple(
        SchrittAbschlussView(
            prozedur_schritt_id=s["prozedur_schritt_id"],
            ist_pflicht=s["ist_pflicht"],
            beurteilung=BeurteilungErgebnis(s["beurteilung"]) if s.get("beurteilung") else None,
            nachweis_ids=tuple(s.get("nachweis_ids", [])),
        )
        for s in data.get("schritte", [])
    )
    return ProtokollSnapshot(
        snapshot_id=data["snapshot_id"],
        prueflauf_id=data["prueflauf_id"],
        version_id=data["version_id"],
        pruefobjekt_kennung=data["pruefobjekt_kennung"],
        produktkodierung=data["produktkodierung"],
        pruefer_id=data["pruefer_id"],
        gestartet_am=_dt_from_str(data["gestartet_am"]),
        abgeschlossen_am=_dt_from_str(data["abgeschlossen_am"]),
        ist_gueltig=data["ist_gueltig"],
        schritte=schritte,
        fehlende_sollbestueckung=tuple(data.get("fehlende_sollbestueckung", [])),
    )
