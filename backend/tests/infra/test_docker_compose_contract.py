"""Infra-Contract-Tests — docker-compose Dev-Stack (Gate 7.2 / 7.5b)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
DOCKERFILE = REPO_ROOT / "infra/docker/backend.Dockerfile"
ENTRYPOINT = REPO_ROOT / "infra/docker/backend-entrypoint.sh"


def test_compose_definiert_postgres_und_backend():
    text = COMPOSE_FILE.read_text(encoding="utf-8")
    assert "postgres:15" in text
    assert "backend:" in text
    assert "postgresql+psycopg://postgres:postgres@db:5432/app" in text
    assert "condition: service_healthy" in text
    assert "pg_isready" in text


def test_backend_dockerfile_migriert_dann_startet_fastapi():
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert ".[persistence,pdf,api]" in text
    assert "alembic.ini" in text
    assert "alembic" in text
    assert "backend-entrypoint.sh" in text
    assert "ENTRYPOINT" in text
    assert "http.server" not in text


def test_backend_entrypoint_upgrade_then_uvicorn():
    text = ENTRYPOINT.read_text(encoding="utf-8")
    assert "alembic upgrade head" in text
    assert "uvicorn" in text
    assert "api.app:create_app" in text
    assert "--factory" in text
    # Migration vor App-Start, nicht innerhalb FastAPI
    assert text.index("alembic upgrade head") < text.index("uvicorn")
