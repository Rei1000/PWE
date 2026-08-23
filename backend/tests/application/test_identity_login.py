"""Application-Tests — Login (Gate 8.1a)."""

import pytest

from adapters.persistence.in_memory_identity import InMemoryBenutzerRepository, InMemorySessionStore
from adapters.security.argon2_hasher import Argon2PasswortHasher
from application.identity.login import Login, UngueltigeAnmeldedaten
from application.identity.logout import Logout
from domain.identity.benutzer import Benutzer
from domain.identity.typen import BenutzerStatus, Systemrolle


@pytest.fixture
def login_uc():
    repo = InMemoryBenutzerRepository()
    hasher = Argon2PasswortHasher()
    sessions = InMemorySessionStore()
    repo.save(
        Benutzer.anlegen(
            login="alice",
            anzeigename="Alice",
            passwort_hash=hasher.hash("secret"),
            rollen=frozenset({Systemrolle.PRUEFER}),
            status=BenutzerStatus.AKTIV,
        )
    )
    return Login(repo, hasher, sessions), sessions, repo


def test_login_erfolg(login_uc):
    uc, sessions, _ = login_uc
    ergebnis = uc.execute(login="alice", passwort="secret")
    assert sessions.laden(ergebnis.session_id) is not None
    assert ergebnis.benutzer.login == "alice"


def test_login_falsches_passwort(login_uc):
    uc, _, _ = login_uc
    with pytest.raises(UngueltigeAnmeldedaten):
        uc.execute(login="alice", passwort="nope")


def test_logout_loescht_session(login_uc):
    uc, sessions, _ = login_uc
    ergebnis = uc.execute(login="alice", passwort="secret")
    Logout(sessions).execute(session_id=ergebnis.session_id)
    assert sessions.laden(ergebnis.session_id) is None
