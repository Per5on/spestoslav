-- Additive compatibility patch for the existing Flyway preview only.
-- Test on backend-readiness-fixes first. Do not run the Alembic baseline here.
-- The optional legacy postal column unblocks the currently deployed 0.3 API;
-- 0.4 reads canonical postal links and does not depend on this column.
ALTER TABLE inhabited_localities ADD COLUMN IF NOT EXISTS postal_code VARCHAR(12);
CREATE TABLE IF NOT EXISTS review_submissions (
 id UUID PRIMARY KEY, owner_subject VARCHAR(200) NOT NULL, request_key VARCHAR(100) NOT NULL,
 cache_id UUID NOT NULL UNIQUE REFERENCES price_cache(id), reviewed_by VARCHAR(200), review_note TEXT,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 CONSTRAINT uq_review_request UNIQUE(owner_subject,request_key));
CREATE INDEX IF NOT EXISTS ix_review_owner ON review_submissions(owner_subject,created_at);
CREATE TABLE IF NOT EXISTS collection_sources (
 code VARCHAR(64) PRIMARY KEY, retailer_code VARCHAR(64) NOT NULL REFERENCES catalog_retailers(code),
 origin VARCHAR(500) NOT NULL, kind VARCHAR(24) NOT NULL DEFAULT 'OFFICIAL', enabled BOOLEAN NOT NULL);
CREATE TABLE IF NOT EXISTS receipt_jobs (
 id UUID PRIMARY KEY, scan_id UUID NOT NULL UNIQUE REFERENCES receipt_scans(id),
 owner_subject VARCHAR(200) NOT NULL, attempts INTEGER NOT NULL, claimed_at TIMESTAMPTZ, error VARCHAR(300));
CREATE INDEX IF NOT EXISTS ix_receipt_job_owner ON receipt_jobs(owner_subject);
ALTER TABLE collection_sources ADD COLUMN IF NOT EXISTS kind VARCHAR(24) NOT NULL DEFAULT 'OFFICIAL';
ALTER TABLE current_prices ADD COLUMN IF NOT EXISTS observed_at TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS product_identification_requests (
 id UUID PRIMARY KEY, owner_subject VARCHAR(200) NOT NULL, barcode VARCHAR(64) NOT NULL,
 description TEXT, status VARCHAR(20) NOT NULL, product_id UUID REFERENCES products(id),
 reviewed_by VARCHAR(200), created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 CONSTRAINT uq_identification_owner_barcode UNIQUE(owner_subject,barcode));
CREATE TABLE IF NOT EXISTS product_images (
 product_id UUID PRIMARY KEY REFERENCES products(id),image_url VARCHAR(1000) NOT NULL,source_url VARCHAR(1000) NOT NULL);
CREATE TABLE IF NOT EXISTS national_offers (
 id UUID PRIMARY KEY, product_id UUID NOT NULL REFERENCES products(id),retailer_code VARCHAR(64) NOT NULL REFERENCES catalog_retailers(code),
 price_eur NUMERIC(12,4) NOT NULL,source_reference VARCHAR(1000) NOT NULL,observed_at TIMESTAMPTZ NOT NULL,
 verified_at TIMESTAMPTZ NOT NULL,verified_by VARCHAR(200) NOT NULL,valid_until TIMESTAMPTZ NOT NULL);
CREATE INDEX IF NOT EXISTS ix_national_offer_product_retailer ON national_offers(product_id,retailer_code,observed_at);
