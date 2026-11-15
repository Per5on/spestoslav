-- Owner-requested retirement of Home and postal search. Keep canonical localities.
-- Run transactionally after the name-only API is deployed. No CASCADE drops.
DELETE FROM review_submissions WHERE cache_id IN (SELECT id FROM price_cache WHERE product_id IN (SELECT id FROM products WHERE category_code='home') OR branch_id IN (SELECT b.id FROM store_branches b JOIN catalog_retailers r ON r.code=b.retailer_code WHERE r.category_code='home'));
DELETE FROM price_cache WHERE product_id IN (SELECT id FROM products WHERE category_code='home') OR branch_id IN (SELECT b.id FROM store_branches b JOIN catalog_retailers r ON r.code=b.retailer_code WHERE r.category_code='home');
DELETE FROM price_observations WHERE product_id IN (SELECT id FROM products WHERE category_code='home') OR branch_id IN (SELECT b.id FROM store_branches b JOIN catalog_retailers r ON r.code=b.retailer_code WHERE r.category_code='home');
DELETE FROM national_offers WHERE product_id IN (SELECT id FROM products WHERE category_code='home') OR retailer_code IN (SELECT code FROM catalog_retailers WHERE category_code='home');
DELETE FROM current_prices WHERE product_id IN (SELECT id FROM products WHERE category_code='home') OR branch_id IN (SELECT b.id FROM store_branches b JOIN catalog_retailers r ON r.code=b.retailer_code WHERE r.category_code='home');
DELETE FROM promotions WHERE product_id IN (SELECT id FROM products WHERE category_code='home') OR branch_id IN (SELECT b.id FROM store_branches b JOIN catalog_retailers r ON r.code=b.retailer_code WHERE r.category_code='home');
DELETE FROM receipt_items WHERE product_id IN (SELECT id FROM products WHERE category_code='home') OR receipt_scan_id IN (SELECT s.id FROM receipt_scans s JOIN store_branches b ON b.id=s.branch_id JOIN catalog_retailers r ON r.code=b.retailer_code WHERE r.category_code='home');
DELETE FROM receipt_jobs WHERE scan_id IN (SELECT s.id FROM receipt_scans s JOIN store_branches b ON b.id=s.branch_id JOIN catalog_retailers r ON r.code=b.retailer_code WHERE r.category_code='home');
DELETE FROM receipt_scans WHERE branch_id IN (SELECT b.id FROM store_branches b JOIN catalog_retailers r ON r.code=b.retailer_code WHERE r.category_code='home');
DELETE FROM product_identification_requests WHERE product_id IN (SELECT id FROM products WHERE category_code='home');
DELETE FROM product_images WHERE product_id IN (SELECT id FROM products WHERE category_code='home');
DELETE FROM product_barcodes WHERE product_id IN (SELECT id FROM products WHERE category_code='home');
DELETE FROM collection_sources WHERE retailer_code IN (SELECT code FROM catalog_retailers WHERE category_code='home');
DELETE FROM products WHERE category_code='home';
DELETE FROM store_branches WHERE retailer_code IN (SELECT code FROM catalog_retailers WHERE category_code='home');
DELETE FROM catalog_retailers WHERE category_code='home';
DELETE FROM product_categories WHERE code='home';
UPDATE product_categories SET sort_order=CASE code WHEN 'groceries' THEN 10 WHEN 'technology' THEN 20 WHEN 'fuel' THEN 30 ELSE sort_order END;
DROP TABLE IF EXISTS locality_postal_codes;
ALTER TABLE inhabited_localities DROP COLUMN IF EXISTS postal_code;
ALTER TABLE store_branches DROP COLUMN IF EXISTS postal_code;
