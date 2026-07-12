"""HTTP-DTOs — nur Transport, keine Domain-Logik."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from enum import Enum

from pydantic import BaseModel, Field


class PrueflaufStartenRequest(BaseModel):
    produktkodierung: str
    pruefobjekt_kennung: str
    pruefer_id: str


class PrueflaufResponse(BaseModel):
    prueflauf_id: str
    version_id: str
    produktkodierung: str
    pruefobjekt_kennung: str
    pruefer_id: str
    status: str


class KomponenteErfassenRequest(BaseModel):
    komponenten_typ: str
    seriennummer: str


class NachweisArtEnum(str, Enum):
    """Transport-Enum — Werte sind der öffentliche API-Contract (lowercase snake_case)."""

    MESSWERT = "messwert"
    FOTO = "foto"
    KOMMENTAR = "kommentar"
    MANUELLE_EINGABE = "manuelle_eingabe"
    ROHANTWORT = "rohantwort"
    EXTRAHIERTER_WERT = "extrahierter_wert"
    ERGAENZUNG = "ergaenzung"
    KOMPONENTENERFASSUNG = "komponentenerfassung"


NACHWEIS_ART_API_WERTE: tuple[str, ...] = tuple(member.value for member in NachweisArtEnum)


class NachweisErfassenRequest(BaseModel):
    art: NachweisArtEnum
    payload: dict[str, Any] = Field(default_factory=dict)
    ist_automatisch: bool = False


class NachweisResponse(BaseModel):
    nachweis_id: str
    art: str


class AbschlussResponse(BaseModel):
    prueflauf_id: str
    status: str
    ist_gueltig: bool
    snapshot_id: str


class ProzedurSchrittEntwurfRequest(BaseModel):
    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any] = Field(default_factory=dict)


class EntwurfAnlegenRequest(BaseModel):
    produktkodierung: str
    prozedur_schritte: list[ProzedurSchrittEntwurfRequest]
    sollbestueckung: list[str] = Field(default_factory=list)
    basisprodukt_sollvorgaben: dict[str, Any] = Field(default_factory=dict)
    kundenprofil_sollvorgaben: dict[str, Any] = Field(default_factory=dict)
    definition_sollvorgaben: dict[str, Any] = Field(default_factory=dict)


class EntwurfResponse(BaseModel):
    produktdefinition_id: str
    produktkodierung: str


class VersionResponse(BaseModel):
    version_id: str
    produktdefinition_id: str
    produktkodierung: str


class NachweisDetailResponse(BaseModel):
    nachweis_id: str
    art: str
    erfasst_am: datetime
    payload: dict[str, Any]
    ist_automatisch: bool


class BeurteilungResponse(BaseModel):
    ergebnis: str
    festgelegt_am: datetime
    kommentar: str | None = None


class SchrittDurchfuehrungResponse(BaseModel):
    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any]
    nachweise: list[NachweisDetailResponse]
    beurteilung: BeurteilungResponse | None = None
    kann_nachweis_erfassen: bool = False
    kann_beurteilt_werden: bool = False


class PrueflaufDetailResponse(BaseModel):
    prueflauf_id: str
    version_id: str
    produktkodierung: str
    pruefobjekt_kennung: str
    pruefer_id: str
    status: str
    gestartet_am: datetime
    abgeschlossen_am: datetime | None = None
    schritte: list[SchrittDurchfuehrungResponse]
    sollbestueckung: list[str]
    erfasste_komponenten: list[str]
    ist_abgeschlossen: bool = False
    fehlende_komponenten: list[str] = Field(default_factory=list)
    kann_komponente_erfassen: bool = False
    kann_abgeschlossen_werden: bool = False
