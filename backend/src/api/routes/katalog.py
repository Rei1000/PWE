"""HTTP-Routen — Katalog (Bibliothek CRUD Gate 8.2a, Setup Gate 6.3a)."""

from __future__ import annotations

from fastapi import APIRouter, Body, Request, Response

from api.authz import require_identity_lesen, require_katalog_bearbeiten, require_katalog_veroeffentlichen
from api.current_user import RequestCurrentUserProvider
from api.deps import get_request_deps
from api.schemas import (
    AktiveProdukteListeResponse,
    AktivesProduktResponse,
    AutomatisierungZuweisenRequest,
    AutomatisierungZuweisenResponse,
    EntwurfAnlegenRequest,
    EntwurfDetailResponse,
    EntwurfResponse,
    ErrorResponse,
    ExternesKommandoAktualisierenRequest,
    ExternesKommandoAnlegenRequest,
    ExternesKommandoAnlegenResponse,
    ExternesKommandoDetailResponse,
    ExternesKommandoListeResponse,
    ExternesKommandoListenEintragResponse,
    ProzedurSchrittAnlegenRequest,
    ProzedurSchrittAktualisierenRequest,
    ProzedurSchrittEntwurfResponse,
    ProzedurSchrittReihenfolgeRequest,
    PruefschrittVorlageAktualisierenRequest,
    PruefschrittVorlageAnlegenRequest,
    PruefschrittVorlageAnlegenResponse,
    PruefschrittVorlageDetailResponse,
    PruefschrittVorlageListeResponse,
    PruefschrittVorlageListenEintragResponse,
    RoutineAktionResponse,
    RoutineAnlegenRequest,
    RoutineAnlegenResponse,
    RoutineAktualisierenRequest,
    RoutineDetailResponse,
    RoutineListeResponse,
    RoutineListenEintragResponse,
    VeroeffentlichenRequest,
    VersionResponse,
)
from application.katalog.aktive_produkte_listen import AktiveProdukteListen
from application.katalog.automatisierung_entfernen import AutomatisierungEntfernen
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.entwurf_lesen import EntwurfLesen
from application.katalog.externe_kommandos_listen import ExterneKommandosListen
from application.katalog.externes_kommando_aktualisieren import ExternesKommandoAktualisieren
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.externes_kommando_lesen import ExternesKommandoLesen
from application.katalog.externes_kommando_loeschen import ExternesKommandoLoeschen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.prozedur_schritt_anlegen import ProzedurSchrittAnlegen
from application.katalog.prozedur_schritt_aktualisieren import ProzedurSchrittAktualisieren
from application.katalog.prozedur_schritt_loeschen import ProzedurSchrittLoeschen
from application.katalog.prozedur_schritt_reihenfolge_aendern import ProzedurSchrittReihenfolgeAendern
from application.katalog.pruefschritt_vorlage_aktualisieren import PruefschrittVorlageAktualisieren
from application.katalog.pruefschritt_vorlage_anlegen import PruefschrittVorlageAnlegen
from application.katalog.pruefschritt_vorlage_lesen import PruefschrittVorlageLesen
from application.katalog.pruefschritt_vorlage_loeschen import PruefschrittVorlageLoeschen
from application.katalog.pruefschritt_vorlagen_listen import PruefschrittVorlagenListen
from application.katalog.routine_anlegen import RoutineAnlegen
from application.katalog.routine_aktualisieren import RoutineAktualisieren
from application.katalog.routine_lesen import RoutineLesen
from application.katalog.routine_loeschen import RoutineLoeschen
from application.katalog.routine_zuweisen import RoutineProzedurSchrittZuweisen
from application.katalog.routinen_listen import RoutinenListen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from domain.katalog.routine import Routine

router = APIRouter(prefix="/katalog", tags=["Katalog"])


