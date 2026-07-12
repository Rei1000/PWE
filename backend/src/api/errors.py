"""HTTP-Fehlerabbildung für Domain-Fehler."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.fehler import (
    domain_error_code,
    fehler_response,
    http_status_for_domain_error,
    oeffentliche_fehlermeldung,
)
from domain.shared.errors import DomainError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        status = http_status_for_domain_error(exc)
        return JSONResponse(
            status_code=status,
            content=fehler_response(
                detail=oeffentliche_fehlermeldung(exc),
                code=domain_error_code(exc),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=fehler_response(detail="Validierungsfehler", code="validation"),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(_request: Request, _exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=fehler_response(detail="Ungültiger Wert in der Anfrage", code="ungueltiger_wert"),
        )
