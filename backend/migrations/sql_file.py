"""Execute a whole PostgreSQL script without splitting SQL string/function bodies."""

from pathlib import Path
from alembic import op


def execute_sql_file(path):
    script = Path(path).read_text(encoding="utf-8").strip()
    if not script:
        return
    context = op.get_context()
    if context.as_sql:
        # Emit exact SQL: SQLAlchemy.text would interpret colon-like text as binds.
        context.impl.static_output(script if script.endswith(";") else script + ";")
    else:
        # No parameters/prepared statement: psycopg uses PostgreSQL's multi-command
        # protocol inside the migration's existing transaction.
        op.get_bind().exec_driver_sql(script, execution_options={"no_parameters": True})
