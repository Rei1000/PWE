"""Session-weite Alembic-Migration für PostgreSQL-Tests (Gate 7.5b).

Gleiche Mechanik wie Docker/CI: `alembic upgrade head` auf DATABASE_URL.
Idempotent — Legacy-DBs ohne alembic_version werden gestampt.
Isolierte Testschemas migrieren zusätzlich per ALEMBIC_SCHEMA.
"""

from __future__ import annotations

import os

import fastapi.testclient as _ftc
import pytest

from tests.support.alembic_migrate import alembic_ensure_head
from tests.support.auth import login_as_admin

# Gate 8.1a: API-Tests standardmäßig mit Session + CSRF (Seed-Admin).
AUTO_LOGIN = True
OriginalTestClient = _ftc.TestClient


class _AuthTestClient(OriginalTestClient):
    def __enter__(self):
        super().__enter__()
        if AUTO_LOGIN:
            try:
                self.headers.update(login_as_admin(self))
            except AssertionError:
                pass
        return self


_ftc.TestClient = _AuthTestClient


@pytest.fixture(scope="session", autouse=True)
def migrate_public_schema_when_database_url_set():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        yield
        return
    alembic_ensure_head(database_url=url)
    yield
