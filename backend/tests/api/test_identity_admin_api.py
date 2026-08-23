"""API-Tests — Identity Administration Backend (Gate 8.1c1)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from starlette.testclient import TestClient as RawTestClient

from api.app import create_app
from api.auth_settings import CSRF_HEADER
from api.deps import in_memory_deps
from domain.identity.benutzer import Benutzer
from domain.identity.typen import BenutzerStatus, Systemrolle


def _login(client, login: str, passwort: str) -> dict[str, str]:
    r = client.post("/auth/login", json={"login": login, "passwort": passwort})
    assert r.status_code == 200, r.text
    return {CSRF_HEADER: r.json()["csrf_token"]}


def test_benutzer_lifecycle_und_letzter_admin():
    app = create_app(in_memory_deps())
    with TestClient(app) as client:
        create = client.post(
            "/identity/benutzer",
            json={
                "login": "neu1",
                "anzeigename": "Neu",
                "passwort": "geheim-1",
                "rollen": ["pruefer"],
            },
        )
        assert create.status_code == 201, create.text
        bid = create.json()["benutzer_id"]
        assert create.json()["status"] == "neu"
        assert create.json()["passwortwechsel_erforderlich"] is True

        assert client.post(f"/identity/benutzer/{bid}/aktivieren").status_code == 200
        assert client.get(f"/identity/benutzer/{bid}").json()["status"] == "aktiv"

        me = client.get("/auth/me").json()
        # Letzten Admin (Seed) nicht sperren
        bad = client.post(f"/identity/benutzer/{me['benutzer_id']}/sperren")
        assert bad.status_code == 409
        assert bad.json()["code"] == "letzter_administrator_verletzt"


def test_pruefer_darf_benutzerliste_nicht_lesen():
    deps = in_memory_deps(seed_admin=False)
    hasher = deps.passwort_hasher
    deps.benutzer_repo.save(
        Benutzer.anlegen(
            login="nur-p",
            anzeigename="P",
            passwort_hash=hasher.hash("secret"),
            rollen=frozenset({Systemrolle.PRUEFER}),
            status=BenutzerStatus.AKTIV,
        )
    )
    app = create_app(deps)
    with RawTestClient(app) as client:
        headers = _login(client, "nur-p", "secret")
        r = client.get("/identity/benutzer", headers=headers)
        assert r.status_code == 403


def test_qm_liest_benutzer_aber_aendert_keine_rollen():
    deps = in_memory_deps(seed_admin=False)
    hasher = deps.passwort_hasher
    deps.benutzer_repo.save(
        Benutzer.anlegen(
            login="admin",
            anzeigename="A",
            passwort_hash=hasher.hash("a"),
            rollen=frozenset({Systemrolle.ADMINISTRATOR}),
            status=BenutzerStatus.AKTIV,
        )
    )
    qm = Benutzer.anlegen(
        login="qm",
        anzeigename="QM",
        passwort_hash=hasher.hash("q"),
        rollen=frozenset({Systemrolle.QM}),
        status=BenutzerStatus.AKTIV,
    )
    deps.benutzer_repo.save(qm)
    app = create_app(deps)
    with RawTestClient(app) as client:
        headers = _login(client, "qm", "q")
        assert client.get("/identity/benutzer", headers=headers).status_code == 200
        r = client.put(
            f"/identity/benutzer/{qm.benutzer_id}/rollen",
            json={"rollen": ["administrator"]},
            headers=headers,
        )
        assert r.status_code == 403


def test_force_change_blockiert_katalog():
    deps = in_memory_deps(seed_admin=False)
    hasher = deps.passwort_hasher
    deps.benutzer_repo.save(
        Benutzer.anlegen(
            login="force",
            anzeigename="F",
            passwort_hash=hasher.hash("alt"),
            rollen=frozenset({Systemrolle.ADMINISTRATOR, Systemrolle.PRUEFER}),
            status=BenutzerStatus.AKTIV,
            passwortwechsel_erforderlich=True,
        )
    )
    app = create_app(deps)
    with RawTestClient(app) as client:
        headers = _login(client, "force", "alt")
        me = client.get("/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["passwortwechsel_erforderlich"] is True
        blocked = client.post(
            "/katalog/entwuerfe",
            json={"produktkodierung": "1234567890", "prozedur_schritte": [], "sollbestueckung": []},
            headers=headers,
        )
        assert blocked.status_code == 403
        assert blocked.json()["code"] == "passwort_wechsel_erforderlich"

        changed = client.post(
            "/auth/passwort",
            json={"altes_passwort": "alt", "neues_passwort": "neu-pass"},
            headers=headers,
        )
        assert changed.status_code == 204
        # Session invalid — erneuter Login nötig
        assert client.get("/auth/me").status_code == 401


def test_audit_nur_admin():
    deps = in_memory_deps(seed_admin=False)
    hasher = deps.passwort_hasher
    deps.benutzer_repo.save(
        Benutzer.anlegen(
            login="admin",
            anzeigename="A",
            passwort_hash=hasher.hash("a"),
            rollen=frozenset({Systemrolle.ADMINISTRATOR}),
            status=BenutzerStatus.AKTIV,
        )
    )
    deps.benutzer_repo.save(
        Benutzer.anlegen(
            login="abt",
            anzeigename="Abt",
            passwort_hash=hasher.hash("b"),
            rollen=frozenset({Systemrolle.ABTEILUNGSLEITER}),
            status=BenutzerStatus.AKTIV,
        )
    )
    app = create_app(deps)
    with RawTestClient(app) as client:
        headers = _login(client, "abt", "b")
        assert client.get("/identity/audit", headers=headers).status_code == 403
        headers = _login(client, "admin", "a")
        assert client.get("/identity/audit", headers=headers).status_code == 200
