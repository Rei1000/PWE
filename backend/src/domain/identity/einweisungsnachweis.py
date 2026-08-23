"""Identity — Aggregate Einweisungsnachweis (Gate 8.1b, ADR-0026)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import uuid4

from domain.identity.typen import EinweisungsStatus
from domain.shared.errors import DomainError, InvariantViolation


class EinweisungNichtGueltig(DomainError):
    """Einweisung ist widerrufen, abgelaufen oder sonst ungültig."""


class EinweisungBereitsGueltig(DomainError):
    """Es existiert bereits eine gültige Einweisung für (Benutzer, Version)."""


@dataclass(frozen=True)
class Einweisungsnachweis:
    """Aggregate Root — Qualifikation Benutzer × ProduktdefinitionsVersion."""

    einweisung_id: str
    benutzer_id: str
    version_id: str
    eingewiesen_durch: str
    datum: datetime
    status: EinweisungsStatus
    gueltig_bis: date | None = None
    bemerkung: str | None = None
    herkunft_einweisung_id: str | None = None
    uebernommen_bei_publish: bool = False

    @classmethod
    def anlegen(
        cls,
        *,
        benutzer_id: str,
        version_id: str,
        eingewiesen_durch: str,
        datum: datetime | None = None,
        gueltig_bis: date | None = None,
        bemerkung: str | None = None,
        herkunft_einweisung_id: str | None = None,
        uebernommen_bei_publish: bool = False,
        einweisung_id: str | None = None,
        status: EinweisungsStatus = EinweisungsStatus.GUELTIG,
    ) -> Einweisungsnachweis:
        bid = benutzer_id.strip()
        vid = version_id.strip()
        durch = eingewiesen_durch.strip()
        if not bid:
            raise InvariantViolation("benutzer_id darf nicht leer sein")
        if not vid:
            raise InvariantViolation("version_id darf nicht leer sein")
        if not durch:
            raise InvariantViolation("eingewiesen_durch darf nicht leer sein")
        return cls(
            einweisung_id=einweisung_id or str(uuid4()),
            benutzer_id=bid,
            version_id=vid,
            eingewiesen_durch=durch,
            datum=datum or datetime.now(UTC),
            status=status,
            gueltig_bis=gueltig_bis,
            bemerkung=bemerkung.strip() if bemerkung and bemerkung.strip() else None,
            herkunft_einweisung_id=herkunft_einweisung_id,
            uebernommen_bei_publish=uebernommen_bei_publish,
        )

    def ist_gueltig(self, *, jetzt: datetime | None = None) -> bool:
        if self.status != EinweisungsStatus.GUELTIG:
            return False
        if self.gueltig_bis is None:
            return True
        ref = jetzt or datetime.now(UTC)
        heute = ref.date() if isinstance(ref, datetime) else ref
        return self.gueltig_bis >= heute

    def assert_gueltig(self, *, jetzt: datetime | None = None) -> None:
        if not self.ist_gueltig(jetzt=jetzt):
            raise EinweisungNichtGueltig("Einweisung ist nicht gültig")

    def widerrufen(self) -> Einweisungsnachweis:
        if self.status == EinweisungsStatus.WIDERRUFEN:
            return self
        return Einweisungsnachweis(
            einweisung_id=self.einweisung_id,
            benutzer_id=self.benutzer_id,
            version_id=self.version_id,
            eingewiesen_durch=self.eingewiesen_durch,
            datum=self.datum,
            status=EinweisungsStatus.WIDERRUFEN,
            gueltig_bis=self.gueltig_bis,
            bemerkung=self.bemerkung,
            herkunft_einweisung_id=self.herkunft_einweisung_id,
            uebernommen_bei_publish=self.uebernommen_bei_publish,
        )

    def als_abgelaufen(self) -> Einweisungsnachweis:
        return Einweisungsnachweis(
            einweisung_id=self.einweisung_id,
            benutzer_id=self.benutzer_id,
            version_id=self.version_id,
            eingewiesen_durch=self.eingewiesen_durch,
            datum=self.datum,
            status=EinweisungsStatus.ABGELAUFEN,
            gueltig_bis=self.gueltig_bis,
            bemerkung=self.bemerkung,
            herkunft_einweisung_id=self.herkunft_einweisung_id,
            uebernommen_bei_publish=self.uebernommen_bei_publish,
        )

    def uebernehmen_auf_version(
        self,
        *,
        neue_version_id: str,
        eingewiesen_durch: str,
        datum: datetime,
    ) -> Einweisungsnachweis:
        """Publish-Übernahme: neuer Nachweis für V_neu, Herkunft gesetzt."""
        return Einweisungsnachweis.anlegen(
            benutzer_id=self.benutzer_id,
            version_id=neue_version_id,
            eingewiesen_durch=eingewiesen_durch,
            datum=datum,
            gueltig_bis=self.gueltig_bis,
            bemerkung=f"Übernommen von Version {self.version_id}",
            herkunft_einweisung_id=self.einweisung_id,
            uebernommen_bei_publish=True,
            status=EinweisungsStatus.GUELTIG,
        )
