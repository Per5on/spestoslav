-- Data reconciliation only, on preview br-snowy-morning-baym8iw6.
-- The older locator lists this address, but the current feed omits it.
-- Retain for audit; inactive means pending review here, NOT a confirmed closure.
-- Source evidence: data/store_branch_pending_review.csv and data/evidence/2026-11-14-groceries.json.
UPDATE store_branches
SET active=false, updated_at=now()
WHERE source='OFFICIAL_STORE_LOCATOR'
  AND source_id='inventory:mini_mart:b5a435773a4c22d36a9159aad6d0b2ca'
  AND retailer_code='mini_mart' AND city='София'
  AND municipality='Столична' AND region='София (столица)'
  AND address='бул. „Христо Ботев” № 75' AND active=true
RETURNING id, retailer_code, branch_name, active;
