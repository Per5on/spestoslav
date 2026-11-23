"""Add a canonical locality cross-reference for the NSI register."""

from pathlib import Path

from alembic import op

from migrations.sql_file import execute_sql_file

revision = "0009_locality_ekatte"
down_revision = "0008_technology_catalog"
branch_labels = None
depends_on = None


def upgrade():
    execute_sql_file(Path(__file__).resolve().parents[1] / "sql/0009_locality_ekatte.sql")


def downgrade():
    op.drop_table("locality_ekatte")
