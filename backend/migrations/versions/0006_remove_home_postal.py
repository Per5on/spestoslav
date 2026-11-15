"""Retire Home-category records and postal search, keeping locality identities."""

from pathlib import Path
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006_remove_home_postal"
down_revision = "0005_catalog_and_freshness"
branch_labels = None
depends_on = None


def upgrade():
    sql = Path(__file__).resolve().parents[1] / "sql" / "0006_remove_home_postal.sql"
    for statement in sql.read_text().split(";"):
        if statement.strip():
            op.execute(statement)


def downgrade():
    # Structure only. Removed data is recoverable from the pre-change Neon branch,
    # not fabricated by a downgrade.
    op.add_column("inhabited_localities", sa.Column("postal_code", sa.String(12)))
    op.create_index(
        "ix_localities_postal_code", "inhabited_localities", ["postal_code"]
    )
    op.add_column("store_branches", sa.Column("postal_code", sa.String(12)))
    op.create_table(
        "locality_postal_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "locality_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inhabited_localities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("postal_code", sa.String(12), nullable=False),
        sa.Column("source", sa.String(40), nullable=False),
        sa.UniqueConstraint(
            "locality_id", "postal_code", name="uq_locality_postal_code"
        ),
    )
    op.create_index(
        "ix_locality_postal_code_value", "locality_postal_codes", ["postal_code"]
    )
