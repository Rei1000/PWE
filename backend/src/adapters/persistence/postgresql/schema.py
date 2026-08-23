"""SQLAlchemy-ORM-Schema — nur im Adapter, nicht in der Domain.

PostgreSQL-Schemaänderungen erfolgen ausschließlich über Alembic-Migrationen.
Die FastAPI-Runtime erzeugt oder verändert kein Datenbankschema (Gate 7.5b).
"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ProduktdefinitionEntwurfRow(Base):
    __tablename__ = "produktdefinition_entwurf"

    produktdefinition_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    produktkodierung: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class ProduktdefinitionsVersionRow(Base):
    __tablename__ = "produktdefinitions_version"

    version_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    produktdefinition_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    produktkodierung: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class AktiveVersionRow(Base):
    __tablename__ = "aktive_version"

    produktkodierung: Mapped[str] = mapped_column(String(64), primary_key=True)
    version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("produktdefinitions_version.version_id"),
        nullable=False,
    )


class PrueflaufRow(Base):
    __tablename__ = "prueflauf"

    prueflauf_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    produktkodierung: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class ExternesKommandoRow(Base):
    __tablename__ = "externes_kommando"

    kommando_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bezeichnung: Mapped[str] = mapped_column(String(128), nullable=False)
    kommandocode: Mapped[str] = mapped_column(String(256), nullable=False)


class RoutineRow(Base):
    __tablename__ = "routine"

    routine_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bezeichnung: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class PruefschrittVorlageRow(Base):
    __tablename__ = "pruefschritt_vorlage"

    vorlage_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bezeichnung: Mapped[str] = mapped_column(String(128), nullable=False)
    beschreibung: Mapped[str | None] = mapped_column(String(512), nullable=True)


class ProtokollSnapshotRow(Base):
    __tablename__ = "protokoll_snapshot"

    snapshot_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prueflauf_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class BenutzerRow(Base):
    __tablename__ = "benutzer"

    benutzer_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    login: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    anzeigename: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    passwort_hash: Mapped[str] = mapped_column(Text, nullable=False)
    rollen_json: Mapped[str] = mapped_column(Text, nullable=False)
    passwortwechsel_erforderlich: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )


class IdentitySessionRow(Base):
    __tablename__ = "identity_session"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    benutzer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    csrf_token: Mapped[str] = mapped_column(String(128), nullable=False)
    erzeugt_am: Mapped[str] = mapped_column(String(64), nullable=False)
    zuletzt_gesehen_am: Mapped[str] = mapped_column(String(64), nullable=False)


class BerechtigungsprofilRow(Base):
    __tablename__ = "berechtigungsprofil"

    profil_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bezeichnung: Mapped[str] = mapped_column(String(256), nullable=False)
    beschreibung: Mapped[str | None] = mapped_column(String(512), nullable=True)
    aktiv: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class IdentityAuditRow(Base):
    __tablename__ = "identity_audit"

    audit_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    akteur_benutzer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    ziel_benutzer_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    aktion: Mapped[str] = mapped_column(String(64), nullable=False)
    zeitpunkt: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    referenz_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details_json: Mapped[str] = mapped_column(Text, nullable=False)


class ProfilProduktdefinitionRow(Base):
    __tablename__ = "profil_produktdefinition"

    profil_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    produktdefinition_id: Mapped[str] = mapped_column(String(36), primary_key=True)


class BenutzerProfilRow(Base):
    __tablename__ = "benutzer_profil"

    benutzer_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    profil_id: Mapped[str] = mapped_column(String(36), primary_key=True)


class EinweisungsnachweisRow(Base):
    __tablename__ = "einweisungsnachweis"
    __table_args__ = (
        Index("ix_einweisungsnachweis_benutzer_id", "benutzer_id"),
        Index("ix_einweisungsnachweis_version_id", "version_id"),
        Index("ix_einweisungsnachweis_benutzer_version", "benutzer_id", "version_id"),
        Index(
            "uq_einweisung_gueltig_benutzer_version",
            "benutzer_id",
            "version_id",
            unique=True,
            postgresql_where=text("status = 'gueltig'"),
        ),
    )

    einweisung_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    benutzer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    eingewiesen_durch: Mapped[str] = mapped_column(String(36), nullable=False)
    datum: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    gueltig_bis: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bemerkung: Mapped[str | None] = mapped_column(String(512), nullable=True)
    herkunft_einweisung_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    uebernommen_bei_publish: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
