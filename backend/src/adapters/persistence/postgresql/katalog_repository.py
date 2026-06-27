"""PostgreSQL-Implementierung — KatalogRepository."""

from __future__ import annotations

from sqlalchemy.orm import Session

from adapters.persistence.postgresql.mapping import (
    entwurf_from_payload,
    entwurf_to_payload,
    version_from_payload,
    version_to_payload,
)
from adapters.persistence.postgresql.schema import (
    AktiveVersionRow,
    ProduktdefinitionEntwurfRow,
    ProduktdefinitionsVersionRow,
)
from domain.katalog.produktdefinition import Produktdefinition
from domain.katalog.version import ProduktdefinitionsVersion


class PostgresKatalogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_aktive_version_fuer_kodierung(
        self, produktkodierung: str
    ) -> ProduktdefinitionsVersion | None:
        aktiv = self._session.get(AktiveVersionRow, produktkodierung)
        if aktiv is None:
            return None
        return self.get_version(aktiv.version_id)

    def get_version(self, version_id: str) -> ProduktdefinitionsVersion | None:
        row = self._session.get(ProduktdefinitionsVersionRow, version_id)
        if row is None:
            return None
        return version_from_payload(row.payload)

    def save_version(self, version: ProduktdefinitionsVersion) -> None:
        existing = self._session.get(ProduktdefinitionsVersionRow, version.version_id)
        if existing is None:
            self._session.add(
                ProduktdefinitionsVersionRow(
                    version_id=version.version_id,
                    produktdefinition_id=version.produktdefinition_id,
                    produktkodierung=version.produktkodierung,
                    payload=version_to_payload(version),
                )
            )

        aktiv = self._session.get(AktiveVersionRow, version.produktkodierung)
        if aktiv is None:
            self._session.add(
                AktiveVersionRow(
                    produktkodierung=version.produktkodierung,
                    version_id=version.version_id,
                )
            )
        else:
            aktiv.version_id = version.version_id

        self._session.commit()

    def get_entwurf(self, produktdefinition_id: str) -> Produktdefinition | None:
        row = self._session.get(ProduktdefinitionEntwurfRow, produktdefinition_id)
        if row is None:
            return None
        return entwurf_from_payload(row.payload)

    def save_entwurf(self, entwurf: Produktdefinition) -> None:
        row = self._session.get(ProduktdefinitionEntwurfRow, entwurf.produktdefinition_id)
        payload = entwurf_to_payload(entwurf)
        if row is None:
            self._session.add(
                ProduktdefinitionEntwurfRow(
                    produktdefinition_id=entwurf.produktdefinition_id,
                    produktkodierung=entwurf.produktkodierung,
                    payload=payload,
                )
            )
        else:
            row.produktkodierung = entwurf.produktkodierung
            row.payload = payload
        self._session.commit()
