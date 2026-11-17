"""Add source-backed technology catalogue metadata."""

from pathlib import Path
from alembic import op
from migrations.sql_file import execute_sql_file

revision = "0008_technology_catalog"
down_revision = "0007_grocery_workflows"
branch_labels = None
depends_on = None


def upgrade():
    execute_sql_file(
        Path(__file__).resolve().parents[1] / "sql/0008_technology_catalog.sql"
    )


def downgrade():
    op.drop_index(
        "ix_technology_catalog_identities_group_code",
        table_name="technology_catalog_identities",
    )
    op.drop_table("technology_catalog_identities")
    op.drop_table("technology_groups")
