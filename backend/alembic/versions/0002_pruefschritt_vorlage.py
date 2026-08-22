"""PrüfschrittVorlage-Tabelle (Gate 8.2b1, ADR-0020)."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_pruefschritt_vorlage"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pruefschritt_vorlage",
        sa.Column("vorlage_id", sa.String(length=36), nullable=False),
        sa.Column("bezeichnung", sa.String(length=128), nullable=False),
        sa.Column("beschreibung", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("vorlage_id"),
    )


def downgrade() -> None:
    op.drop_table("pruefschritt_vorlage")
