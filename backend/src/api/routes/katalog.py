"""HTTP-Routen — Katalog (Bibliothek CRUD Gate 8.2a, Setup Gate 6.3a)."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response

from api.deps import get_request_deps
from api.schemas import (
    AutomatisierungZuweisenRequest,
    AutomatisierungZuweisenResponse,
    EntwurfAnlegenRequest,
    EntwurfResponse,
    ErrorResponse,
    ExternesKommandoAktualisierenRequest,
    ExternesKommandoAnlegenRequest,
    ExternesKommandoAnlegenResponse,
    ExternesKommandoDetailResponse,
    ExternesKommandoListeResponse,
    ExternesKommandoListenEintragResponse,
    RoutineAktionResponse,
    RoutineAnlegenRequest,
    RoutineAnlegenResponse,
    RoutineAktualisierenRequest,
    RoutineDetailResponse,
    RoutineListeResponse,
    RoutineListenEintragResponse,
    VersionResponse,
)
from application.katalog.automatisierung_entfernen import AutomatisierungEntfernen
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externe_kommandos_listen import ExterneKommandosListen
from application.katalog.externes_kommando_aktualisieren import ExternesKommandoAktualisieren
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.externes_kommando_lesen import ExternesKommandoLesen
from application.katalog.externes_kommando_loeschen import ExternesKommandoLoeschen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.routine_anlegen import RoutineAnlegen
from application.katalog.routine_aktualisieren import RoutineAktualisieren
from application.katalog.routine_lesen import RoutineLesen
from application.katalog.routine_loeschen import RoutineLoeschen
from application.katalog.routine_zuweisen import RoutineProzedurSchrittZuweisen
from application.katalog.routinen_listen import RoutinenListen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.routine import Routine

router = APIRouter(prefix="/katalog", tags=["Katalog"])


def _routine_aktionen_response(routine: Routine) -> list[RoutineAktionResponse]:
    return [
        RoutineAktionResponse(position=a.position, kommando_id=a.kommando_id)
        for a in sorted(routine.aktionen, key=lambda x: x.position)
    ]


def _automatisierung_response(
    entwurf_produktdefinition_id: str,
    schritt_id: str,
    schritt_kommando_id: str | None,
    schritt_routine_id: str | None,
) -> AutomatisierungZuweisenResponse:
    return AutomatisierungZuweisenResponse(
        produktdefinition_id=entwurf_produktdefinition_id,
        schritt_id=schritt_id,
        kommando_id=schritt_kommando_id,
        routine_id=schritt_routine_id,
    )


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


@router.get(
    "/bibliothek/kommandos",
    response_model=ExternesKommandoListeResponse,
)
def externe_kommandos_listen(request: Request) -> ExternesKommandoListeResponse:
    deps = get_request_deps(request)
    kommandos = ExterneKommandosListen(deps.bibliothek).execute()
    return ExternesKommandoListeResponse(
        kommandos=[
            ExternesKommandoListenEintragResponse(
                kommando_id=k.kommando_id,
                bezeichnung=k.bezeichnung,
            )
            for k in kommandos
        ]
    )


@router.get(
    "/bibliothek/kommandos/{kommando_id}",
    response_model=ExternesKommandoDetailResponse,
    responses={404: {"model": ErrorResponse}},
)
def externes_kommando_lesen(kommando_id: str, request: Request) -> ExternesKommandoDetailResponse:
    deps = get_request_deps(request)
    kommando = ExternesKommandoLesen(deps.bibliothek).execute(kommando_id)
    return ExternesKommandoDetailResponse(
        kommando_id=kommando.kommando_id,
        bezeichnung=kommando.bezeichnung,
        kommandocode=kommando.kommandocode,
    )


@router.put(
    "/bibliothek/kommandos/{kommando_id}",
    response_model=ExternesKommandoDetailResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def externes_kommando_aktualisieren(
    kommando_id: str,
    body: ExternesKommandoAktualisierenRequest,
    request: Request,
) -> ExternesKommandoDetailResponse:
    deps = get_request_deps(request)
    kommando = ExternesKommandoAktualisieren(deps.bibliothek).execute(
        kommando_id,
        bezeichnung=body.bezeichnung,
        kommandocode=body.kommandocode,
    )
    return ExternesKommandoDetailResponse(
        kommando_id=kommando.kommando_id,
        bezeichnung=kommando.bezeichnung,
        kommandocode=kommando.kommandocode,
    )


@router.delete(
    "/bibliothek/kommandos/{kommando_id}",
    status_code=204,
    response_class=Response,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def externes_kommando_loeschen(kommando_id: str, request: Request) -> Response:
    deps = get_request_deps(request)
    ExternesKommandoLoeschen(deps.katalog, deps.bibliothek).execute(kommando_id)
    return Response(status_code=204)


@router.post(
    "/bibliothek/routinen",
    status_code=201,
    response_model=RoutineAnlegenResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def routine_anlegen(body: RoutineAnlegenRequest, request: Request) -> RoutineAnlegenResponse:
    deps = get_request_deps(request)
    routine = RoutineAnlegen(deps.bibliothek).execute(
        bezeichnung=body.bezeichnung,
        kommando_ids=tuple(body.kommando_ids),
    )
    return RoutineAnlegenResponse(
        routine_id=routine.routine_id,
        bezeichnung=routine.bezeichnung,
        aktionen=_routine_aktionen_response(routine),
    )


@router.get(
    "/bibliothek/routinen",
    response_model=RoutineListeResponse,
)
def routinen_listen(request: Request) -> RoutineListeResponse:
    deps = get_request_deps(request)
    routinen = RoutinenListen(deps.bibliothek).execute()
    return RoutineListeResponse(
        routinen=[
            RoutineListenEintragResponse(
                routine_id=r.routine_id,
                bezeichnung=r.bezeichnung,
                anzahl_aktionen=len(r.aktionen),
            )
            for r in routinen
        ]
    )


@router.get(
    "/bibliothek/routinen/{routine_id}",
    response_model=RoutineDetailResponse,
    responses={404: {"model": ErrorResponse}},
)
def routine_lesen(routine_id: str, request: Request) -> RoutineDetailResponse:
    deps = get_request_deps(request)
    routine = RoutineLesen(deps.bibliothek).execute(routine_id)
    return RoutineDetailResponse(
        routine_id=routine.routine_id,
        bezeichnung=routine.bezeichnung,
        aktionen=_routine_aktionen_response(routine),
    )


@router.put(
    "/bibliothek/routinen/{routine_id}",
    response_model=RoutineDetailResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def routine_aktualisieren(
    routine_id: str,
    body: RoutineAktualisierenRequest,
    request: Request,
) -> RoutineDetailResponse:
    deps = get_request_deps(request)
    routine = RoutineAktualisieren(deps.bibliothek).execute(
        routine_id,
        bezeichnung=body.bezeichnung,
        kommando_ids=tuple(body.kommando_ids),
    )
    return RoutineDetailResponse(
        routine_id=routine.routine_id,
        bezeichnung=routine.bezeichnung,
        aktionen=_routine_aktionen_response(routine),
    )


@router.delete(
    "/bibliothek/routinen/{routine_id}",
    status_code=204,
    response_class=Response,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def routine_loeschen(routine_id: str, request: Request) -> Response:
    deps = get_request_deps(request)
    RoutineLoeschen(deps.katalog, deps.bibliothek).execute(routine_id)
    return Response(status_code=204)


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

    if body.kommando_id is not None:
        entwurf = KommandoProzedurSchrittZuweisen(deps.katalog, deps.bibliothek).execute(
            produktdefinition_id,
            schritt_id,
            body.kommando_id,
        )
    elif body.routine_id is not None:
        entwurf = RoutineProzedurSchrittZuweisen(deps.katalog, deps.bibliothek).execute(
            produktdefinition_id,
            schritt_id,
            body.routine_id,
        )
    else:
        entwurf = AutomatisierungEntfernen(deps.katalog).execute(
            produktdefinition_id,
            schritt_id,
        )

    schritt = next(s for s in entwurf.prozedur_schritte if s.schritt_id == schritt_id)
    return _automatisierung_response(
        entwurf.produktdefinition_id,
        schritt_id,
        schritt.kommando_id,
        schritt.routine_id,
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
