"""Initial Spestoslav schema; independent of legacy Flyway history."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("product_categories", sa.Column("code", sa.String(40), primary_key=True), sa.Column("name_bg", sa.String(120), nullable=False), sa.Column("name_en", sa.String(120), nullable=False), sa.Column("description_bg", sa.String(300), nullable=False, server_default=""), sa.Column("description_en", sa.String(300), nullable=False, server_default=""), sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("inhabited_localities", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("source", sa.String(40), nullable=False), sa.Column("source_id", sa.String(100), nullable=False), sa.Column("name", sa.String(180), nullable=False), sa.Column("name_bg", sa.String(180)), sa.Column("postal_code", sa.String(12)), sa.Column("type", sa.String(24), nullable=False, server_default="OTHER"), sa.Column("municipality", sa.String(160)), sa.Column("region", sa.String(160)), sa.Column("on_map", sa.Boolean(), nullable=False, server_default=sa.true()), sa.UniqueConstraint("source", "source_id", name="uq_inhabited_locality_source"))
    op.create_index("ix_localities_name_lower", "inhabited_localities", [sa.text("lower(name)")])
    op.create_index("ix_localities_postal_code", "inhabited_localities", ["postal_code"])
    op.create_table("catalog_retailers", sa.Column("code", sa.String(64), primary_key=True), sa.Column("name", sa.String(160), nullable=False), sa.Column("category_code", sa.String(40), sa.ForeignKey("product_categories.code"), nullable=False), sa.Column("website_url", sa.String(500)), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("products", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("category_code", sa.String(40), sa.ForeignKey("product_categories.code"), nullable=False), sa.Column("barcode", sa.String(64)), sa.Column("brand", sa.String(160)), sa.Column("name", sa.String(300), nullable=False), sa.Column("variant", sa.String(200)), sa.Column("package_quantity", sa.Numeric(12,3)), sa.Column("package_unit", sa.String(32)), sa.Column("normalized_name", sa.String(400), nullable=False), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_products_barcode", "products", ["barcode"])
    op.create_table("store_branches", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("retailer_code", sa.String(64), sa.ForeignKey("catalog_retailers.code"), nullable=False), sa.Column("locality_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inhabited_localities.id"), nullable=False), sa.Column("branch_name", sa.String(160)), sa.Column("address", sa.String(300), nullable=False), sa.Column("source", sa.String(40), nullable=False, server_default="MANUAL"), sa.Column("source_id", sa.String(100)), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_branch_locality", "store_branches", ["locality_id", "active"])
    op.create_table("price_observations", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False), sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("store_branches.id"), nullable=False), sa.Column("price_eur", sa.Numeric(12,4), nullable=False), sa.Column("regular_price_eur", sa.Numeric(12,4)), sa.Column("source", sa.String(80), nullable=False), sa.Column("source_reference", sa.String(500)), sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("valid_from", sa.DateTime(timezone=True)), sa.Column("valid_until", sa.DateTime(timezone=True)), sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_check_constraint("ck_price_positive", "price_observations", "price_eur > 0")
    op.create_table("user_submissions", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("submission_type", sa.String(40), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("locality_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inhabited_localities.id")), sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("reviewed_at", sa.DateTime(timezone=True)))

def downgrade():
    op.drop_table("user_submissions")
    op.drop_constraint("ck_price_positive", "price_observations", type_="check")
    op.drop_table("price_observations")
    op.drop_table("store_branches")
    op.drop_table("products")
    op.drop_table("catalog_retailers")
    op.drop_index("ix_localities_postal_code", table_name="inhabited_localities")
    op.drop_index("ix_localities_name_lower", table_name="inhabited_localities")
    op.drop_table("inhabited_localities")
    op.drop_table("product_categories")
