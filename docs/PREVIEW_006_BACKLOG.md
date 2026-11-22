## 22 November 2026 — owner TODO

- [x] Drop x86_64 Android packaging and the hosted x86_64 emulator job. Retain signed ARM APK and test-signed AAB checks. Record the change in the development log. Installed Android testing moves to an ARM device.
- [x] Settings left column: Език, Тема, Размер на шрифта. Right column: Общи условия, Политика за поверителност, Изтрий данни.
- [x] Place the location field above the tabs. Keep each original category symbol above its name. Compact the stacked contents with 16 pt icons and 10 pt padding on each vertical edge.
- [x] Shrink the header and the Спестовник wordmark. Align the two slogan lines with the vertical menu and keep the wordmark visibly larger.
- [x] Use transparent, visually consistent thumbnail artwork. Use product-matched references where known and symbolic artwork where needed. Verify that tomato entries do not display banana artwork.
- [x] Горива: two static rows of content-width fuel controls. Top row Бензин 95, Бензин 98+, Обнови. Bottom row Дизел, Дизел +, Автогаз.
- [x] Capture a browser preview screenshot and report verification before Android build approval. [Browser preview](references/preview-10.5-compact-layout.jpg).
- [x] Refresh the grocery directory from the six requested official sources. T MARKET has partial coverage from verified store pages and a closure notice.
- [ ] After the final beta and before the first release, write a concise introduction summarizing the app's verified features and functionality. Keep the reminder in the handoff.

## Pre-alpha 010 — owner requirements, 21 November 2026

- [x] Backend first: paginated nationwide merchant directory from active recorded branches, grouped by category and canonical locality, with existing branch names and addresses.
- [x] Rename Моят списък to Сравни цените in all interface languages.
- [x] Food and Technology: remove Stores and Products buttons, put light-green product search before Refresh in the same row.
- [x] Remove group headings. Use two horizontally scrollable rows with a lower-right horizontal overflow button. Technology order: All Products and TV/Computing above, Smart Home, Small Appliances and Major Appliances below, then overflow.
- [x] Replace all Technology thumbnails with bundled, coherent colorful symbolic artwork. Keep the approved Food references and use matching card presentation.
- [x] Fuel: replace Stations and Fuel buttons with a compact current-fuel selector before Refresh.
- [x] Add Търговски обекти to the upper vertical menu. List addresses by category and canonical locality.
- [x] Preserve default and saved palettes. Add #b9ceac/#f2eee7, #f8c7fb/#c181f3, #022f40/#38aecc, #a29f61/#383615, #f7da83/#073368, #edede2/#ebbdd3, #1B263B/#FF7F50, #1B263B/#F4C7C3 and #806380/#ffc6ff. Include the repeated purple pair once.
- [x] After frontend, remove demonstrated obsolete code, then audit and remove unused dependencies.
- [x] Record three checks and a successful dry run for the candidate. See the handoff and visual evidence below.
- [x] Rename Облик to Тема. Remove the image switches, ignore legacy hide preferences, bundle small WebP defaults, and keep Dark mode reachable above the palettes.
- [x] Obtain acknowledgment and verify installed Android 10 smoke, ARM APK, and test-signed AAB for the 010 build.
- [ ] Complete physical-device and live API/data acceptance, including the deployed merchant directory.
- [x] Audit missing Food and Technology thumbnails. Pilot licensed, exact-identity 160 × 140 WebPs and verify decoding, cache behavior, and size.
- [x] Extend basket comparison with current per-merchant item prices and line subtotals. Verify complete totals, missing and expired prices, price timestamps, and responsive merchant cards.
- [x] Size Храни group buttons to their labels using the same content-width principle as Техника. Verify short and long translations at narrow widths.
- [x] In both Храни and Техника, make the horizontal ⋯ open a pop-up menu matching the header's vertical ⋮ interaction. Close on selection, outside tap, or Back, and preserve the chosen group.
- [x] Remove palettes 2, 3, 4, 5, 7, 8, 10, 14 and 17. Verify retained and removed saved selections.
- [ ] Extend photo coverage beyond the seven-record representative pilot with documented reuse rights and product matching.
- [x] Unify Food and Technology thumbnail framing to match the milk, oil and sugar examples. Verify bundled photo and symbolic fallback rendering.
- [x] Distinguish same-name products using source-backed details, barcode or catalogue code. Verify search and preserve separate basket identities.
- [x] Show the dated merchant inventory if the deployed directory route is absent. Verify recovery to live results when the route becomes available.
- [x] Enlarge thumbnails on tap without leaving the app. Show representative group photography in place of sketches and preserve image credits.
- [ ] Obtain approval of the exact 10.5 candidate before APK/AAB dispatch and verify the installed Android build. Locally verified feature scope and live rollout limits are in the handoff.

[Accepted itemized comparison layout sample with simulated prices](references/itemized-comparison-preview.png)

[Browser dry-run screenshots](references/pre-alpha-010-dry-run.jpg) · [Verification and next actions](CODEX_HANDOFF.md#21-november-2026--codex-pre-alpha-010)

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
