"""HTTP-Routen — Benutzerverwaltung und Audit (Gate 8.1c1)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from api.authz import require_administrator, require_identity_lesen
from api.current_user import RequestCurrentUserProvider
from api.deps import get_request_deps
from api.schemas import (
    AuditEintragResponse,
    AuditListeResponse,
    BenutzerAnlegenRequest,
    BenutzerListeResponse,
    BenutzerResponse,
    BenutzerRollenSetzenRequest,
    PasswortResetRequest,
)
from application.identity.benutzer_verwaltung import (
    BenutzerAktivieren,
    BenutzerAnlegen,
    BenutzerArchivieren,
    BenutzerEntsperren,
    BenutzerLesen,
    BenutzerListen,
    BenutzerRollenSetzen,
    BenutzerSperren,
    BenutzerWiederherstellen,
)
from application.identity.passwort_verwaltung import PasswortZuruecksetzen
from domain.identity.typen import Systemrolle

router = APIRouter(prefix="/identity", tags=["Identity"])


def _benutzer_response(b, *, profil_ids: list[str] | None = None) -> BenutzerResponse:
    return BenutzerResponse(
        benutzer_id=b.benutzer_id,
        login=b.login,
        anzeigename=b.anzeigename,
        status=b.status.value,
        rollen=sorted(r.value for r in b.rollen),
        passwortwechsel_erforderlich=b.passwortwechsel_erforderlich,
        profil_ids=profil_ids if profil_ids is not None else [],
    )


def _rollen_from_body(werte: list[str]) -> frozenset[Systemrolle]:
    return frozenset(Systemrolle(v) for v in werte)


@router.get("/benutzer", response_model=BenutzerListeResponse)
def benutzer_listen(request: Request) -> BenutzerListeResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_identity_lesen(aktueller)
    deps = get_request_deps(request)
    liste = BenutzerListen(deps.benutzer_repo).execute()
    return BenutzerListeResponse(benutzer=[_benutzer_response(b) for b in liste])


@router.get("/benutzer/{benutzer_id}", response_model=BenutzerResponse)
def benutzer_lesen(benutzer_id: str, request: Request) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_identity_lesen(aktueller)
    deps = get_request_deps(request)
    b = BenutzerLesen(deps.benutzer_repo).execute(benutzer_id)
    profil_ids = sorted(deps.profile_repo.profil_ids_fuer_benutzer(benutzer_id))
    return _benutzer_response(b, profil_ids=profil_ids)


@router.post("/benutzer", status_code=201, response_model=BenutzerResponse)
def benutzer_anlegen(body: BenutzerAnlegenRequest, request: Request) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    b = BenutzerAnlegen(deps.benutzer_repo, deps.passwort_hasher, deps.audit_repo).execute(
        akteur_id=aktueller.benutzer_id,
        login=body.login,
        anzeigename=body.anzeigename,
        passwort_klartext=body.passwort,
        rollen=_rollen_from_body(body.rollen),
    )
    return _benutzer_response(b)


@router.post("/benutzer/{benutzer_id}/aktivieren", response_model=BenutzerResponse)
def benutzer_aktivieren(benutzer_id: str, request: Request) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    b = BenutzerAktivieren(deps.benutzer_repo, deps.session_store, deps.audit_repo).execute(
        akteur_id=aktueller.benutzer_id, benutzer_id=benutzer_id
    )
    return _benutzer_response(b)


@router.post("/benutzer/{benutzer_id}/sperren", response_model=BenutzerResponse)
def benutzer_sperren(benutzer_id: str, request: Request) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    b = BenutzerSperren(deps.benutzer_repo, deps.session_store, deps.audit_repo).execute(
        akteur_id=aktueller.benutzer_id, benutzer_id=benutzer_id
    )
    return _benutzer_response(b)


@router.post("/benutzer/{benutzer_id}/entsperren", response_model=BenutzerResponse)
def benutzer_entsperren(benutzer_id: str, request: Request) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    b = BenutzerEntsperren(deps.benutzer_repo, deps.session_store, deps.audit_repo).execute(
        akteur_id=aktueller.benutzer_id, benutzer_id=benutzer_id
    )
    return _benutzer_response(b)


@router.post("/benutzer/{benutzer_id}/archivieren", response_model=BenutzerResponse)
def benutzer_archivieren(benutzer_id: str, request: Request) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    b = BenutzerArchivieren(deps.benutzer_repo, deps.session_store, deps.audit_repo).execute(
        akteur_id=aktueller.benutzer_id, benutzer_id=benutzer_id
    )
    return _benutzer_response(b)


@router.post("/benutzer/{benutzer_id}/wiederherstellen", response_model=BenutzerResponse)
def benutzer_wiederherstellen(benutzer_id: str, request: Request) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    b = BenutzerWiederherstellen(
        deps.benutzer_repo, deps.session_store, deps.audit_repo
    ).execute(akteur_id=aktueller.benutzer_id, benutzer_id=benutzer_id)
    return _benutzer_response(b)


@router.put("/benutzer/{benutzer_id}/rollen", response_model=BenutzerResponse)
def benutzer_rollen_setzen(
    benutzer_id: str, body: BenutzerRollenSetzenRequest, request: Request
) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    b = BenutzerRollenSetzen(deps.benutzer_repo, deps.audit_repo).execute(
        akteur_id=aktueller.benutzer_id,
        benutzer_id=benutzer_id,
        rollen=_rollen_from_body(body.rollen),
    )
    return _benutzer_response(b)


@router.post("/benutzer/{benutzer_id}/passwort", response_model=BenutzerResponse)
def benutzer_passwort_reset(
    benutzer_id: str, body: PasswortResetRequest, request: Request
) -> BenutzerResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    b = PasswortZuruecksetzen(
        deps.benutzer_repo, deps.passwort_hasher, deps.session_store, deps.audit_repo
    ).execute(
        akteur_id=aktueller.benutzer_id,
        benutzer_id=benutzer_id,
        neues_passwort=body.neues_passwort,
    )
    return _benutzer_response(b)


@router.get("/audit", response_model=AuditListeResponse)
def audit_listen(request: Request) -> AuditListeResponse:
    aktueller = RequestCurrentUserProvider(request).require()
    require_administrator(aktueller)
    deps = get_request_deps(request)
    eintraege = deps.audit_repo.list_all()
    return AuditListeResponse(
        eintraege=[
            AuditEintragResponse(
                audit_id=e.audit_id,
                akteur_benutzer_id=e.akteur_benutzer_id,
                ziel_benutzer_id=e.ziel_benutzer_id,
                aktion=e.aktion,
                zeitpunkt=e.zeitpunkt,
                referenz_id=e.referenz_id,
                details=e.details,
            )
            for e in eintraege
        ]
    )
