"""SQLAlchemy-ORM-Schema — nur im Adapter, nicht in der Domain."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, engine
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


class ProtokollSnapshotRow(Base):
    __tablename__ = "protokoll_snapshot"

    snapshot_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prueflauf_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


def init_schema(db_engine: engine.Engine) -> None:
    Base.metadata.create_all(db_engine)
