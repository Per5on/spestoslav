"""Add store price, barcode, promotion and receipt foundations."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_marketplace_core"
down_revision = "0002_locality_postal_codes"
branch_labels = None
depends_on = None

def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("store_branches")}
    if "locality_id" not in columns:
        op.add_column("store_branches", sa.Column("locality_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inhabited_localities.id"), nullable=True))
    if "postal_code" not in columns:
        op.add_column("store_branches", sa.Column("postal_code", sa.String(12)))
    if "latitude" not in columns:
        op.add_column("store_branches", sa.Column("latitude", sa.Numeric(9,6)))
    if "longitude" not in columns:
        op.add_column("store_branches", sa.Column("longitude", sa.Numeric(9,6)))
    op.create_table("product_barcodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("barcode", sa.String(64), nullable=False, unique=True),
        sa.Column("source", sa.String(40), nullable=False, server_default="ADMIN"),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_table("current_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("store_branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("price_eur", sa.Numeric(12,4), nullable=False), sa.Column("source", sa.String(40), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("product_id","branch_id",name="uq_current_price_product_branch"),
        sa.CheckConstraint("price_eur > 0",name="ck_current_price_positive"))
    op.create_table("price_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="SET NULL")),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("store_branches.id", ondelete="SET NULL")),
        sa.Column("raw_product_description", sa.String(400)), sa.Column("submitted_price_eur", sa.Numeric(12,4), nullable=False),
        sa.Column("source", sa.String(40), nullable=False), sa.Column("source_reference", sa.String(500)),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True)), sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("submitted_price_eur > 0",name="ck_price_cache_positive"),
        sa.CheckConstraint("status IN ('PENDING','VERIFIED','REJECTED','EXPIRED')",name="ck_price_cache_status"))
    op.create_index("ix_price_cache_status_collected","price_cache",["status","collected_at"])
    op.create_table("promotions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("store_branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("promotional_price_eur", sa.Numeric(12,4), nullable=False), sa.Column("regular_price_eur", sa.Numeric(12,4)),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("ends_at", sa.DateTime(timezone=True)),
        sa.Column("source", sa.String(40), nullable=False), sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.CheckConstraint("promotional_price_eur > 0",name="ck_promotion_price_positive"),
        sa.CheckConstraint("regular_price_eur IS NULL OR regular_price_eur > 0",name="ck_promotion_regular_price_positive"))
    op.create_table("receipt_scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("image_storage_key", sa.String(500), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="UPLOADED"), sa.Column("extracted_text", sa.Text()),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("store_branches.id", ondelete="SET NULL")),
        sa.Column("receipt_date", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_table("receipt_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("receipt_scan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("receipt_scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="SET NULL")),
        sa.Column("raw_description", sa.String(400), nullable=False), sa.Column("quantity", sa.Numeric(12,3)),
        sa.Column("unit_price_eur", sa.Numeric(12,4)), sa.Column("line_total_eur", sa.Numeric(12,4)),
        sa.Column("match_confidence", sa.Numeric(5,4)), sa.Column("status", sa.String(20), nullable=False, server_default="UNMATCHED")))

def downgrade():
    op.drop_table("receipt_items")
    op.drop_table("receipt_scans")
    op.drop_table("promotions")
    op.drop_index("ix_price_cache_status_collected", table_name="price_cache")
    op.drop_table("price_cache")
    op.drop_table("current_prices")
    op.drop_table("product_barcodes")
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("store_branches")}
    if "longitude" in columns:
        op.drop_column("store_branches","longitude")
    if "latitude" in columns:
        op.drop_column("store_branches","latitude")
    if "postal_code" in columns:
        op.drop_column("store_branches","postal_code")
    if "locality_id" in columns:
        op.drop_column("store_branches","locality_id")
