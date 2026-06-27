"""FastAPI-Anwendung — Transport ohne Fachlogik (ADR-0002)."""

from __future__ import annotations

from fastapi import FastAPI

from api.deps import ApiDeps, in_memory_deps
from api.errors import register_exception_handlers
from api.routes import katalog, prueflaeufe


def create_app(deps: ApiDeps | None = None) -> FastAPI:
    app = FastAPI(title="PWE API", version="0.1.0")
    app.state.deps = deps or in_memory_deps()
    register_exception_handlers(app)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(katalog.router)
    app.include_router(prueflaeufe.router)
    return app
