"""HTTP-Routen — Auth (Gate 8.1a)."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response

from api.auth_settings import CSRF_COOKIE, SESSION_COOKIE, AuthCookieSettings
from api.current_user import RequestCurrentUserProvider
from api.deps import get_request_deps
from api.schemas import LoginRequest, LoginResponse, MeResponse
from application.identity.login import Login
from application.identity.logout import Logout


router = APIRouter(prefix="/auth", tags=["Auth"])


def _set_auth_cookies(
    response: Response,
    *,
    session_id: str,
    csrf_token: str,
    settings: AuthCookieSettings,
) -> None:
    common = {
        "httponly": True,
        "secure": settings.secure,
        "samesite": settings.samesite,
        "path": "/",
    }
    response.set_cookie(SESSION_COOKIE, session_id, **common)
    # CSRF: für Double-Submit vom Frontend lesbar (nicht HttpOnly)
    response.set_cookie(
        CSRF_COOKIE,
        csrf_token,
        httponly=False,
        secure=settings.secure,
        samesite=settings.samesite,
        path="/",
    )


def _clear_auth_cookies(response: Response, settings: AuthCookieSettings) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")


@router.post("/login", response_model=LoginResponse)
def auth_login(body: LoginRequest, request: Request, response: Response) -> LoginResponse:
    deps = get_request_deps(request)
    settings: AuthCookieSettings = request.app.state.auth_cookie_settings
    ergebnis = Login(deps.benutzer_repo, deps.passwort_hasher, deps.session_store).execute(
        login=body.login,
        passwort=body.passwort,
    )
    _set_auth_cookies(
        response,
        session_id=ergebnis.session_id,
        csrf_token=ergebnis.csrf_token,
        settings=settings,
    )
    return LoginResponse(
        benutzer_id=ergebnis.benutzer.benutzer_id,
        login=ergebnis.benutzer.login,
        anzeigename=ergebnis.benutzer.anzeigename,
        rollen=sorted(r.value for r in ergebnis.benutzer.rollen),
        csrf_token=ergebnis.csrf_token,
    )


@router.post("/logout", status_code=204)
def auth_logout(request: Request, response: Response) -> Response:
    deps = get_request_deps(request)
    settings: AuthCookieSettings = request.app.state.auth_cookie_settings
    session_id = request.cookies.get(SESSION_COOKIE)
    Logout(deps.session_store).execute(session_id=session_id)
    _clear_auth_cookies(response, settings)
    return Response(status_code=204)


@router.get("/me", response_model=MeResponse)
def auth_me(request: Request) -> MeResponse:
    benutzer = RequestCurrentUserProvider(request).require()
    return MeResponse(
        benutzer_id=benutzer.benutzer_id,
        login=benutzer.login,
        anzeigename=benutzer.anzeigename,
        status=benutzer.status.value,
        rollen=sorted(r.value for r in benutzer.rollen),
    )
