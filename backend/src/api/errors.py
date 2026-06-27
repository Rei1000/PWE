"""HTTP-Fehlerabbildung für Domain-Fehler."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.shared.errors import DomainError, InvariantViolation


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        status = 409 if isinstance(exc, InvariantViolation) else 404
        return JSONResponse(status_code=status, content={"detail": str(exc)})
