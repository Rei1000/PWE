"""HTTP-DTOs — nur Transport, keine Domain-Logik."""

from __future__ import annotations

from typing import Any

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


class NachweisErfassenRequest(BaseModel):
    art: str
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
