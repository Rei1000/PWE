"""Identity Administration — Force-Change, Profil aktiv, Audit (Gate 8.1c1)."""

from alembic import op
import sqlalchemy as sa

revision = "0005_identity_admin"
down_revision = "0004_qualification_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "benutzer",
        sa.Column(
            "passwortwechsel_erforderlich",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "berechtigungsprofil",
        sa.Column(
            "aktiv",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_table(
        "identity_audit",
        sa.Column("audit_id", sa.String(length=36), primary_key=True),
        sa.Column("akteur_benutzer_id", sa.String(length=36), nullable=False),
        sa.Column("ziel_benutzer_id", sa.String(length=36), nullable=True),
        sa.Column("aktion", sa.String(length=64), nullable=False),
        sa.Column("zeitpunkt", sa.String(length=64), nullable=False),
        sa.Column("referenz_id", sa.String(length=36), nullable=True),
        sa.Column("details_json", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_identity_audit_akteur_benutzer_id", "identity_audit", ["akteur_benutzer_id"]
    )
    op.create_index("ix_identity_audit_zeitpunkt", "identity_audit", ["zeitpunkt"])


def downgrade() -> None:
    op.drop_index("ix_identity_audit_zeitpunkt", table_name="identity_audit")
    op.drop_index("ix_identity_audit_akteur_benutzer_id", table_name="identity_audit")
    op.drop_table("identity_audit")
    op.drop_column("berechtigungsprofil", "aktiv")
    op.drop_column("benutzer", "passwortwechsel_erforderlich")
