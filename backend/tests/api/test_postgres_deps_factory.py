"""API-Tests — PostgreSQL-Deps-Factory (Composition Root)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.persistence import postgres_deps

pytestmark = pytest.mark.postgresql


def test_postgres_deps_factory_wird_pro_request_aufgerufen():
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL nicht gesetzt")

    session_ids: list[int] = []

    def tracking_factory(session):
        session_ids.append(id(session))
        return postgres_deps(session)

    with TestClient(create_app(postgres_deps_factory=tracking_factory)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/health").status_code == 200

    assert len(session_ids) == 2
    assert session_ids[0] != session_ids[1]


def test_simulation_port_ist_pro_request_neu():
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL nicht gesetzt")

    port_ids: list[int] = []

    def tracking_factory(session):
        deps = postgres_deps(session)
        port_ids.append(id(deps.kommando_port))
        return deps

    with TestClient(create_app(postgres_deps_factory=tracking_factory)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/health").status_code == 200

    assert len(port_ids) == 2
    assert port_ids[0] != port_ids[1]
