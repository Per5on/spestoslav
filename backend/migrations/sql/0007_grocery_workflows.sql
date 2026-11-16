CREATE TABLE IF NOT EXISTS grocery_groups (
 code VARCHAR(40) PRIMARY KEY,
 name_bg VARCHAR(120) NOT NULL,
 name_en VARCHAR(120) NOT NULL,
 aliases VARCHAR(500) NOT NULL,
 sort_order INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS grocery_catalog_identities (
 product_id UUID PRIMARY KEY REFERENCES products(id),
 group_code VARCHAR(40) NOT NULL REFERENCES grocery_groups(code),
 source VARCHAR(64) NOT NULL,
 source_product_code VARCHAR(100) NOT NULL,
 source_category VARCHAR(300) NOT NULL,
 source_url VARCHAR(500) NOT NULL,
 observed_at TIMESTAMP WITH TIME ZONE NOT NULL,
 CONSTRAINT uq_grocery_source_identity UNIQUE(source, source_product_code)
);
CREATE INDEX IF NOT EXISTS ix_grocery_catalog_identities_group_code ON grocery_catalog_identities(group_code);
ALTER TABLE receipt_jobs ADD COLUMN IF NOT EXISTS request_key VARCHAR(100);
ALTER TABLE receipt_jobs ADD COLUMN IF NOT EXISTS upload_fingerprint VARCHAR(64);
CREATE UNIQUE INDEX IF NOT EXISTS uq_receipt_upload_request ON receipt_jobs(owner_subject, request_key);