@router.get("/aktive-produkte", response_model=AktiveProdukteListeResponse)
def aktive_produkte_listen(request: Request) -> AktiveProdukteListeResponse:
    require_identity_lesen(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    produkte = AktiveProdukteListen(deps.katalog).execute()
    return AktiveProdukteListeResponse(
        produkte=[
            AktivesProduktResponse(
                produktkodierung=p.produktkodierung,
                produktdefinition_id=p.produktdefinition_id,
                version_id=p.version_id,
            )
            for p in produkte
        ]
    )


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
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
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
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
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
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
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
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
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
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
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
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    RoutineLoeschen(deps.katalog, deps.bibliothek).execute(routine_id)
    return Response(status_code=204)


@router.post(
    "/bibliothek/vorlagen",
    status_code=201,
    response_model=PruefschrittVorlageAnlegenResponse,
    responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def pruefschritt_vorlage_anlegen(
    body: PruefschrittVorlageAnlegenRequest,
    request: Request,
) -> PruefschrittVorlageAnlegenResponse:
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    vorlage = PruefschrittVorlageAnlegen(deps.bibliothek).execute(
        bezeichnung=body.bezeichnung,
        beschreibung=body.beschreibung,
    )
    return PruefschrittVorlageAnlegenResponse(
        vorlage_id=vorlage.vorlage_id,
        bezeichnung=vorlage.bezeichnung,
    )


@router.get(
    "/bibliothek/vorlagen",
    response_model=PruefschrittVorlageListeResponse,
)
def pruefschritt_vorlagen_listen(request: Request) -> PruefschrittVorlageListeResponse:
    deps = get_request_deps(request)
    vorlagen = PruefschrittVorlagenListen(deps.bibliothek).execute()
    return PruefschrittVorlageListeResponse(
        vorlagen=[
            PruefschrittVorlageListenEintragResponse(
                vorlage_id=v.vorlage_id,
                bezeichnung=v.bezeichnung,
            )
            for v in vorlagen
        ]
    )


@router.get(
    "/bibliothek/vorlagen/{vorlage_id}",
    response_model=PruefschrittVorlageDetailResponse,
    responses={404: {"model": ErrorResponse}},
)
def pruefschritt_vorlage_lesen(
    vorlage_id: str, request: Request
) -> PruefschrittVorlageDetailResponse:
    deps = get_request_deps(request)
    vorlage = PruefschrittVorlageLesen(deps.bibliothek).execute(vorlage_id)
    return PruefschrittVorlageDetailResponse(
        vorlage_id=vorlage.vorlage_id,
        bezeichnung=vorlage.bezeichnung,
        beschreibung=vorlage.beschreibung,
    )


@router.put(
    "/bibliothek/vorlagen/{vorlage_id}",
    response_model=PruefschrittVorlageDetailResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def pruefschritt_vorlage_aktualisieren(
    vorlage_id: str,
    body: PruefschrittVorlageAktualisierenRequest,
    request: Request,
) -> PruefschrittVorlageDetailResponse:
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    vorlage = PruefschrittVorlageAktualisieren(deps.bibliothek).execute(
        vorlage_id,
        bezeichnung=body.bezeichnung,
        beschreibung=body.beschreibung,
    )
    return PruefschrittVorlageDetailResponse(
        vorlage_id=vorlage.vorlage_id,
        bezeichnung=vorlage.bezeichnung,
        beschreibung=vorlage.beschreibung,
    )


@router.delete(
    "/bibliothek/vorlagen/{vorlage_id}",
    status_code=204,
    response_class=Response,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def pruefschritt_vorlage_loeschen(vorlage_id: str, request: Request) -> Response:
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    PruefschrittVorlageLoeschen(deps.katalog, deps.bibliothek).execute(vorlage_id)
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
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
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


def _schritt_response(schritt: ProzedurSchrittEntwurf) -> ProzedurSchrittEntwurfResponse:
    return ProzedurSchrittEntwurfResponse(
        schritt_id=schritt.schritt_id,
        vorlage_id=schritt.vorlage_id,
        ist_pflicht=schritt.ist_pflicht,
        reihenfolge=schritt.reihenfolge,
        sollvorgaben=schritt.sollvorgaben,
        kommando_id=schritt.kommando_id,
        routine_id=schritt.routine_id,
    )


def _entwurf_detail_response(entwurf: Produktdefinition) -> EntwurfDetailResponse:
    schritte = sorted(entwurf.prozedur_schritte, key=lambda s: s.reihenfolge)
    return EntwurfDetailResponse(
        produktdefinition_id=entwurf.produktdefinition_id,
        produktkodierung=entwurf.produktkodierung,
        sollbestueckung=list(entwurf.sollbestueckung),
        prozedur_schritte=[_schritt_response(s) for s in schritte],
    )


@router.get(
    "/entwuerfe/{produktdefinition_id}",
    response_model=EntwurfDetailResponse,
    responses={404: {"model": ErrorResponse}},
)
def entwurf_lesen(produktdefinition_id: str, request: Request) -> EntwurfDetailResponse:
    deps = get_request_deps(request)
    entwurf = EntwurfLesen(deps.katalog).execute(produktdefinition_id)
    return _entwurf_detail_response(entwurf)


@router.post(
    "/entwuerfe/{produktdefinition_id}/schritte",
    status_code=201,
    response_model=ProzedurSchrittEntwurfResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def prozedur_schritt_anlegen(
    produktdefinition_id: str,
    body: ProzedurSchrittAnlegenRequest,
    request: Request,
) -> ProzedurSchrittEntwurfResponse:
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    schritt = ProzedurSchrittAnlegen(deps.katalog, deps.bibliothek).execute(
        produktdefinition_id,
        schritt_id=body.schritt_id,
        vorlage_id=body.vorlage_id,
        ist_pflicht=body.ist_pflicht,
        sollvorgaben=body.sollvorgaben,
    )
    return _schritt_response(schritt)


@router.put(
    "/entwuerfe/{produktdefinition_id}/schritte/reihenfolge",
    response_model=EntwurfDetailResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def prozedur_schritt_reihenfolge_aendern(
    produktdefinition_id: str,
    body: ProzedurSchrittReihenfolgeRequest,
    request: Request,
) -> EntwurfDetailResponse:
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    entwurf = ProzedurSchrittReihenfolgeAendern(deps.katalog).execute(
        produktdefinition_id,
        body.schritt_ids,
    )
    return _entwurf_detail_response(entwurf)


@router.put(
    "/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}",
    response_model=ProzedurSchrittEntwurfResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def prozedur_schritt_aktualisieren(
    produktdefinition_id: str,
    schritt_id: str,
    body: ProzedurSchrittAktualisierenRequest,
    request: Request,
) -> ProzedurSchrittEntwurfResponse:
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    schritt = ProzedurSchrittAktualisieren(deps.katalog, deps.bibliothek).execute(
        produktdefinition_id,
        schritt_id,
        vorlage_id=body.vorlage_id,
        ist_pflicht=body.ist_pflicht,
        sollvorgaben=body.sollvorgaben,
    )
    return _schritt_response(schritt)


@router.delete(
    "/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}",
    status_code=204,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def prozedur_schritt_loeschen(
    produktdefinition_id: str,
    schritt_id: str,
    request: Request,
) -> Response:
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
    deps = get_request_deps(request)
    ProzedurSchrittLoeschen(deps.katalog).execute(produktdefinition_id, schritt_id)
    return Response(status_code=204)


@router.post("/entwuerfe", status_code=201, response_model=EntwurfResponse)
def entwurf_anlegen(body: EntwurfAnlegenRequest, request: Request) -> EntwurfResponse:
    require_katalog_bearbeiten(RequestCurrentUserProvider(request).require())
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
    produktdefinition_id: str,
    request: Request,
    body: VeroeffentlichenRequest = Body(default_factory=VeroeffentlichenRequest),
) -> VersionResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_katalog_veroeffentlichen(aktueller)
    deps = get_request_deps(request)
    flag = body.einweisung_uebernehmen
    version = ProduktdefinitionVeroeffentlichen(deps.katalog, deps.bibliothek).execute(
        produktdefinition_id,
        einweisung_uebernehmen=flag,
        eingewiesen_durch=aktueller.benutzer_id if flag else None,
        einweisungen=deps.einweisung_repo if flag else None,
    )
    return VersionResponse(
        version_id=version.version_id,
        produktdefinition_id=version.produktdefinition_id,
        produktkodierung=version.produktkodierung,
    )
