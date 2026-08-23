"""API-Tests — Qualification Engine Business Cases (Gate 8.1b)."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient

from adapters.persistence.in_memory import InMemoryKatalogRepository
from api.app import create_app
from api.auth_settings import CSRF_HEADER
from api.deps import in_memory_deps
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import Einweisungsnachweis
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.prueflauf import Prueflauf
from tests.support.qualification import qualify_client_for_kodierung


def _version(**kwargs) -> ProduktdefinitionsVersion:
    defaults = dict(
        version_id="ver-1",
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=(
            MaterialisierterProzedurSchritt(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
        sollbestueckung=(),
    )
    defaults.update(kwargs)
    return ProduktdefinitionsVersion(**defaults)


def _app_with_version(**kwargs):
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(_version(**kwargs))
    return create_app(deps), deps


def test_start_ohne_einweisung_403():
    app, deps = _app_with_version()
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        # nur Profil, keine Einweisung
        profil = Berechtigungsprofil.anlegen(
            bezeichnung="P", produktdefinition_ids={"pd-1"}
        )
        deps.profile_repo.save(profil)
        deps.profile_repo.benutzer_zuordnen(
            profil_id=profil.profil_id, benutzer_id=me["benutzer_id"]
        )
        r = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "1234567890", "pruefobjekt_kennung": "X"},
        )
        assert r.status_code == 403
        assert r.json()["code"] == "qualifikation_unzureichend"


def test_start_ohne_profil_403():
    app, deps = _app_with_version()
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        deps.einweisung_repo.save(
            Einweisungsnachweis.anlegen(
                benutzer_id=me["benutzer_id"],
                version_id="ver-1",
                eingewiesen_durch="admin",
            )
        )
        r = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "1234567890", "pruefobjekt_kennung": "X"},
        )
        assert r.status_code == 403


def test_einweisung_alte_version_403():
    app, deps = _app_with_version(version_id="ver-neu")
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        profil = Berechtigungsprofil.anlegen(
            bezeichnung="P", produktdefinition_ids={"pd-1"}
        )
        deps.profile_repo.save(profil)
        deps.profile_repo.benutzer_zuordnen(
            profil_id=profil.profil_id, benutzer_id=me["benutzer_id"]
        )
        deps.einweisung_repo.save(
            Einweisungsnachweis.anlegen(
                benutzer_id=me["benutzer_id"],
                version_id="ver-alt",
                eingewiesen_durch="admin",
            )
        )
        r = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "1234567890", "pruefobjekt_kennung": "X"},
        )
        assert r.status_code == 403


def test_start_mit_qualifikation_201():
    app, _deps = _app_with_version()
    with TestClient(app) as client:
        qualify_client_for_kodierung(client, "1234567890")
        r = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "1234567890", "pruefobjekt_kennung": "X"},
        )
        assert r.status_code == 201


def test_doppelte_gueltige_einweisung_409():
    app, _deps = _app_with_version()
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        body = {
            "benutzer_id": me["benutzer_id"],
            "version_id": "ver-1",
        }
        first = client.post("/identity/einweisungen", json=body)
        assert first.status_code == 201, first.text
        second = client.post("/identity/einweisungen", json=body)
        assert second.status_code == 409
        assert second.json()["code"] == "einweisung_bereits_gueltig"


def test_widerruf_dann_neue_einweisung_erlaubt():
    app, _deps = _app_with_version()
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        first = client.post(
            "/identity/einweisungen",
            json={"benutzer_id": me["benutzer_id"], "version_id": "ver-1"},
        )
        assert first.status_code == 201
        eid = first.json()["einweisung_id"]
        wid = client.post(f"/identity/einweisungen/{eid}/widerrufen")
        assert wid.status_code == 200
        assert wid.json()["status"] == "widerrufen"
        second = client.post(
            "/identity/einweisungen",
            json={"benutzer_id": me["benutzer_id"], "version_id": "ver-1"},
        )
        assert second.status_code == 201


def test_abgelaufene_einweisung_start_403():
    app, deps = _app_with_version()
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        profil = Berechtigungsprofil.anlegen(
            bezeichnung="P", produktdefinition_ids={"pd-1"}
        )
        deps.profile_repo.save(profil)
        deps.profile_repo.benutzer_zuordnen(
            profil_id=profil.profil_id, benutzer_id=me["benutzer_id"]
        )
        deps.einweisung_repo.save(
            Einweisungsnachweis.anlegen(
                benutzer_id=me["benutzer_id"],
                version_id="ver-1",
                eingewiesen_durch="admin",
                gueltig_bis=date.today() - timedelta(days=1),
            )
        )
        r = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "1234567890", "pruefobjekt_kennung": "X"},
        )
        assert r.status_code == 403


def test_lauf_fortsetzbar_nach_widerruf():
    app, deps = _app_with_version()
    with TestClient(app) as client:
        qualify_client_for_kodierung(client, "1234567890")
        start = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "1234567890", "pruefobjekt_kennung": "X"},
        )
        assert start.status_code == 201
        pid = start.json()["prueflauf_id"]
        me = client.get("/auth/me").json()
        e = deps.einweisung_repo.get_gueltige(
            benutzer_id=me["benutzer_id"], version_id="ver-1"
        )
        assert e is not None
        deps.einweisung_repo.save(e.widerrufen())
        # Nachweis ohne Re-Qualification
        r = client.post(
            f"/prueflaeufe/{pid}/schritte/s1/nachweise",
            json={"art": "kommentar", "payload": {"text": "ok"}},
        )
        assert r.status_code == 201


def test_fremd_prueflauf_mutation_403():
    app, deps = _app_with_version()
    prueflauf = Prueflauf.starten(
        version_id="ver-1",
        pruefobjekt_kennung="X",
        produktkodierung="1234567890",
        pruefer_id="jemand-anderes",
        prozedur_schritt_ids=["s1"],
    )
    deps.prueflauf_repo.save(prueflauf)
    with TestClient(app) as client:
        r = client.post(
            f"/prueflaeufe/{prueflauf.prueflauf_id}/schritte/s1/nachweise",
            json={"art": "kommentar", "payload": {"text": "x"}},
        )
        assert r.status_code == 403


def test_abgelaufene_einweisung_neue_anlegen_erlaubt():
    app, deps = _app_with_version()
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        deps.einweisung_repo.save(
            Einweisungsnachweis.anlegen(
                benutzer_id=me["benutzer_id"],
                version_id="ver-1",
                eingewiesen_durch="admin",
                gueltig_bis=date.today() - timedelta(days=1),
            )
        )
        r = client.post(
            "/identity/einweisungen",
            json={"benutzer_id": me["benutzer_id"], "version_id": "ver-1"},
        )
        assert r.status_code == 201, r.text
        assert r.json()["status"] == "gueltig"


def test_pruefer_katalog_entwurf_403():
    from domain.identity.benutzer import Benutzer, PasswortHash
    from domain.identity.typen import BenutzerStatus, Systemrolle
    from starlette.testclient import TestClient as RawTestClient

    deps = in_memory_deps(seed_admin=False)
    hasher = deps.passwort_hasher
    deps.benutzer_repo.save(
        Benutzer.anlegen(
            login="nur-pruefer",
            anzeigename="Nur Prüfer",
            passwort_hash=hasher.hash("secret"),
            rollen=frozenset({Systemrolle.PRUEFER}),
            status=BenutzerStatus.AKTIV,
        )
    )
    app = create_app(deps)
    with RawTestClient(app) as client:
        login = client.post("/auth/login", json={"login": "nur-pruefer", "passwort": "secret"})
        assert login.status_code == 200
        headers = {CSRF_HEADER: login.json()["csrf_token"]}
        r = client.post(
            "/katalog/entwuerfe",
            json={
                "produktkodierung": "9999999999",
                "prozedur_schritte": [],
                "sollbestueckung": [],
            },
            headers=headers,
        )
        assert r.status_code == 403
        assert r.json()["code"] == "nicht_berechtigt"


def test_pruefer_publish_403():
    from domain.identity.benutzer import Benutzer, PasswortHash
    from domain.identity.typen import BenutzerStatus, Systemrolle
    from starlette.testclient import TestClient as RawTestClient

    deps = in_memory_deps(seed_admin=False)
    hasher = deps.passwort_hasher
    deps.benutzer_repo.save(
        Benutzer.anlegen(
            login="nur-pruefer",
            anzeigename="Nur Prüfer",
            passwort_hash=hasher.hash("secret"),
            rollen=frozenset({Systemrolle.PRUEFER}),
            status=BenutzerStatus.AKTIV,
        )
    )
    app = create_app(deps)
    with RawTestClient(app) as client:
        login = client.post("/auth/login", json={"login": "nur-pruefer", "passwort": "secret"})
        assert login.status_code == 200
        headers = {CSRF_HEADER: login.json()["csrf_token"]}
        r = client.post(
            "/katalog/entwuerfe/pd-x/veroeffentlichen",
            json={},
            headers=headers,
        )
        assert r.status_code == 403
        assert r.json()["code"] == "nicht_berechtigt"
