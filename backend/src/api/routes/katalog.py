"""HTTP-Routen — Katalog (minimal für Frontend-Vorbereitung)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from api.schemas import EntwurfAnlegenRequest, EntwurfResponse, VersionResponse
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf

router = APIRouter(prefix="/katalog", tags=["Katalog"])


@router.post("/entwuerfe", status_code=201, response_model=EntwurfResponse)
def entwurf_anlegen(body: EntwurfAnlegenRequest, request: Request) -> EntwurfResponse:
    deps = request.app.state.deps
    schritte = tuple(
        ProzedurSchrittEntwurf(
            schritt_id=s.schritt_id,
            vorlage_id=s.vorlage_id,
            ist_pflicht=s.ist_pflicht,
            reihenfolge=s.reihenfolge,
            sollvorgaben=s.sollvorgaben,
        )
        for s in body.prozedur_schritte
    )
    entwurf = EntwurfAnlegen(deps.katalog).execute(
        produktkodierung=body.produktkodierung,
        prozedur_schritte=schritte,
        sollbestueckung=tuple(body.sollbestueckung),
        basisprodukt_sollvorgaben=body.basisprodukt_sollvorgaben or None,
        kundenprofil_sollvorgaben=body.kundenprofil_sollvorgaben or None,
        definition_sollvorgaben=body.definition_sollvorgaben or None,
    )
    return EntwurfResponse(
        produktdefinition_id=entwurf.produktdefinition_id,
        produktkodierung=entwurf.produktkodierung,
    )


@router.post(
    "/entwuerfe/{produktdefinition_id}/veroeffentlichen",
    status_code=201,
    response_model=VersionResponse,
)
def entwurf_veroeffentlichen(
    produktdefinition_id: str, request: Request
) -> VersionResponse:
    deps = request.app.state.deps
    version = ProduktdefinitionVeroeffentlichen(deps.katalog).execute(produktdefinition_id)
    return VersionResponse(
        version_id=version.version_id,
        produktdefinition_id=version.produktdefinition_id,
        produktkodierung=version.produktkodierung,
    )
