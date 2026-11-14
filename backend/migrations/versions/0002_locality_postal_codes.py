"""Normalize locality postal-code associations."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_locality_postal_codes"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("inhabited_localities", sa.Column("name_latin", sa.String(180), nullable=True))
    op.add_column("inhabited_localities", sa.Column("municipality_code", sa.String(20), nullable=True))
    op.add_column("inhabited_localities", sa.Column("region_code", sa.String(12), nullable=True))
    op.create_table(
        "locality_postal_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("locality_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inhabited_localities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("postal_code", sa.String(12), nullable=False),
        sa.Column("source", sa.String(40), nullable=False, server_default="GEONAMES"),
        sa.UniqueConstraint("locality_id", "postal_code", name="uq_locality_postal_code"),
    )
    op.create_index("ix_locality_postal_code_value", "locality_postal_codes", ["postal_code"])

def downgrade():
    op.drop_index("ix_locality_postal_code_value", table_name="locality_postal_codes")
    op.drop_table("locality_postal_codes")
    op.drop_column("inhabited_localities", "region_code")
    op.drop_column("inhabited_localities", "municipality_code")
    op.drop_column("inhabited_localities", "name_latin")
