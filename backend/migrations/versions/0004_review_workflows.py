"""Authenticated submissions, collection-source approval and receipt ownership."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_review_workflows"
down_revision = "0003_marketplace_core"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "review_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_subject", sa.String(200), nullable=False),
        sa.Column("request_key", sa.String(100), nullable=False),
        sa.Column(
            "cache_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("price_cache.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("reviewed_by", sa.String(200)),
        sa.Column("review_note", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("owner_subject", "request_key", name="uq_review_request"),
    )
    op.create_index(
        "ix_review_owner", "review_submissions", ["owner_subject", "created_at"]
    )
    op.create_table(
        "collection_sources",
        sa.Column("code", sa.String(64), primary_key=True),
        sa.Column(
            "retailer_code",
            sa.String(64),
            sa.ForeignKey("catalog_retailers.code"),
            nullable=False,
        ),
        sa.Column("origin", sa.String(500), nullable=False),
        sa.Column("kind", sa.String(24), nullable=False, server_default="OFFICIAL"),
        sa.Column("enabled", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "receipt_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("receipt_scans.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("owner_subject", sa.String(200), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True)),
        sa.Column("error", sa.String(300)),
    )
    op.create_index("ix_receipt_job_owner", "receipt_jobs", ["owner_subject"])


def downgrade():
    op.drop_table("receipt_jobs")
    op.drop_table("collection_sources")
    op.drop_table("review_submissions")
