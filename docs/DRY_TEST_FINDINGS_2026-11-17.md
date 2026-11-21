# Recommendation dry tests — 17 November 2026

Status: **assessment complete; implementation awaits owner approval**. This gate supersedes older build/deploy authorizations for this proposed work.

## Scope and evidence

Reviewed immutable source snapshot of `origin/codex/preview-006` at `8526eb866e01d85d0969029b7d5bed375cf3a8b6` (draft PR #13), the uploaded `You need to identify and.txt`, and the owner's four-item priority list. Source snapshot, test harnesses and derived image are isolated under `/workspace/work/dry-review-2026-11-17/`. Existing local branch and its edits were preserved.

Only public HTTP GETs, read-only Neon SELECT/EXPLAIN queries, Render deployment reads and local synthetic tests were performed. No application implementation, shared writes, migration/index creation, purge, branch deletion, deployment, commit/push, APK compilation or release was performed. An npm dependency installation and its dependency patches occurred only inside the isolated snapshot. This report and continuity notes are the only project documentation changes.

### 1. Async receipt upload and demo default — fixes justified

- Candidate `backend/app/receipts.py:upload_receipt` awaits reading/closing the upload, then performs Pillow processing, synchronous storage and SQLAlchemy operations on the async route's event loop.
- Executed the actual handler with a small synthetic image, fake storage taking 150 ms and fake commit taking 50 ms. Three recorded repetitions produced maximum event-loop tick gaps of **203–307 ms**. Running the same isolated invocation on a worker thread gave **5.8–5.9 ms** gaps, while request duration remained about 203 ms. This proves responsiveness risk, not a measured production latency improvement.
- Proposed remedy: run blocking processing/storage/DB work in a bounded synchronous worker execution path, with appropriate session ownership, bounded input reading and cleanup. Reverify ownership, EXIF stripping, upload limits, idempotency, concurrent requests and storage/DB failure cleanup. Merely adding `await` to synchronous clients is not a remedy.
- Candidate `mobile/App.tsx` initializes demo mode to true. Existing model/cache tests pass demo-price isolation, so this is a presentation/default issue, not evidence of fabricated live offers. Default real catalogue mode off from demos; retain a clearly labelled opt-in preview and current cache exclusion rules.
- Evidence: `upload-drytest.json`, reproducible `probe_upload.py` in evidence directory. Neither test touches real receipts or storage.

### 2. Seed CSV and shared Neon reconciliation — no missing seed rows

Matched branch identities using normalized retailer code, locality name, municipality, region and address, not totals alone:

| Check | Result |
|---|---:|
| CSV branches | 116 |
| Shared DB branches | 139 |
| CSV identities present in DB | 116 |
| CSV-only identities | 0 |
| DB-only identities | 23 |

All existing seed branches are present. The 23 additional database records require a provenance/status review; a count difference is not permission to delete them or overwrite the database with the CSV. Current inventory validator also passes with 5,291 canonical localities and no duplicate/unmatched seed branches.

Shared category coverage: groceries 14 retailers/134 active branches; technology 8/2; fuel 7/2. The two technology branches are in Велико Търново. Shared catalogue has 1,000 grocery products, **zero technology products**, zero product images, zero barcode rows and zero current prices. Thus category/source coverage remains a functional gap independent of seed synchronization.

Evidence: `seed-reconciliation.json` includes the 23 DB-only records; `neon-branch-detail.json` preserves public branch identities. No closure status was inferred.

### 3. Deployment, latency and indexes — deploy contract first; no speculative index migration

- Render's latest reported live deployment remains `dep-dbsppd8n74is73aimkc0`, source `538bd9a`, API **0.5.0**. Public `/openapi.json` independently reports 0.5.0. `/api/v1/catalog/groceries` returns **404**, while the candidate source expects this endpoint and falls back to serial 100-product pages.
- First `/health` attempt timed out at 25 seconds; next OpenAPI request took 8.34 seconds. Later locality HTTP samples took 927 ms (`Sofia`), 341 ms (`София`), and Sofia stores returned 46 grocery, zero technology and zero fuel branches. These are a small sequential sample, not a load benchmark or proof of the precise cold-start cause. Full timings are in `http-drytest.json`.
- EXPLAIN ANALYZE of candidate-equivalent locality SQL, two repetitions each for `Sofia`, `София`, `Бяла`, used sequential scans of 5,291 rows. Warm execution was **3.329–5.156 ms**. An earlier equivalent broad-query sample with physical reads took 47.95 ms. These do not establish the missing-index claim as the cause of slow end-to-end search.
- Existing shared indexes already include locality-name, locality/active-branch, current-price, history and receipt-job indexes (26 index definitions across the inspected tables). Inspect query expression and workload before selecting an index. A lower-name B-tree does not accelerate leading-wildcard substring predicates, but this single plan does not prove it is unused by every workload.
- Proposed order: reconcile approved source/deployment contract, reduce avoidable fallback requests, preserve suggestions while loading and provide bounded retry/error UX; then profile again. A trigram experiment belongs on a disposable local database if measured latency justifies it. No extension or index was installed on shared Neon.
- Evidence: `neon-indexes.json`, `neon-plan.json`, `neon-exact-plans.json`, `locality-queries.json`, `http-drytest.json`.

### 4. ARM64, R8 and assets — viable trial, native acceptance still required

- Current workflow packages arm64-v8a, armeabi-v7a and x86_64 together. Inspected a preserved **failed-attempt Preview005 APK**, not the published005 or future006 artifact, solely as a size baseline: **75,515,089 bytes**. Non-ARM64 native libraries account for **31,848,748 bytes**. Simple subtraction leaves about **43.7 MB**, a **42.2% theoretical reduction**, before rebuilt packaging/signing differences. This is not a measured new APK or guaranteed saving.
- SDK54's installed `expo-build-properties` validator accepts both `enableMinifyInReleaseBuilds: true` and `enableShrinkResourcesInReleaseBuilds: true`; resource shrinking requires minification. Configuration support is verified; R8 runtime safety and actual savings are **not yet tested** because no native build was started under the approval hold.
- Proposed architecture: ARM64 primary APK and separate x86_64 emulator artifact using the same release/minification configuration. Do not call an x86_64 emulator pass proof of ARM64 device acceptance. Retain/offer an ARMv7 fallback until dropping 32-bit support is explicitly decided. Production Play AAB can split architectures later.
- Derived a **separate** 256×256 WebP header-logo trial: **17,236 bytes**, compared with original PNG **1,008,792 bytes**. The source/icon/reference PNG remains untouched. Inspect quality on Android before switching the header reference; expected APK savings are smaller than the raw ratio when assets are reused or transformed.
- Keep expo-system-ui for Android interface style and active web-preview/test dependencies. No evidence justifies removing them. Icon-font subsetting is lower priority than ABI/R8 changes.
- Evidence: `asset-catalogue-drytest.json`, `header-logo-trial.webp`, `probe_assets.py`. SDK validator executed in isolated dependency installation; no app config was edited.

### 5. Purging, schema compression and backups — design only; defer destructive action

- Shared `receipt_scans`, `receipt_jobs`, `price_cache`, `national_offers`, `price_observations` and legacy `user_submissions` each currently have **zero rows**. Purging these today has no meaningful data-volume benefit. Total relation sizes measured approximately 3.04 MB for localities, 647 KB for products and 270 KB for branches, including indexes; these are not Neon billable branch-storage measurements.
- **All 5,291 live locality rows have distinct `name` and `name_bg` values.** The report's duplicate-name assumption about the CSV cannot be applied to the live schema. Do not drop either field without a field-contract migration and Bulgarian/Latin lookup compatibility tests.
- `Product.barcode` is used by lookup, admin and write paths. A future consolidation must migrate/backfill callers and validate GTIN aliases/conflicts before any column removal.
- Preserve receipt text and image needed for correction, owner storage and review. Proposed retention must specify user deletion, reviewed/unreviewed records, failed/deleting jobs, private objects, rollback/audit obligations and bounded retry-safe batches. No retention duration or purge job is approved by this dry test. Keep price history distinct from disposable cache.
- No endpoint usage was found for `user_submissions`, but code search alone does not exclude external integrations; defer removal. Recovery/validation branch storage is copy-on-write; table totals cannot be summed to estimate savings. Verify branch dependencies and a recovery plan before considering deletion.
- Preserve original CSV provenance and visual references; compact generated distribution assets separately.

### 6. Technology catalogue — scoped proposal, no imported products yet

The uploaded national market-share/bestseller assertions have no supporting citations; no exact national top1,000 ranking is verified. Proposed label: **1,000 verified, commonly stocked technology products**. A provisional allocation totals exactly1,000: mobile/accessories250; major/climate appliances250; small appliances250; TV/computing/audio200; smart-home/mobility50. These are planning quotas, not measured sales shares.

Require a small multi-retailer sourcing pilot before scaling: official source URL/time, retailer SKU, brand, manufacturer model/MPN, variant attributes, verified GTIN when available and image rights. Keep an exact product identity separate from retailer listings, shipping/installation/warranty, availability and timestamped conditional prices. Deduplicate compatible listings without merging different RAM/storage/color/bundle variants. Appliances remain within Техника; do not restore removed Дом.

Existing grocery importer, six-group provenance schema and cached-product validator are grocery-specific; copying them unchanged will not enable technology caching/import. Plan a compatible technology metadata/cache contract. Official feed access, model-level source extraction, image rights and actual1,000-item coverage remain unverified and require approval for implementation/sourcing work. No fabricated SKU list was generated.

## Existing-source checks executed

- Backend tests in the isolated source, with DATABASE_URL and TEST_DATABASE_URL unset: **74 passed, 5 skipped**. Skips include unavailable PostgreSQL/native OCR prerequisites; these are not claimed passed. Existing FastAPI/Starlette test-client deprecation warning remains; no dependency upgrade was applied.
- TypeScript typecheck and npm model, GTIN/search, cache and preview-metadata tests passed. Demo isolation, metadata-only cache and saved-list compatibility remain intact in these tests.
- No new browser/native build, R8 runtime test, physical device test, feedback-email delivery test, real retailer-feed import or database migration test was run. These remain implementation/release acceptance work.

## Concrete implementation scope proposed for approval

1. **Functional fixes first:** make receipt blocking work safe, default demos off, preserve private/idempotent receipt behaviour, reconcile the approved deployment/API contract and validate real store/fuel/image coverage. Review the 23 DB-only branches without deleting them.
2. **Complete agreed Preview006 backlog:** Settings/Feedback, source-backed coverage and location/request UX; configure real email delivery only with provider evidence. Technology catalogue begins with the sourcing/identity pilot and explicit allocation above.
3. **Optimization trial:** derived header image, separate distribution/test ABIs and R8/resource shrinking; measure resulting signed artifacts and test native camera, barcode decode, gallery, receipts/auth and UI. Keep current releases immutable.
4. **Defer speculative deletion:** no bulk seed replacement, locality/barcode/table removal, purge job or recovery-branch deletion until a separate measured retention/compatibility proposal is approved. Add only indexes supported by a subsequent benchmark.
5. **Release gates:** preserve Preview005; three separately evidenced complete passes on final source and explicit promotion of006. No publication follows from this dry-test report alone.

Next action: owner reviews/approves or adjusts the concrete scope. Until then, remain ACTIVE in assessment mode and do not start implementation, deployment or release.
