# Initial source-backed grocery catalogue

`essential-1000.json` contains 1,000 distinct retailer product codes and source names from the public official Burlex consumer-basket table, observed on 15 November 2026. Six approved grocery groups are represented. Household and tobacco records were excluded. Two wine variants were omitted to cap the initial batch at 1,000. This is an initial retailer-scoped selection, **not evidence of the nationwide top 1,000 essentials or complete coverage**; herbs, additional produce and other retailers still need expansion.

A retailer product code is not an EAN/GTIN. No barcode, price, product photo or cross-retailer equivalence was invented. Names preserve the source wording; pack quantities are populated only where an explicit trailing quantity could be parsed. The raw evidence hash is recorded in the JSON; the raw collected table remains in the task workspace. Names from different source codes can be similar and remain separate until reviewed.

## Updating

1. Run `scripts/collect_burlex_catalog.py --store 'EXACT PUBLIC STORE NAME' --output NEW-REVIEW-FILE.json`. Public access must remain permitted; a 403/auth/error stops collection. Requests are sequential and bounded. Existing output is never overwritten.
2. Review source identity/name changes, conflicts, classification, omissions and truncation against the previous batch. Missing data is not a closure or deletion signal. Resolve source terms before enabling unattended commercial collection. This script does not claim a documented/supported retailer API.
3. Update the versioned catalogue deliberately; run importer validation and isolated PostgreSQL tests. Apply migration 0007 before using `scripts/import_grocery_catalog.py --apply`. Repeated imports retain deterministic product IDs and existing barcode assignments; they never publish prices or create branches.
4. Price ingestion is a separate reviewed feed with explicit currency, branch/online scope, validity and source provenance. Undated/ambiguous prices from this table are not imported.

Kaufland/Lidl are follow-up official sources, not connected catalogue APIs in this batch. Fuelo concerns fuel, not grocery identity.
