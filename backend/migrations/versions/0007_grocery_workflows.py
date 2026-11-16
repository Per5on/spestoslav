"""Classified source-backed grocery identities and retry-safe receipt uploads."""

from pathlib import Path
from alembic import op
from migrations.sql_file import execute_sql_file

revision = "0007_grocery_workflows"
down_revision = "0006_remove_home_postal"
branch_labels = None
depends_on = None


def upgrade():
    sql = Path(__file__).resolve().parents[1] / "sql" / "0007_grocery_workflows.sql"
    execute_sql_file(sql)


def downgrade():
    op.drop_index("uq_receipt_upload_request", table_name="receipt_jobs")
    op.drop_column("receipt_jobs", "request_key")
    op.drop_column("receipt_jobs", "upload_fingerprint")
    op.drop_index(
        "ix_grocery_catalog_identities_group_code",
        table_name="grocery_catalog_identities",
    )
    op.drop_table("grocery_catalog_identities")
    op.drop_table("grocery_groups")
