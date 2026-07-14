"""HTTP-Routen — Katalog (minimal für Frontend-Vorbereitung, Gate 6.3a Setup)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from api.deps import get_request_deps
from api.schemas import (
    AutomatisierungZuweisenRequest,
    AutomatisierungZuweisenResponse,
    EntwurfAnlegenRequest,
    EntwurfResponse,
    ErrorResponse,
    ExternesKommandoAnlegenRequest,
    ExternesKommandoAnlegenResponse,
    VersionResponse,
)
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf

router = APIRouter(prefix="/katalog", tags=["Katalog"])


@router.post(
    "/bibliothek/kommandos",
    status_code=201,
    response_model=ExternesKommandoAnlegenResponse,
    responses={422: {"model": ErrorResponse}},
)
def externes_kommando_anlegen(
    body: ExternesKommandoAnlegenRequest,
    request: Request,
) -> ExternesKommandoAnlegenResponse:
    deps = get_request_deps(request)
    kommando = ExternesKommandoAnlegen(deps.bibliothek).execute(
        bezeichnung=body.bezeichnung,
        kommandocode=body.kommandocode,
    )
    return ExternesKommandoAnlegenResponse(
        kommando_id=kommando.kommando_id,
        bezeichnung=kommando.bezeichnung,
    )


@router.put(
    "/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}/automatisierung",
    status_code=200,
    response_model=AutomatisierungZuweisenResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def automatisierung_zuweisen(
    produktdefinition_id: str,
    schritt_id: str,
    body: AutomatisierungZuweisenRequest,
    request: Request,
) -> AutomatisierungZuweisenResponse:
    deps = get_request_deps(request)
    entwurf = KommandoProzedurSchrittZuweisen(deps.katalog, deps.bibliothek).execute(
        produktdefinition_id,
        schritt_id,
        body.kommando_id,
    )
    schritt = next(s for s in entwurf.prozedur_schritte if s.schritt_id == schritt_id)
    return AutomatisierungZuweisenResponse(
        produktdefinition_id=entwurf.produktdefinition_id,
        schritt_id=schritt_id,
        kommando_id=schritt.kommando_id,
        routine_id=schritt.routine_id,
    )


@router.post("/entwuerfe", status_code=201, response_model=EntwurfResponse)
def entwurf_anlegen(body: EntwurfAnlegenRequest, request: Request) -> EntwurfResponse:
    deps = get_request_deps(request)
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
    deps = get_request_deps(request)
    version = ProduktdefinitionVeroeffentlichen(deps.katalog, deps.bibliothek).execute(
        produktdefinition_id
    )
    return VersionResponse(
        version_id=version.version_id,
        produktdefinition_id=version.produktdefinition_id,
        produktkodierung=version.produktkodierung,
    )
