"""Barcode identification, product media, national online scope and freshness."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_catalog_and_freshness"
down_revision = "0004_review_workflows"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "current_prices", sa.Column("observed_at", sa.DateTime(timezone=True))
    )
    op.create_table(
        "product_identification_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_subject", sa.String(200), nullable=False),
        sa.Column("barcode", sa.String(64), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id")
        ),
        sa.Column("reviewed_by", sa.String(200)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "owner_subject", "barcode", name="uq_identification_owner_barcode"
        ),
    )
    op.create_table(
        "product_images",
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            primary_key=True,
        ),
        sa.Column("image_url", sa.String(1000), nullable=False),
        sa.Column("source_url", sa.String(1000), nullable=False),
    )
    op.create_table(
        "national_offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column(
            "retailer_code",
            sa.String(64),
            sa.ForeignKey("catalog_retailers.code"),
            nullable=False,
        ),
        sa.Column("price_eur", sa.Numeric(12, 4), nullable=False),
        sa.Column("source_reference", sa.String(1000), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_by", sa.String(200), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_national_offer_product_retailer",
        "national_offers",
        ["product_id", "retailer_code", "observed_at"],
    )


def downgrade():
    op.drop_table("national_offers")
    op.drop_table("product_images")
    op.drop_table("product_identification_requests")
    op.drop_column("current_prices", "observed_at")
