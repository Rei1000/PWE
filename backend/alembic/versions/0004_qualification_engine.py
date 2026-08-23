"""Qualification Engine — Profile und Einweisungsnachweise (Gate 8.1b)."""

from alembic import op
import sqlalchemy as sa

revision = "0004_qualification_engine"
down_revision = "0003_identity_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "berechtigungsprofil",
        sa.Column("profil_id", sa.String(length=36), primary_key=True),
        sa.Column("bezeichnung", sa.String(length=256), nullable=False),
        sa.Column("beschreibung", sa.String(length=512), nullable=True),
    )

    op.create_table(
        "profil_produktdefinition",
        sa.Column("profil_id", sa.String(length=36), primary_key=True),
        sa.Column("produktdefinition_id", sa.String(length=36), primary_key=True),
    )

    op.create_table(
        "benutzer_profil",
        sa.Column("benutzer_id", sa.String(length=36), primary_key=True),
        sa.Column("profil_id", sa.String(length=36), primary_key=True),
    )

    op.create_table(
        "einweisungsnachweis",
        sa.Column("einweisung_id", sa.String(length=36), primary_key=True),
        sa.Column("benutzer_id", sa.String(length=36), nullable=False),
        sa.Column("version_id", sa.String(length=36), nullable=False),
        sa.Column("eingewiesen_durch", sa.String(length=36), nullable=False),
        sa.Column("datum", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gueltig_bis", sa.String(length=32), nullable=True),
        sa.Column("bemerkung", sa.String(length=512), nullable=True),
        sa.Column("herkunft_einweisung_id", sa.String(length=36), nullable=True),
        sa.Column("uebernommen_bei_publish", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(
        "ix_einweisungsnachweis_benutzer_id", "einweisungsnachweis", ["benutzer_id"]
    )
    op.create_index(
        "ix_einweisungsnachweis_version_id", "einweisungsnachweis", ["version_id"]
    )
    op.create_index(
        "ix_einweisungsnachweis_benutzer_version",
        "einweisungsnachweis",
        ["benutzer_id", "version_id"],
    )
    op.create_index(
        "uq_einweisung_gueltig_benutzer_version",
        "einweisungsnachweis",
        ["benutzer_id", "version_id"],
        unique=True,
        postgresql_where=sa.text("status = 'gueltig'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_einweisung_gueltig_benutzer_version",
        table_name="einweisungsnachweis",
        postgresql_where=sa.text("status = 'gueltig'"),
    )
    op.drop_index("ix_einweisungsnachweis_benutzer_version", table_name="einweisungsnachweis")
    op.drop_index("ix_einweisungsnachweis_version_id", table_name="einweisungsnachweis")
    op.drop_index("ix_einweisungsnachweis_benutzer_id", table_name="einweisungsnachweis")
    op.drop_table("einweisungsnachweis")
    op.drop_table("benutzer_profil")
    op.drop_table("profil_produktdefinition")
    op.drop_table("berechtigungsprofil")
