-- Additive schema migration for the existing bgprices preview database.
-- This is the SQL equivalent of Alembic revision 0003 for the pre-existing Flyway schema.
-- Run once against the intended branch; it deliberately preserves all existing rows.
ALTER TABLE store_branches ADD COLUMN locality_id UUID REFERENCES inhabited_localities(id);
ALTER TABLE store_branches ADD COLUMN postal_code VARCHAR(12);
CREATE INDEX ix_store_branches_locality_active ON store_branches(locality_id, active);
CREATE TABLE product_barcodes (id UUID PRIMARY KEY, product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE, barcode VARCHAR(64) NOT NULL UNIQUE, source VARCHAR(40) NOT NULL DEFAULT 'ADMIN', verified BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE INDEX ix_product_barcodes_product ON product_barcodes(product_id);
CREATE TABLE current_prices (id UUID PRIMARY KEY, product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE, branch_id UUID NOT NULL REFERENCES store_branches(id) ON DELETE CASCADE, price_eur NUMERIC(12,4) NOT NULL CHECK (price_eur > 0), source VARCHAR(40) NOT NULL, verified_at TIMESTAMPTZ NOT NULL, expires_at TIMESTAMPTZ, CONSTRAINT uq_current_price_product_branch UNIQUE(product_id, branch_id));
CREATE INDEX ix_current_prices_branch ON current_prices(branch_id);
CREATE INDEX ix_current_prices_product ON current_prices(product_id);
CREATE TABLE price_cache (id UUID PRIMARY KEY, product_id UUID REFERENCES products(id) ON DELETE SET NULL, branch_id UUID REFERENCES store_branches(id) ON DELETE SET NULL, raw_product_description VARCHAR(400), submitted_price_eur NUMERIC(12,4) NOT NULL CHECK (submitted_price_eur > 0), source VARCHAR(40) NOT NULL, source_reference VARCHAR(500), status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','VERIFIED','REJECTED','EXPIRED')), collected_at TIMESTAMPTZ NOT NULL DEFAULT now(), expires_at TIMESTAMPTZ, reviewed_at TIMESTAMPTZ);
CREATE INDEX ix_price_cache_status_collected ON price_cache(status,collected_at);
CREATE TABLE promotions (id UUID PRIMARY KEY, product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE, branch_id UUID NOT NULL REFERENCES store_branches(id) ON DELETE CASCADE, promotional_price_eur NUMERIC(12,4) NOT NULL CHECK (promotional_price_eur > 0), regular_price_eur NUMERIC(12,4) CHECK (regular_price_eur IS NULL OR regular_price_eur > 0), starts_at TIMESTAMPTZ NOT NULL, ends_at TIMESTAMPTZ, source VARCHAR(40) NOT NULL, verified BOOLEAN NOT NULL DEFAULT FALSE);
CREATE INDEX ix_promotions_branch_dates ON promotions(branch_id,starts_at,ends_at);
CREATE INDEX ix_promotions_product ON promotions(product_id);
CREATE TABLE receipt_scans (id UUID PRIMARY KEY, image_storage_key VARCHAR(500) NOT NULL, status VARCHAR(24) NOT NULL DEFAULT 'UPLOADED', extracted_text TEXT, branch_id UUID REFERENCES store_branches(id) ON DELETE SET NULL, receipt_date TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE INDEX ix_receipt_scans_status_created ON receipt_scans(status,created_at);
CREATE TABLE receipt_items (id UUID PRIMARY KEY, receipt_scan_id UUID NOT NULL REFERENCES receipt_scans(id) ON DELETE CASCADE, product_id UUID REFERENCES products(id) ON DELETE SET NULL, raw_description VARCHAR(400) NOT NULL, quantity NUMERIC(12,3), unit_price_eur NUMERIC(12,4), line_total_eur NUMERIC(12,4), match_confidence NUMERIC(5,4), status VARCHAR(20) NOT NULL DEFAULT 'UNMATCHED');
CREATE INDEX ix_receipt_items_scan ON receipt_items(receipt_scan_id);