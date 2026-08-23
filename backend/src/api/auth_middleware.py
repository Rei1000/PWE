"""Session-Auth + CSRF (ADR-0024) — nach Request-Deps auflösen."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from api.auth_settings import CSRF_COOKIE, CSRF_HEADER, SESSION_COOKIE, AuthCookieSettings
from api.deps import get_request_deps
from api.fehler import fehler_response
from application.identity.aktueller_benutzer import (
    AktuellerBenutzerLaden,
    NichtAuthentifiziert,
    SessionAbgelaufen,
    SessionTimeouts,
)
from domain.shared.errors import DomainError

_PUBLIC_EXACT = frozenset({
    "/health",
    "/auth/login",
    "/openapi.json",
    "/redoc",
})


def is_public_path(path: str) -> bool:
    if path in _PUBLIC_EXACT:
        return True
    return path.startswith("/docs")


def csrf_ok(request: Request) -> bool:
    """Double-Submit: bei vorhandener Session müssen Cookie und Header übereinstimmen."""
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return True
    if request.url.path == "/auth/login":
        return True
    if not request.cookies.get(SESSION_COOKIE):
        return True
    cookie_csrf = request.cookies.get(CSRF_COOKIE)
    header_csrf = request.headers.get(CSRF_HEADER)
    return bool(cookie_csrf and header_csrf and cookie_csrf == header_csrf)


async def apply_authentication(request: Request, call_next) -> Response:
    """Erwartet: request.state.deps bzw. app.state.deps sind gesetzt."""
    if not csrf_ok(request):
        return JSONResponse(
            status_code=403,
            content=fehler_response(detail="CSRF-Prüfung fehlgeschlagen", code="csrf_ungueltig"),
        )

    path = request.url.path
    if is_public_path(path):
        return await call_next(request)

    deps = get_request_deps(request)
    settings: AuthCookieSettings = request.app.state.auth_cookie_settings
    try:
        benutzer = AktuellerBenutzerLaden(
            deps.benutzer_repo,
            deps.session_store,
            SessionTimeouts(idle=settings.idle, absolute=settings.absolute),
        ).execute(session_id=request.cookies.get(SESSION_COOKIE))
    except (NichtAuthentifiziert, SessionAbgelaufen, DomainError):
        return JSONResponse(
            status_code=401,
            content=fehler_response(detail="Nicht angemeldet", code="nicht_authentifiziert"),
        )

    request.state.aktueller_benutzer = benutzer
    return await call_next(request)
