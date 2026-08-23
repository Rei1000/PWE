"""HTTP-Routen — Qualifikation: Profile und Einweisungen (Gate 8.1b)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Request, Response

from api.authz import require_rollen
from api.current_user import RequestCurrentUserProvider
from api.deps import get_request_deps
from api.schemas import (
    EinweisungAnlegenRequest,
    EinweisungResponse,
    ProfilAktualisierenRequest,
    ProfilAnlegenRequest,
    ProfilResponse,
)
from application.identity.einweisung_verwaltung import (
    EinweisungAnlegen,
    EinweisungLesen,
    EinweisungWiderrufen,
)
from application.identity.profil_verwaltung import (
    ProfilAktualisieren,
    ProfilAnlegen,
    ProfilBenutzerEntfernen,
    ProfilBenutzerZuordnen,
    ProfilLesen,
)
from domain.identity.typen import Systemrolle

router = APIRouter(prefix="/identity", tags=["Identity"])


def _profil_response(profil) -> ProfilResponse:
    return ProfilResponse(
        profil_id=profil.profil_id,
        bezeichnung=profil.bezeichnung,
        beschreibung=profil.beschreibung,
        produktdefinition_ids=sorted(profil.produktdefinition_ids),
    )


def _einweisung_response(e) -> EinweisungResponse:
    return EinweisungResponse(
        einweisung_id=e.einweisung_id,
        benutzer_id=e.benutzer_id,
        version_id=e.version_id,
        eingewiesen_durch=e.eingewiesen_durch,
        datum=e.datum,
        status=e.status.value,
        gueltig_bis=e.gueltig_bis.isoformat() if e.gueltig_bis else None,
        bemerkung=e.bemerkung,
        herkunft_einweisung_id=e.herkunft_einweisung_id,
        uebernommen_bei_publish=e.uebernommen_bei_publish,
    )


@router.post("/profile", status_code=201, response_model=ProfilResponse)
def profil_anlegen(body: ProfilAnlegenRequest, request: Request) -> ProfilResponse:
    benutzer = RequestCurrentUserProvider(request).require()
    require_rollen(benutzer, Systemrolle.ADMINISTRATOR, Systemrolle.QM)
    deps = get_request_deps(request)
    profil = ProfilAnlegen(deps.profile_repo).execute(
        bezeichnung=body.bezeichnung,
        beschreibung=body.beschreibung,
        produktdefinition_ids=body.produktdefinition_ids,
    )
    return _profil_response(profil)


@router.get("/profile/{profil_id}", response_model=ProfilResponse)
def profil_lesen(profil_id: str, request: Request) -> ProfilResponse:
    RequestCurrentUserProvider(request).require()
    deps = get_request_deps(request)
    profil = ProfilLesen(deps.profile_repo).execute(profil_id)
    return _profil_response(profil)


@router.put("/profile/{profil_id}", response_model=ProfilResponse)
def profil_aktualisieren(
    profil_id: str, body: ProfilAktualisierenRequest, request: Request
) -> ProfilResponse:
    benutzer = RequestCurrentUserProvider(request).require()
    require_rollen(benutzer, Systemrolle.ADMINISTRATOR, Systemrolle.QM)
    deps = get_request_deps(request)
    profil = ProfilAktualisieren(deps.profile_repo).execute(
        profil_id=profil_id,
        bezeichnung=body.bezeichnung,
        beschreibung=body.beschreibung,
        produktdefinition_ids=body.produktdefinition_ids,
    )
    return _profil_response(profil)


@router.put("/profile/{profil_id}/benutzer/{benutzer_id}", status_code=204, response_class=Response)
def profil_benutzer_zuordnen(
    profil_id: str, benutzer_id: str, request: Request
) -> Response:
    aktueller = RequestCurrentUserProvider(request).require()
    require_rollen(aktueller, Systemrolle.ADMINISTRATOR, Systemrolle.ABTEILUNGSLEITER)
    deps = get_request_deps(request)
    ProfilBenutzerZuordnen(deps.profile_repo, deps.benutzer_repo).execute(
        profil_id=profil_id, benutzer_id=benutzer_id
    )
    return Response(status_code=204)


@router.delete(
    "/profile/{profil_id}/benutzer/{benutzer_id}", status_code=204, response_class=Response
)
def profil_benutzer_entfernen(
    profil_id: str, benutzer_id: str, request: Request
) -> Response:
    aktueller = RequestCurrentUserProvider(request).require()
    require_rollen(aktueller, Systemrolle.ADMINISTRATOR, Systemrolle.ABTEILUNGSLEITER)
    deps = get_request_deps(request)
    ProfilBenutzerEntfernen(deps.profile_repo).execute(
        profil_id=profil_id, benutzer_id=benutzer_id
    )
    return Response(status_code=204)


@router.post("/einweisungen", status_code=201, response_model=EinweisungResponse)
def einweisung_anlegen(body: EinweisungAnlegenRequest, request: Request) -> EinweisungResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_rollen(aktueller, Systemrolle.ADMINISTRATOR, Systemrolle.ABTEILUNGSLEITER)
    deps = get_request_deps(request)
    gueltig_bis = date.fromisoformat(body.gueltig_bis) if body.gueltig_bis else None
    e = EinweisungAnlegen(deps.einweisung_repo, deps.benutzer_repo, deps.katalog).execute(
        benutzer_id=body.benutzer_id,
        version_id=body.version_id,
        eingewiesen_durch=aktueller.benutzer_id,
        gueltig_bis=gueltig_bis,
        bemerkung=body.bemerkung,
    )
    return _einweisung_response(e)


@router.get("/einweisungen/{einweisung_id}", response_model=EinweisungResponse)
def einweisung_lesen(einweisung_id: str, request: Request) -> EinweisungResponse:
    RequestCurrentUserProvider(request).require()
    deps = get_request_deps(request)
    e = EinweisungLesen(deps.einweisung_repo).execute(einweisung_id)
    return _einweisung_response(e)


@router.post(
    "/einweisungen/{einweisung_id}/widerrufen",
    response_model=EinweisungResponse,
)
def einweisung_widerrufen(einweisung_id: str, request: Request) -> EinweisungResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_rollen(aktueller, Systemrolle.ADMINISTRATOR, Systemrolle.ABTEILUNGSLEITER)
    deps = get_request_deps(request)
    e = EinweisungWiderrufen(deps.einweisung_repo).execute(einweisung_id)
    return _einweisung_response(e)
