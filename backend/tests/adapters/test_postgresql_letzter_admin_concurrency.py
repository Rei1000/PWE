"""PostgreSQL — Letzter-Admin Concurrency (Gate 8.1c1)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from sqlalchemy.orm import sessionmaker

from adapters.persistence.postgresql.audit_repository import PostgresIdentityAuditRepository
from adapters.persistence.postgresql.identity_repository import (
    PostgresBenutzerRepository,
    PostgresSessionStore,
)
from adapters.security.argon2_hasher import Argon2PasswortHasher
from application.identity.benutzer_verwaltung import BenutzerSperren
from domain.identity.benutzer import Benutzer
from domain.identity.letzter_administrator import LetzterAdministratorVerletzt
from domain.identity.typen import BenutzerStatus, Systemrolle

pytestmark = pytest.mark.postgresql


def _seed_zwei_admins(session) -> tuple[str, str]:
    hasher = Argon2PasswortHasher()
    repo = PostgresBenutzerRepository(session)
    a1 = Benutzer.anlegen(
        login="conc-admin-1",
        anzeigename="A1",
        passwort_hash=hasher.hash("x"),
        rollen=frozenset({Systemrolle.ADMINISTRATOR}),
        status=BenutzerStatus.AKTIV,
        benutzer_id="conc-a1",
    )
    a2 = Benutzer.anlegen(
        login="conc-admin-2",
        anzeigename="A2",
        passwort_hash=hasher.hash("x"),
        rollen=frozenset({Systemrolle.ADMINISTRATOR}),
        status=BenutzerStatus.AKTIV,
        benutzer_id="conc-a2",
    )
    repo.save(a1)
    repo.save(a2)
    session.commit()
    return a1.benutzer_id, a2.benutzer_id


def test_parallele_sperrung_letzter_zwei_admins_eine_gewinnt(pg_engine):
    """Zwei parallele Transaktionen sperren je einen der beiden letzten Admins.

    Mit Advisory-Lock darf nur eine Mutation committen; danach bleibt ≥1 aktiver Admin.
    """
    factory = sessionmaker(bind=pg_engine, expire_on_commit=False)
    setup = factory()
    try:
        id1, id2 = _seed_zwei_admins(setup)
    finally:
        setup.close()

    barrier = __import__("threading").Barrier(2)
    ergebnisse: list[str] = []

    def _sperre(ziel_id: str) -> str:
        session = factory()
        try:
            barrier.wait(timeout=10)
            uc = BenutzerSperren(
                PostgresBenutzerRepository(session),
                PostgresSessionStore(session),
                PostgresIdentityAuditRepository(session),
            )
            try:
                uc.execute(akteur_id="test", benutzer_id=ziel_id)
                session.commit()
                return "ok"
            except LetzterAdministratorVerletzt:
                session.rollback()
                return "conflict"
            except Exception:
                session.rollback()
                raise
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(_sperre, id1), pool.submit(_sperre, id2)]
        for f in as_completed(futures):
            ergebnisse.append(f.result())

    assert sorted(ergebnisse) == ["conflict", "ok"]

    verify = factory()
    try:
        alle = PostgresBenutzerRepository(verify).list_all()
        aktive_admins = [b for b in alle if b.ist_aktiver_administrator()]
        assert len(aktive_admins) >= 1
        assert {b.benutzer_id for b in aktive_admins} <= {id1, id2}
    finally:
        verify.close()
