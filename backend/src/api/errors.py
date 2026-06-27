"""HTTP-Fehlerabbildung für Domain-Fehler."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.fehler import domain_error_code, fehler_response
from domain.shared.errors import DomainError, InvariantViolation


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        status = 409 if isinstance(exc, InvariantViolation) else 404
        return JSONResponse(
            status_code=status,
            content=fehler_response(detail=str(exc), code=domain_error_code(exc)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=fehler_response(detail="Validierungsfehler", code="validation"),
        )
