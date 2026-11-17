## 17 November — findings moved to to-do; execution candidate007

Owner authorized the following sequence; retain this006 backlog as the finding/task log, implement on `codex/preview-007`. See [dry-test evidence](DRY_TEST_FINDINGS_2026-11-17.md) and [007 plan](PREVIEW_007_PLAN.md).

- [ ] +1pt actual app text at every setting (owner clarified); all6languages/narrow widths.
- [ ] Official-source technology catalogue and Markdown identity list, target1,000 distinct products; no invented national popularity ranking.
- [ ] Seven required technology retailers and six fuel chains: verify official locators/coverage, not fabricated branches/prices.
- [ ] Offload receipt blocking work; preserve bounded upload, owner scope, idempotency and cleanup.
- [ ] Default demo off; preserve labelled opt-in and price/cache isolation.
- [x] Dry-reconcile116 CSV identities: all exist among139 Neon branches; review23 DB-only records, do not delete to force equality.
- [ ] Approved source/deployment contract alignment: live0.5 lacks candidate snapshot/auth routes.
- [ ] Stores overview without locality; verified local branches and honest zero-coverage states.
- [ ] Licensed product image sourcing/fallback; fuel/station availability.
- [ ] Faster location/request UX; warm SQL3–5ms means no justified speculative index addition yet.
- [ ] Settings black/white responsive choices; backend Feedback with real provider evidence.
- [ ] ARM64 distribution/x86_64 verification, R8/resource shrinking and derived WebP; measure real artifact.
- [ ] Three complete verification passes on final source and explicit release gate.
- [ ] Retention/purge/barcode-column/locality-column/backup deletion remain deferred, outside this implementation.

Historical006 scope follows; latest owner order above wins.

# Preview 006 backlog — 16 November 2026 (owner instruction)

**Branch:** `Test_postpreview-005` / draft PR #11. **Baseline:** published Preview 005, preserved. This is a candidate, not a released Preview 006. See Issue #10 for toolbar, feedback email, and mandatory three verification passes. Keep these work items together in the post-preview branch; do not modify the released Preview 005 artifacts.

## P0: data availability and performance (backend-first, then frontend)
- **Stores not populated:** inspect live `/api/v1/catalog`, `/api/v1/stores?locality_id=...&category_code=...` for representative Bulgarian cities, towns, and villages. Confirm database seed counts vs actual API response, active flags, locality UUID joins, category codes, pagination, deployed migrations, and production deployment version. Diagnose empty response separately from client render failures. Never fabricate branch availability.
- **Petrol stations not populated:** check `fuel` category, active retailer and StoreBranch rows, locality associations, backend API contract, and frontend category mapping. Keep fuel prices clearly unknown when no verified source exists; don't invent station locations or prices.
- **Product photos/thumbnails missing:** inspect product `image_url` data and product image relations, backend serialization, reachable HTTPS image URLs, CDN/host permissions, image fallback and caching in mobile. Test at least one real licensed/authorized image per supported category; show an explicit placeholder only when no image exists. Don't scrape copyrighted imagery without permission.
- **Slow location search:** profile real backend latency (cold start vs warm, SQL `EXPLAIN ANALYZE`, locality indexes, query limits, transliteration matching, payload size, network timings). Optimize backend filtering/indexes and bounded results first. Then optimize client debounce/cancellation, short reasonable timeout, caching of recent queries, and avoid repeated unnecessary calls. Ensure names/municipality/region still distinguish duplicates and selection works for towns and villages.
- Inspect `mobile/src/catalog/useCatalog.ts`: store fetching is conditional on `localityId` and currently returns an empty store list when no locality is selected. Confirm intended default behavior and add a useful all-store/choose-location state without lying about branch availability. Also inspect `allPages` and avoid unnecessary serial fetches; product images and fuel category may require different API paths.
- Inspect `mobile/src/location/LocationPicker.tsx`: 300ms debounce and **60-second request timeout** may contribute to perceived hangs; measure before tuning and add explicit short failure/retry UX.

## P1: Settings presentation (three-dot menu)
- In **Настройки**, use **black lettering on white background**. Settings options/choices should use simple compact button-like icons/shapes sized to approximately the font height, with thin padding between lettering and borders; no oversized illustrations.
- Settings options and choices **may be organized in two columns**, with responsive fallback to one column on narrow screens or larger accessibility font sizes. Keep minimum accessible touch targets and all six languages; do not clip labels.
- Apply to Settings screens and controls only, not global app branding.

## P1: existing Issue #10
- Shared toolbar: **Магазини/Продукти** 1pt smaller, **Обнови** gets freed width and a thin visible green border.
- **Обратна връзка**: sender/name, email address, message and submit; server-managed email to fixed `ivo77@duck.com`, never a recipient field or client-side secret. Prove actual provider acceptance/delivery; don't report success if credentials are missing.

## Verification / release gate
- **Three distinct complete green passes** on exact final source: backend unit/integration/security and DB matrix; functional UI + backend/data/image/location performance/feedback integration; release-grade native Android 10 emulator with barcode image decode and settings, stores, fuel, images, and feedback flows. Include measured latency baseline/after, sample counts and API payloads (redacted), CI links and screenshots.
- Confirm deployment/config/seeds separately from passing mocked CI tests. If live backend is empty, release remains blocked even when tests are green.
- After checks, owner may choose Preview 006 from this branch; update version metadata and produce fresh APK, not a relabelled 005 artifact. Preserve all earlier numbered releases.

## Preliminary source review (not runtime verification)
- `backend/app/catalog_api.py`: `/catalog` filters retailers by active local branches when locality supplied; verify seed/joins and branch API output.
- `mobile/src/catalog/useCatalog.ts`: no locality -> stores empty; fuel skips product loading; separate product and store fetches; allPages serial pagination.
- `mobile/src/location/LocationPicker.tsx`: 300ms debounce, 60s fetch abort timeout, clears results during every new request. These are investigation targets, not confirmed root causes.
- CI backend test success is not evidence that shared Neon has complete stores/images/stations or that Render live API responds quickly.
