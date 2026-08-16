"""Initial schema — Ist-Zustand aus adapters.persistence.postgresql.schema (Gate 7.5a).

Keine fachlichen Schemaänderungen. Downgrade entfernt nur diese Initialstruktur.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "externes_kommando",
        sa.Column("kommando_id", sa.String(length=36), nullable=False),
        sa.Column("bezeichnung", sa.String(length=128), nullable=False),
        sa.Column("kommandocode", sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint("kommando_id"),
    )
    op.create_table(
        "produktdefinition_entwurf",
        sa.Column("produktdefinition_id", sa.String(length=36), nullable=False),
        sa.Column("produktkodierung", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("produktdefinition_id"),
    )
    op.create_index(
        op.f("ix_produktdefinition_entwurf_produktkodierung"),
        "produktdefinition_entwurf",
        ["produktkodierung"],
        unique=False,
    )
    op.create_table(
        "produktdefinitions_version",
        sa.Column("version_id", sa.String(length=36), nullable=False),
        sa.Column("produktdefinition_id", sa.String(length=36), nullable=False),
        sa.Column("produktkodierung", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("version_id"),
    )
    op.create_index(
        op.f("ix_produktdefinitions_version_produktdefinition_id"),
        "produktdefinitions_version",
        ["produktdefinition_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_produktdefinitions_version_produktkodierung"),
        "produktdefinitions_version",
        ["produktkodierung"],
        unique=False,
    )
    op.create_table(
        "protokoll_snapshot",
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("prueflauf_id", sa.String(length=36), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("snapshot_id"),
    )
    op.create_index(
        op.f("ix_protokoll_snapshot_prueflauf_id"),
        "protokoll_snapshot",
        ["prueflauf_id"],
        unique=True,
    )
    op.create_table(
        "prueflauf",
        sa.Column("prueflauf_id", sa.String(length=36), nullable=False),
        sa.Column("version_id", sa.String(length=36), nullable=False),
        sa.Column("produktkodierung", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("prueflauf_id"),
    )
    op.create_index(
        op.f("ix_prueflauf_produktkodierung"),
        "prueflauf",
        ["produktkodierung"],
        unique=False,
    )
    op.create_index(
        op.f("ix_prueflauf_version_id"),
        "prueflauf",
        ["version_id"],
        unique=False,
    )
    op.create_table(
        "routine",
        sa.Column("routine_id", sa.String(length=36), nullable=False),
        sa.Column("bezeichnung", sa.String(length=128), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("routine_id"),
    )
    op.create_table(
        "aktive_version",
        sa.Column("produktkodierung", sa.String(length=64), nullable=False),
        sa.Column("version_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["version_id"],
            ["produktdefinitions_version.version_id"],
        ),
        sa.PrimaryKeyConstraint("produktkodierung"),
    )


def downgrade() -> None:
    op.drop_table("aktive_version")
    op.drop_table("routine")
    op.drop_index(op.f("ix_prueflauf_version_id"), table_name="prueflauf")
    op.drop_index(op.f("ix_prueflauf_produktkodierung"), table_name="prueflauf")
    op.drop_table("prueflauf")
    op.drop_index(op.f("ix_protokoll_snapshot_prueflauf_id"), table_name="protokoll_snapshot")
    op.drop_table("protokoll_snapshot")
    op.drop_index(
        op.f("ix_produktdefinitions_version_produktkodierung"),
        table_name="produktdefinitions_version",
    )
    op.drop_index(
        op.f("ix_produktdefinitions_version_produktdefinition_id"),
        table_name="produktdefinitions_version",
    )
    op.drop_table("produktdefinitions_version")
    op.drop_index(
        op.f("ix_produktdefinition_entwurf_produktkodierung"),
        table_name="produktdefinition_entwurf",
    )
    op.drop_table("produktdefinition_entwurf")
    op.drop_table("externes_kommando")
