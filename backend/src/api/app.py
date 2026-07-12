"""FastAPI-Anwendung — Transport ohne Fachlogik (ADR-0002)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
from starlette.responses import Response

from api.deps import ApiDeps, in_memory_deps
from api.errors import register_exception_handlers
from api.persistence import (
    PersistenceSettings,
    PostgresDepsFactory,
    create_session_factory,
    initialize_postgresql_engine,
    postgres_deps,
)
from api.routes import katalog, prueflaeufe


def create_app(
    deps: ApiDeps | None = None,
    *,
    postgres_deps_factory: PostgresDepsFactory | None = None,
) -> FastAPI:
    settings = PersistenceSettings.from_env()
    use_postgresql = deps is None and settings.database_url is not None
    resolve_postgres_deps: PostgresDepsFactory = postgres_deps_factory or postgres_deps

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if deps is not None:
            app.state.persistence_mode = "in-memory"
            app.state.deps = deps
        elif settings.database_url is not None:
            engine = initialize_postgresql_engine(settings.database_url)
            app.state.engine = engine
            app.state.session_factory = create_session_factory(engine)
            app.state.persistence_mode = "postgresql"
        else:
            app.state.persistence_mode = "in-memory"
            app.state.deps = in_memory_deps()
        yield
        if hasattr(app.state, "engine"):
            app.state.engine.dispose()

    app = FastAPI(title="PWE API", version="0.1.0", lifespan=lifespan)
    register_exception_handlers(app)

    if use_postgresql:

        @app.middleware("http")
        async def postgres_unit_of_work(request: Request, call_next) -> Response:
            session: Session = app.state.session_factory()
            request.state.deps = resolve_postgres_deps(session)
            try:
                response = await call_next(request)
                session.commit()
                return response
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(katalog.router)
    app.include_router(prueflaeufe.router)
    return app
