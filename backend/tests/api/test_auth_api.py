"""API-Tests — Auth Foundation (Gate 8.1a)."""

from fastapi.testclient import TestClient
from starlette.testclient import TestClient as RawTestClient

from api.app import create_app
from api.deps import in_memory_deps
from api.identity_seed import DEFAULT_ADMIN_LOGIN
from tests.support.auth import login_as_admin


def test_login_logout_me():
    app = create_app(in_memory_deps())
    with RawTestClient(app) as client:
        bad = client.post(
            "/auth/login",
            json={"login": DEFAULT_ADMIN_LOGIN, "passwort": "wrong"},
        )
        assert bad.status_code == 401

        headers = login_as_admin(client)
        me = client.get("/auth/me")
        assert me.status_code == 200
        assert me.json()["login"] == DEFAULT_ADMIN_LOGIN
        assert "administrator" in me.json()["rollen"]

        out = client.post("/auth/logout", headers=headers)
        assert out.status_code == 204
        assert client.get("/auth/me").status_code == 401


def test_protected_route_requires_auth():
    app = create_app(in_memory_deps())
    with RawTestClient(app) as client:
        assert client.get("/auth/me").status_code == 401
        r = client.get("/prueflaeufe/does-not-exist")
        assert r.status_code == 401


def test_prueflauf_start_uses_session_user_not_body():
    from adapters.persistence.in_memory import InMemoryKatalogRepository
    from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion

    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-1",
            produktdefinition_id="pd-1",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    sollvorgaben={},
                ),
            ),
            sollbestueckung=(),
        )
    )
    app = create_app(deps)
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        response = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": "1234567890",
                "pruefobjekt_kennung": "SN-1",
                "pruefer_id": "impersonate-me",
            },
        )
        assert response.status_code == 201, response.text
        assert response.json()["pruefer_id"] == me["benutzer_id"]
        assert response.json()["pruefer_id"] != "impersonate-me"


def test_csrf_required_when_session_present():
    app = create_app(in_memory_deps())
    with RawTestClient(app) as client:
        login_as_admin(client)
        response = client.post("/auth/logout")
        assert response.status_code == 403
        assert response.json()["code"] == "csrf_ungueltig"
