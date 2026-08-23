"""PostgreSQL — Qualifikation: Profile + Einweisungen (Gate 8.1b)."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from adapters.persistence.postgresql.schema import (
    BenutzerProfilRow,
    BerechtigungsprofilRow,
    EinweisungsnachweisRow,
    ProfilProduktdefinitionRow,
)
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import Einweisungsnachweis
from domain.identity.typen import EinweisungsStatus


def _profil_to_domain(
    row: BerechtigungsprofilRow, pd_ids: frozenset[str]
) -> Berechtigungsprofil:
    return Berechtigungsprofil(
        profil_id=row.profil_id,
        bezeichnung=row.bezeichnung,
        beschreibung=row.beschreibung,
        produktdefinition_ids=pd_ids,
        aktiv=bool(getattr(row, "aktiv", True)),
    )


def _load_pd_ids(session: Session, profil_id: str) -> frozenset[str]:
    stmt = select(ProfilProduktdefinitionRow.produktdefinition_id).where(
        ProfilProduktdefinitionRow.profil_id == profil_id
    )
    return frozenset(session.scalars(stmt).all())


def _einweisung_to_row(e: Einweisungsnachweis) -> EinweisungsnachweisRow:
    return EinweisungsnachweisRow(
        einweisung_id=e.einweisung_id,
        benutzer_id=e.benutzer_id,
        version_id=e.version_id,
        eingewiesen_durch=e.eingewiesen_durch,
        datum=e.datum.isoformat(),
        status=e.status.value,
        gueltig_bis=e.gueltig_bis.isoformat() if e.gueltig_bis else None,
        bemerkung=e.bemerkung,
        herkunft_einweisung_id=e.herkunft_einweisung_id,
        uebernommen_bei_publish=e.uebernommen_bei_publish,
    )


def _row_to_einweisung(row: EinweisungsnachweisRow) -> Einweisungsnachweis:
    return Einweisungsnachweis(
        einweisung_id=row.einweisung_id,
        benutzer_id=row.benutzer_id,
        version_id=row.version_id,
        eingewiesen_durch=row.eingewiesen_durch,
        datum=datetime.fromisoformat(row.datum),
        status=EinweisungsStatus(row.status),
        gueltig_bis=date.fromisoformat(row.gueltig_bis) if row.gueltig_bis else None,
        bemerkung=row.bemerkung,
        herkunft_einweisung_id=row.herkunft_einweisung_id,
        uebernommen_bei_publish=row.uebernommen_bei_publish,
    )


class PostgresBerechtigungsprofilRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, profil: Berechtigungsprofil) -> None:
        existing = self._session.get(BerechtigungsprofilRow, profil.profil_id)
        if existing is None:
            self._session.add(
                BerechtigungsprofilRow(
                    profil_id=profil.profil_id,
                    bezeichnung=profil.bezeichnung,
                    beschreibung=profil.beschreibung,
                    aktiv=profil.aktiv,
                )
            )
        else:
            existing.bezeichnung = profil.bezeichnung
            existing.beschreibung = profil.beschreibung
            existing.aktiv = profil.aktiv
            self._session.execute(
                delete(ProfilProduktdefinitionRow).where(
                    ProfilProduktdefinitionRow.profil_id == profil.profil_id
                )
            )
        for pd_id in profil.produktdefinition_ids:
            self._session.add(
                ProfilProduktdefinitionRow(
                    profil_id=profil.profil_id, produktdefinition_id=pd_id
                )
            )

    def get(self, profil_id: str) -> Berechtigungsprofil | None:
        row = self._session.get(BerechtigungsprofilRow, profil_id)
        if row is None:
            return None
        return _profil_to_domain(row, _load_pd_ids(self._session, profil_id))

    def list_all(self) -> list[Berechtigungsprofil]:
        rows = self._session.scalars(select(BerechtigungsprofilRow)).all()
        return [_profil_to_domain(r, _load_pd_ids(self._session, r.profil_id)) for r in rows]

    def delete(self, profil_id: str) -> None:
        self._session.execute(
            delete(BenutzerProfilRow).where(BenutzerProfilRow.profil_id == profil_id)
        )
        self._session.execute(
            delete(ProfilProduktdefinitionRow).where(
                ProfilProduktdefinitionRow.profil_id == profil_id
            )
        )
        row = self._session.get(BerechtigungsprofilRow, profil_id)
        if row is not None:
            self._session.delete(row)

    def profil_ids_fuer_benutzer(self, benutzer_id: str) -> frozenset[str]:
        stmt = select(BenutzerProfilRow.profil_id).where(
            BenutzerProfilRow.benutzer_id == benutzer_id
        )
        return frozenset(self._session.scalars(stmt).all())

    def benutzer_zuordnen(self, *, profil_id: str, benutzer_id: str) -> None:
        existing = self._session.get(
            BenutzerProfilRow, {"benutzer_id": benutzer_id, "profil_id": profil_id}
        )
        if existing is None:
            self._session.add(
                BenutzerProfilRow(benutzer_id=benutzer_id, profil_id=profil_id)
            )

    def benutzer_entfernen(self, *, profil_id: str, benutzer_id: str) -> None:
        row = self._session.get(
            BenutzerProfilRow, {"benutzer_id": benutzer_id, "profil_id": profil_id}
        )
        if row is not None:
            self._session.delete(row)

    def profile_fuer_benutzer(self, benutzer_id: str) -> list[Berechtigungsprofil]:
        return [
            p
            for pid in self.profil_ids_fuer_benutzer(benutzer_id)
            if (p := self.get(pid)) is not None
        ]


class PostgresEinweisungsnachweisRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, einweisung: Einweisungsnachweis) -> None:
        existing = self._session.get(EinweisungsnachweisRow, einweisung.einweisung_id)
        row = _einweisung_to_row(einweisung)
        if existing is None:
            self._session.add(row)
        else:
            existing.benutzer_id = row.benutzer_id
            existing.version_id = row.version_id
            existing.eingewiesen_durch = row.eingewiesen_durch
            existing.datum = row.datum
            existing.status = row.status
            existing.gueltig_bis = row.gueltig_bis
            existing.bemerkung = row.bemerkung
            existing.herkunft_einweisung_id = row.herkunft_einweisung_id
            existing.uebernommen_bei_publish = row.uebernommen_bei_publish

    def get(self, einweisung_id: str) -> Einweisungsnachweis | None:
        row = self._session.get(EinweisungsnachweisRow, einweisung_id)
        return _row_to_einweisung(row) if row else None

    def get_gueltige(
        self, *, benutzer_id: str, version_id: str
    ) -> Einweisungsnachweis | None:
        stmt = select(EinweisungsnachweisRow).where(
            EinweisungsnachweisRow.benutzer_id == benutzer_id,
            EinweisungsnachweisRow.version_id == version_id,
            EinweisungsnachweisRow.status == EinweisungsStatus.GUELTIG.value,
        )
        row = self._session.scalars(stmt).first()
        if row is None:
            return None
        e = _row_to_einweisung(row)
        if e.ist_gueltig():
            return e
        return None

    def list_gueltige_fuer_version(self, version_id: str) -> list[Einweisungsnachweis]:
        stmt = select(EinweisungsnachweisRow).where(
            EinweisungsnachweisRow.version_id == version_id,
            EinweisungsnachweisRow.status == EinweisungsStatus.GUELTIG.value,
        )
        return [
            e
            for row in self._session.scalars(stmt).all()
            if (e := _row_to_einweisung(row)).ist_gueltig()
        ]

    def list_fuer_benutzer_version(
        self, *, benutzer_id: str, version_id: str
    ) -> list[Einweisungsnachweis]:
        stmt = select(EinweisungsnachweisRow).where(
            EinweisungsnachweisRow.benutzer_id == benutzer_id,
            EinweisungsnachweisRow.version_id == version_id,
        )
        return [_row_to_einweisung(row) for row in self._session.scalars(stmt).all()]

    def list_fuer_benutzer(self, benutzer_id: str) -> list[Einweisungsnachweis]:
        stmt = select(EinweisungsnachweisRow).where(
            EinweisungsnachweisRow.benutzer_id == benutzer_id
        )
        return [_row_to_einweisung(row) for row in self._session.scalars(stmt).all()]
