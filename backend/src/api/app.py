"""FastAPI-Anwendung — Transport ohne Fachlogik (ADR-0002)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
from starlette.responses import Response

from api.auth_middleware import apply_authentication
from api.auth_settings import AuthCookieSettings
from api.datei_speicher_wiring import DateiSpeicherSettings, create_datei_speicher
from api.deps import ApiDeps, in_memory_deps
from api.errors import register_exception_handlers
from api.identity_seed import ensure_seed_administrator
from api.kommando_wiring import KommandoAdapterSettings, configure_kommando_adapter
from api.persistence import (
    PersistenceSettings,
    PostgresDepsFactory,
    create_session_factory,
    initialize_postgresql_engine,
    postgres_deps,
)
from api.routes import auth, identity_qualification, katalog, prueflaeufe
from adapters.security.argon2_hasher import Argon2PasswortHasher
from adapters.persistence.postgresql.identity_repository import PostgresBenutzerRepository


def create_app(
    deps: ApiDeps | None = None,
    *,
    postgres_deps_factory: PostgresDepsFactory | None = None,
) -> FastAPI:
    settings = PersistenceSettings.from_env()
    use_postgresql = deps is None and settings.database_url is not None
    resolve_postgres_deps: PostgresDepsFactory = postgres_deps_factory or postgres_deps
    auth_cookie_settings = AuthCookieSettings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.auth_cookie_settings = auth_cookie_settings
        if deps is None:
            configure_kommando_adapter(KommandoAdapterSettings.from_env())
            app.state.datei_speicher = create_datei_speicher(DateiSpeicherSettings.from_env())
        if deps is not None:
            app.state.persistence_mode = "in-memory"
            app.state.deps = deps
        elif settings.database_url is not None:
            engine = initialize_postgresql_engine(settings.database_url)
            app.state.engine = engine
            app.state.session_factory = create_session_factory(engine)
            app.state.persistence_mode = "postgresql"
            session = app.state.session_factory()
            try:
                hasher = Argon2PasswortHasher()
                ensure_seed_administrator(PostgresBenutzerRepository(session), hasher)
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
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
            request.state.deps = resolve_postgres_deps(session, app.state.datei_speicher)
            try:

                async def after_deps(req: Request) -> Response:
                    return await apply_authentication(req, call_next)

                response = await after_deps(request)
                session.commit()
                return response
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    else:

        @app.middleware("http")
        async def in_memory_auth(request: Request, call_next) -> Response:
            return await apply_authentication(request, call_next)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(katalog.router)
    app.include_router(prueflaeufe.router)
    app.include_router(identity_qualification.router)
    return app
