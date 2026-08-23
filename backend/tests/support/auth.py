"""Test-Hilfe — Session-Login + CSRF (Gate 8.1a)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.auth_settings import CSRF_HEADER
from api.identity_seed import DEFAULT_ADMIN_LOGIN, DEFAULT_ADMIN_PASSWORD


def login_as_admin(
    client: TestClient,
    *,
    login: str = DEFAULT_ADMIN_LOGIN,
    passwort: str = DEFAULT_ADMIN_PASSWORD,
) -> dict[str, str]:
    response = client.post("/auth/login", json={"login": login, "passwort": passwort})
    assert response.status_code == 200, response.text
    csrf = response.json()["csrf_token"]
    return {CSRF_HEADER: csrf}
