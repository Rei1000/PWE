"""API-Tests — V1 Operational Polish A (Discovery Reads)."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient
from starlette.testclient import TestClient as RawTestClient

from adapters.persistence.in_memory import InMemoryKatalogRepository
from api.app import create_app
from api.auth_settings import CSRF_HEADER
from api.deps import in_memory_deps
from domain.identity.benutzer import Benutzer
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import Einweisungsnachweis
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from tests.support.qualification import qualify_client_for_kodierung


def _login(client, login: str, passwort: str) -> dict[str, str]:
    r = client.post("/auth/login", json={"login": login, "passwort": passwort})
    assert r.status_code == 200, r.text
    return {CSRF_HEADER: r.json()["csrf_token"]}


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


def test_benutzer_detail_profil_ids_leer():
    app = create_app(in_memory_deps())
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        r = client.get(f"/identity/benutzer/{me['benutzer_id']}")
        assert r.status_code == 200
        assert r.json()["profil_ids"] == []


def test_benutzer_detail_profil_ids_nach_zuordnung():
    deps = in_memory_deps()
    app = create_app(deps)
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        profil = Berechtigungsprofil.anlegen(
            bezeichnung="P", produktdefinition_ids={"pd-1"}
        )
        deps.profile_repo.save(profil)
        deps.profile_repo.benutzer_zuordnen(
            profil_id=profil.profil_id, benutzer_id=me["benutzer_id"]
        )
        r = client.get(f"/identity/benutzer/{me['benutzer_id']}")
        assert r.status_code == 200
        assert r.json()["profil_ids"] == [profil.profil_id]


def test_benutzer_detail_profil_ids_nach_entfernen():
    deps = in_memory_deps()
    app = create_app(deps)
    with TestClient(app) as client:
        me = client.get("/auth/me").json()
        profil = Berechtigungsprofil.anlegen(
            bezeichnung="P", produktdefinition_ids={"pd-1"}
        )
        deps.profile_repo.save(profil)
        deps.profile_repo.benutzer_zuordnen(
            profil_id=profil.profil_id, benutzer_id=me["benutzer_id"]
        )
        deps.profile_repo.benutzer_entfernen(
            profil_id=profil.profil_id, benutzer_id=me["benutzer_id"]
        )
        r = client.get(f"/identity/benutzer/{me['benutzer_id']}")
        assert r.json()["profil_ids"] == []


def test_pruefer_darf_benutzer_detail_nicht_lesen():
    deps = in_memory_deps(seed_admin=False)
    hasher = deps.passwort_hasher
    pruefer = Benutzer.anlegen(
        login="nur-p",
        anzeigename="P",
        passwort_hash=hasher.hash("secret"),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
    )
    deps.benutzer_repo.save(pruefer)
    app = create_app(deps)
    with RawTestClient(app) as client:
        headers = _login(client, "nur-p", "secret")
        r = client.get(f"/identity/benutzer/{pruefer.benutzer_id}", headers=headers)
        assert r.status_code == 403


def test_aktive_produkte_leer_ohne_publish():
    app = create_app(in_memory_deps())
    with TestClient(app) as client:
        r = client.get("/katalog/aktive-produkte")
        assert r.status_code == 200
        assert r.json()["produkte"] == []


def test_aktive_produkte_nach_publish():
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(_version())
    app = create_app(deps)
    with TestClient(app) as client:
        r = client.get("/katalog/aktive-produkte")
        assert r.status_code == 200
        produkte = r.json()["produkte"]
        assert len(produkte) == 1
        assert produkte[0]["produktkodierung"] == "1234567890"
        assert produkte[0]["produktdefinition_id"] == "pd-1"
        assert produkte[0]["version_id"] == "ver-1"


def test_pruefer_darf_aktive_produkte_nicht_lesen():
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
        r = client.get("/katalog/aktive-produkte", headers=headers)
        assert r.status_code == 403


def test_startbare_pruefungen_qualifiziert():
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(_version())
    app = create_app(deps)
    with TestClient(app) as client:
        qualify_client_for_kodierung(client, "1234567890")
        r = client.get("/prueflaeufe/startbar")
        assert r.status_code == 200
        assert r.json()["pruefungen"] == [{"produktkodierung": "1234567890"}]


def test_startbare_pruefungen_leer_ohne_qualifikation():
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(_version())
    app = create_app(deps)
    with TestClient(app) as client:
        r = client.get("/prueflaeufe/startbar")
        assert r.status_code == 200
        assert r.json()["pruefungen"] == []


def test_startbare_manipulation_post_bleibt_403():
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(_version())
    app = create_app(deps)
    with TestClient(app) as client:
        assert client.get("/prueflaeufe/startbar").json()["pruefungen"] == []
        r = client.post(
            "/prueflaeufe",
            json={"produktkodierung": "1234567890", "pruefobjekt_kennung": "X"},
        )
        assert r.status_code == 403
        assert r.json()["code"] == "qualifikation_unzureichend"


def test_startbare_abgelaufene_einweisung():
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(_version())
    app = create_app(deps)
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
        r = client.get("/prueflaeufe/startbar")
        assert r.json()["pruefungen"] == []
