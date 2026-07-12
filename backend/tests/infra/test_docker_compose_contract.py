"""Infra-Contract-Tests — docker-compose Dev-Stack (Gate 7.2)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
DOCKERFILE = REPO_ROOT / "infra/docker/backend.Dockerfile"


def test_compose_definiert_postgres_und_backend():
    text = COMPOSE_FILE.read_text(encoding="utf-8")
    assert "postgres:15" in text
    assert "backend:" in text
    assert "postgresql+psycopg://postgres:postgres@db:5432/app" in text
    assert "condition: service_healthy" in text
    assert "pg_isready" in text


def test_backend_dockerfile_startet_fastapi_mit_postgresql_extras():
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert ".[persistence,pdf,api]" in text
    assert "uvicorn" in text
    assert "api.app:create_app" in text
    assert "--factory" in text
    assert "http.server" not in text
