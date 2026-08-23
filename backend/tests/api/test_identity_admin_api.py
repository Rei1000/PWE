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


def test_force_change_blockiert_identity_und_prueflauf():
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
        assert client.get("/identity/benutzer", headers=headers).status_code == 403
        assert client.get("/identity/profile", headers=headers).status_code == 403
        assert (
            client.post(
                "/prueflaeufe",
                json={"produktkodierung": "1234567890", "pruefobjekt_kennung": "X"},
                headers=headers,
            ).status_code
            == 403
        )


def test_einweisung_nur_fuer_aktiven_benutzer():
    from domain.katalog.version import ProduktdefinitionsVersion

    deps = in_memory_deps()
    deps.katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-e1",
            produktdefinition_id="pd-e1",
            produktkodierung="1111111111",
            prozedur_schritte=(),
        )
    )
    app = create_app(deps)
    with TestClient(app) as client:
        neu = client.post(
            "/identity/benutzer",
            json={
                "login": "einw-neu",
                "anzeigename": "N",
                "passwort": "geheim-1",
                "rollen": ["pruefer"],
            },
        )
        assert neu.status_code == 201
        bid = neu.json()["benutzer_id"]
        r = client.post(
            "/identity/einweisungen",
            json={"benutzer_id": bid, "version_id": "ver-e1"},
        )
        assert r.status_code == 409


def test_sperren_invalidiert_alle_sessions():
    from datetime import UTC, datetime

    from ports.session_store import SessionDaten

    deps = in_memory_deps()
    hasher = deps.passwort_hasher
    ziel = Benutzer.anlegen(
        login="ziel",
        anzeigename="Z",
        passwort_hash=hasher.hash("z"),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
        benutzer_id="ziel-1",
    )
    deps.benutzer_repo.save(ziel)
    now = datetime.now(UTC)
    for sid in ("s1", "s2"):
        deps.session_store.speichern(
            SessionDaten(
                session_id=sid,
                benutzer_id="ziel-1",
                csrf_token="c",
                erzeugt_am=now,
                zuletzt_gesehen_am=now,
            )
        )
    app = create_app(deps)
    with TestClient(app) as client:
        assert client.post("/identity/benutzer/ziel-1/sperren").status_code == 200
    assert deps.session_store.laden("s1") is None
    assert deps.session_store.laden("s2") is None


def test_profil_deaktivieren_blockiert_start_lauf_bleibt():
    from domain.identity.berechtigungsprofil import Berechtigungsprofil
    from domain.identity.einweisungsnachweis import Einweisungsnachweis
    from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion

    deps = in_memory_deps()
    deps.katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-p",
            produktdefinition_id="pd-p",
            produktkodierung="2222222222",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="s1", vorlage_id="v1", ist_pflicht=True, reihenfolge=1
                ),
            ),
        )
    )
    app = create_app(deps)
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        profil = Berechtigungsprofil.anlegen(
            bezeichnung="P", produktdefinition_ids={"pd-p"}
        )
        deps.profile_repo.save(profil)
        deps.profile_repo.benutzer_zuordnen(
            profil_id=profil.profil_id, benutzer_id=me["benutzer_id"]
        )
        deps.einweisung_repo.save(
            Einweisungsnachweis.anlegen(
                benutzer_id=me["benutzer_id"],
                version_id="ver-p",
                eingewiesen_durch="admin",
            )
        )
        ok = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "2222222222", "pruefobjekt_kennung": "X"},
        )
        assert ok.status_code == 201, ok.text
        assert (
            client.post(f"/identity/profile/{profil.profil_id}/deaktivieren").status_code
            == 200
        )
        blocked = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "2222222222", "pruefobjekt_kennung": "Y"},
        )
        assert blocked.status_code == 403
        pid = ok.json()["prueflauf_id"]
        cont = client.post(
            f"/prueflaeufe/{pid}/schritte/s1/nachweise",
            json={"art": "kommentar", "payload": {"text": "ok"}},
        )
        assert cont.status_code == 201, cont.text
        assert (
            client.post(f"/identity/profile/{profil.profil_id}/aktivieren").status_code
            == 200
        )
        again = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "2222222222", "pruefobjekt_kennung": "Z"},
        )
        assert again.status_code == 201, again.text
