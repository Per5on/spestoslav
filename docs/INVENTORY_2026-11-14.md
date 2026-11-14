# Reviewed grocery batch — 14 November 2026

Continues Issue #1 from main `7fc6da2`. This is a small reviewed batch, not national coverage or a guarantee that every listed store is currently trading. Android UI, API behavior, prices and schema are unchanged.

## Sources and scope

- Mini Mart: https://mini-mart.bg/nameri-magazin-3/ — HTTP 200, first ten Sofia addresses reviewed directly in official page content. Nine rows retained in the verified batch after cross-checking the navigation-linked current locator at https://mini-mart.bg/nameri-magazin/. Its public Agile Store Locator feed (`wp-admin/admin-ajax.php?action=asl_load_stores`, using page-supplied parameters) returned 358 records. This is a feed record count, not a deduplicated physical-store count. Feed IDs 75 and 118 both describe Patriarch Evtimiy 61, so count that address once. The tenth older-page listing, Hristo Botev 75, was absent from the current feed: it was removed from the seed and verified batch, recorded in `data/store_branch_pending_review.csv`, and deactivated in preview after the initial import. Absence is not proof of closure. Full national reconciliation remains pending.
- CBA: https://www.cba.bg/shops.php — HTTP 200, linked as “Магазини” from https://www.cba.bg/. Six unambiguous Burgas Bolero listings added. The directory displays 120 supermarkets, whereas the homepage advertises 170+. These are publisher counts, not verified inventory counts. Directory regional groupings are not administrative oblasts (for example, Petrich is grouped under Sofia); some city fields conflict with the address city (Bolero 4 says Burgas but its address says Tsarevo). Klasiko listings overlap existing Klasiko inventory. Those cases require review before further ingestion; no duplicate Klasiko rows were added under CBA.
- T MARKET: https://tmarketonline.bg/page/stores-t-market — direct HTTP fetch returned 403; full page content was available through the web tool. It still lists closed Sofia branches. The current main-site locator is https://tmarket.bg/page/nashite-magazini but its extracted page contains only a city selector.
- T MARKET closure/replacement notice: https://tmarket.bg/article/vajna-informaciya-za-klientite-ni-v-grad-sofiya-i-grad-burgas — full official article reviewed, published 2 October 2026. Seven alternatives explicitly offered by the retailer added (five Sofia, two Burgas). This notice is the source for those seven rows; `OFFICIAL_STORE_LOCATOR` here denotes official branch evidence, including this notice, rather than an exhaustive locator snapshot.

The same notice explicitly closes four stores from 5 October 2026: Burgas Konstantin Velichkov 34 / Strandzha 2; Sofia Persenk 22, Atanas Dalchev 2 and Druzhba 2 block 311. Recorded in `data/store_branch_closures.csv`; none existed in the seed or preview before the batch. No database closures were necessary. They were excluded from additions; absence from a partial batch never implies closure. Broader T MARKET closure reconciliation remains pending.

`data/evidence/2026-11-14-groceries.json` records reviewed addresses and retrieval metadata. SHA-256 hashes refer to the HTTP bodies retrieved in this session; raw HTML remains scratch material, so hashes are retrieval fingerprints, not standalone proof. The T MARKET evidence was retrieved through the web tool and has no raw-body hash. No search snippet was used as sole branch evidence. Checked dates have day precision, not an asserted time of store operation.

## Preview synchronization

Explicit destination: project `long-resonance-77491878` (`bg-prices-preview`), branch `br-snowy-morning-baym8iw6` (`preview`). It is the project's default branch but was selected explicitly by ID. No other database was modified.

| Measure | Before | Initial import/repeat | Final reconciliation/repeat |
| --- | ---: | ---: | ---: |
| Branches | 116 | 139 | 139 |
| Non-null locality links | 116 | 139 | 139 |
| Active branches | 116 | 139 | 138 |
| Seed rows | 116 | 139 | 138 |
| Retailers with physical branches | 12 | 15 | 15 |
| Catalog/source registry retailers | 38 | 38 | 38 |

Final verified batch: 22 active additions — Mini Mart 9, T MARKET 7, CBA 6. One additional Mini Mart record retained inactive in preview for audit/pending review, outside the seed and verified batch. This explains 139 total database rows versus 138 seed/active rows. Previously existing branches updated/closed: 0; confirmed closures applied: 0; newly imported records deactivated as pending: 1. No prices added.

Post-import checks: 23 new unique branch UUIDs (22 verified active, one pending inactive); zero duplicate `(source, source_id)` groups across the database; zero batch locality mismatches on `name_bg + municipality + region`; all three retailers active in category `groceries`; maximum new source ID length 52 (limit 100). 138 database branches remain marked active; this does not independently reverify the previous 116. Both the initial 23-row import and the final 22-row import were executed twice without count growth; repeating the pending-record update returned zero rows.

## Reproduction and limits

```bash
python scripts/prepare_branch_batch.py data/batches/2026-11-14-groceries.csv > /tmp/grocery-batch.sql
# Execute the single printed DO statement only on the explicitly selected preview branch.
# Apply scripts/migrations/preview_20261114_pending_minimart.sql there to quarantine
# the pending legacy listing if it exists; a clean seed import has no such row.
cd backend
PYTHONPATH=. pytest -q
```

The batch CSV duplicates the reviewed subset intentionally; validation requires every batch row to occur exactly once in the main seed. The SQL generator targets the existing legacy preview schema, which includes fields absent from the new-install ORM schema; it is not a generic importer for every installation. No migration is needed.

IDs use `inventory:<retailer_code>:<32 hex SHA-256 chars>` from retailer + city + municipality + region + address. They are locally assigned, not official IDs. Source URLs and dates remain in seed/batch/evidence files. A name-only edit preserves identity; an address/format change requires explicit reconciliation. Exact existing retailer/locality/address matches under another source identity abort instead of creating duplicates. Formatting variants still require human review. Existing inactive rows are not automatically reactivated.

The import locks the branch table, requires exactly one locality match and a registered active retailer/category, and aborts the whole statement on a conflict. Repeats use the existing unique `(source,source_id)` index and insert nothing. This is insert-only synchronization: changes to existing metadata, removals and closures need a separately reviewed operation.

Local validation: 18 pytest tests passed, including six existing API tests and twelve batch safety tests. One upstream FastAPI/Starlette httpx deprecation warning remains. Current-commit GitHub Actions results are reported in the PR after pushing; the older CI run in the handoff is not evidence for this change.

Next: continue deduplicating Mini Mart's current map feed and resolve the pending older-page listing; continue T MARKET against a fully reconciled current directory; resolve CBA affiliate overlaps and administrative locality conflicts before larger batches. Then continue remaining groceries, fuel, home and technology as Issue #1 describes.
