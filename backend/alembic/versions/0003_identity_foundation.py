"""Identity-Tabellen — Benutzer und Session (Gate 8.1a)."""

from alembic import op
import sqlalchemy as sa

revision = "0003_identity_foundation"
down_revision = "0002_pruefschritt_vorlage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "benutzer",
        sa.Column("benutzer_id", sa.String(length=36), primary_key=True),
        sa.Column("login", sa.String(length=128), nullable=False),
        sa.Column("anzeigename", sa.String(length=256), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("passwort_hash", sa.Text(), nullable=False),
        sa.Column("rollen_json", sa.Text(), nullable=False),
    )
    op.create_index("ix_benutzer_login", "benutzer", ["login"], unique=True)

    op.create_table(
        "identity_session",
        sa.Column("session_id", sa.String(length=36), primary_key=True),
        sa.Column("benutzer_id", sa.String(length=36), nullable=False),
        sa.Column("csrf_token", sa.String(length=128), nullable=False),
        sa.Column("erzeugt_am", sa.String(length=64), nullable=False),
        sa.Column("zuletzt_gesehen_am", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_identity_session_benutzer_id", "identity_session", ["benutzer_id"])


def downgrade() -> None:
    op.drop_index("ix_identity_session_benutzer_id", table_name="identity_session")
    op.drop_table("identity_session")
    op.drop_index("ix_benutzer_login", table_name="benutzer")
    op.drop_table("benutzer")
