## Build 016 release plan

Build 016 is the next Android candidate, with display label 10.10 and app version 0.5.9. [Future release changelog](../CHANGELOG.md#unreleased--build-016--app-059)

- [x] **Roll out the reviewed directory.** Published 1,585 active branches. Live checks in Пловдив found five indicative technology offers and 17 indicative fuel offers. The candidate shows when the selected town has no current grocery or technology prices. [Rollout record](ACTIVITY_LOG.md#23-november-2026--nationwide-rollout-and-build-016) · [Preview](references/preview016-plovdiv-grocery.png)
- [x] **Run candidate checks.** Mobile tests, strict TypeScript, Expo configuration, live browser checks, and both hosted PostgreSQL jobs passed for source `dcbdea2`. [Hosted checks](https://github.com/Per5on/spestoslav/actions/runs/45249343835)
- [ ] **Package the Android test APK after owner approval.** Use the reviewed build 016 candidate. Verify the app version, Android version code 16, signature, both ARM architectures and the downloaded SHA-256. Record the exact source and artifact link in the changelog.
- [ ] **Verify on an Android device.** Confirm install or upgrade, retained locality and basket, price refresh and comparison, the empty-price notice, camera barcode lookup and receipts. Use София or Велико Търново for grocery coverage when current prices are available. Check Пловдив for indicative technology and fuel offers and for the grocery empty state while coverage is absent.
- [ ] **Expand and sustain live prices.** Find a fresh, reusable grocery source for Пловдив, then verify retailer, branch, product identity, currency and validity before publication. Extend the same checks to other underserved towns. Activate the staged four-hour publisher for sources cleared for recurring reuse and verify a scheduled run publishes before existing prices expire. Include the reviewed Велико Търново branches when the grocery feed is enabled.
- [ ] **Verify live account and email flows.** Use an authorized inbox to check recovery-code expiry and reuse, old-session revocation, sign-in and reset attempt limits, and receipt access after recovery. Confirm feedback delivery separately. Keep these results distinct from fixture checks.

### Historical defect remediation

- [x] **Receipt upload recovery.** Preserve the image if the database commits and the response is lost. Keep cleanup before a known failed commit and verify that repeating the same request returns the original receipt. Regression tests cover a lost commit response and a pre-commit database failure.
- [ ] **Receipt orphan audit.** Prepare the report-only inventory pass against disposable or read-only storage. Validate age, scope and database references before proposing any cleanup.
- [ ] **Price gaps and refresh.** Keep the current focus on coverage gaps and expiry. Validate the Пловдив grocery source and the recurring publication path in the build 016 plan before treating them as resolved.
- [ ] **Live recovery and feedback.** Verify managed expiry, revocation and mail delivery through the existing account and email checks above.

### Future subscriptions

- [x] **Prepare the payment and subscription plan.** Document the Plus proposal, pricing hypotheses, Play Billing architecture, and release checks. [Subscription plan](SUBSCRIPTION_PLAN.md)
- [ ] **Review the proposal.** Confirm tiers, prices and the supported alert coverage before implementing checkout or provisioning payment services.

## 23 November 2026 — next commit and beta checklist

- [x] Consolidate catalogue and receipt-review helpers, tidy imports, and add the pinned Ruff CI check. Preserve historical documentation entry points.
- [x] **Expired price submissions in the candidate.** Submission responses derive `EXPIRED` for elapsed pending observations. The admin queue filters them before pagination. Both list endpoints stay read-only, and late approval is rejected. The local regression passes.
- [ ] **Live expired-submission verification.** Recheck against a disposable PostgreSQL database and verify the behavior after backend rollout.
- [ ] **Receipt orphan sweep.** Prepare a standalone dry-run-by-default command with an explicit option for deletion. Restrict it to receipt objects, bound each pass, and confirm the object remains unreferenced before any deletion. Establish safe behavior for in-flight uploads and partial failures using disposable storage before accepting the implementation. Review only for now. The supplied patch deletes by default.

### Visual review

- [x] **Header.** Remove the logo from the header and use „Сравни и спести“ in the existing slogan position. Enlarge the slogan for smaller screens. Reduce header height and move its bottom edge up slightly. The owner approved the logo-free preview.
- [x] **Android launcher.** Restore the previous money-bag icon for Android only.
- [ ] **Product cards and thumbnails.** Reduce product and thumbnail fields by 2 pt. Unify the visual style across „Храни“ and „Техника“ and retain approved WebP output. Evaluate [Broshura.bg](https://www.broshura.bg) for both categories, checking reuse terms and product matches. Add a thumbnail database if needed. The 2 pt size reduction and six matched generated sample WebPs are implemented. Live coverage remains open. [Implemented technology sample](references/next-beta-technology-implemented.png).
- [x] **Bottom message.** Use the screenshot as the reference for the illustrative-photo notice, store-load error and saved-catalogue notice. Shorten them and group the applicable notices at the bottom of the screen with 1.5 pt between lines. Show each notice under its existing condition. [Implemented footer](references/next-beta-footer-implemented.png).
- [x] **Food groups.** The first row is „Всички храни“ and „Основни храни и консерви“. The second contains „Плодове и зеленчуци“, „Месо, колбаси и риба“ and „Млечни продукти и яйца“. All other available groups, including „Подправки и напитки“, are in the trailing three-dot menu. [Implemented view](references/next-beta-food-implemented.png).
- [ ] **Fuel controls.** Remove „Обнови“ and arrange all five fuel choices in one row. Show local petrol stations and prices for the selected fuel. Remove product search, cart actions and fuel participation in „Сравни цените“. Keep product search and add-to-cart in „Храни“ and „Техника“ only.

Visual approval set: [Food, Technology and Fuel](references/next-beta-catalogue-review.png) · [Food overflow open](references/next-beta-food-groups-mock.png) · [Header and all three footer notices](references/next-beta-no-logo-header.png). The contact-sheet thumbnails are generated, illustrative WebPs. Fuel prices in the mockup are fixture values.

### Backend and beta acceptance

- [x] **Daily source checks.** The owner requested daily checks for „Храни“, „Техника“ and „Горива“. A GitHub Actions workflow on the default branch checks Burlex, Techmart and KARAI at 11:17 UTC. Its report tracks the recent official grocery archive as a secondary source.
- [ ] **Price publication and backup matching.** Apply fresh observations to the live app only after verifying source date, currency, identity and locality. The Burlex and Techmart pilot prices expire after 12 hours and the KARAI pilot after 24 hours. Keep expired observations out of current totals. The archive's sampled Sofia branches are distinct from the two active Burlex pilot branches. Technology and fuel backup sources still need an authorized feed and matching coverage.
- [x] **Forgotten password candidate.** Added „Забравена парола“ to email/password sign-in and implemented Neon Auth email-code recovery. Browser fixtures verified incorrect and reused codes and sign-in with the new password. [Sign-in](references/beta-forgot-password-sign-in.png) · [Email](references/beta-forgot-password-email.png) · [Code](references/beta-forgot-password-code.png)
- [ ] **Live password recovery.** Verify receipt of the code in an authorized inbox and sign in on a new or clean device. Confirm the recovered account can reopen its receipts. The basket and preferences use device-local storage.
- [ ] **Price sources.** Start connecting groceries and technology to Broshura.bg or official merchant pages. Select the lightest reliable source per merchant and verify the location and validity of the offer. Confirm a usable station-level price source for the selected fuel. Keep unavailable prices distinct from verified prices.
- [ ] **Location scope.** Scope filters, results and prices to the selected locality. Restrict comparisons to stores present in that locality. Verify location changes and empty or incomplete coverage.
- [ ] **Моят магазин.** The grocery chain already has a registry placeholder and no seeded branches at this checkpoint. Verify physical addresses against the [official directory](https://www.moiatmagazin.bg/magazini), add the branches to „Търговски обекти“, and include eligible chain products and prices as sourcing becomes available.
- [ ] **Beta feature checks.** Treat subsequent builds as betas. Verify real product thumbnails and prices, locality filtering, product search, cart and price comparison, barcode scan, receipt flows, feedback with email delivery, login, and the other planned features in the [handoff](CODEX_HANDOFF.md) and project documentation. Record fixture results separately from live acceptance. Run the beta candidate against its live API with simulation mode off. Verify live reads, location-specific data and end-to-end authenticated workflows before requesting APK approval. The „данните и изпращането са симулирани“ notice stays on fixture previews only. Keep real outage, missing-price and catalogue notices available in the live app.
- [ ] **Release gates.** Show visual previews of all user-facing changes for review before including them in the build or APK commit. Review the code, verify backend functionality and pass dry tests. Obtain explicit owner approval for the APK build after those gates. Keep the cleanup, expired submissions and receipt sweep tasks above in scope.

### Source checks — 23 November 2026

| Source | Observed | Next check |
| --- | --- | --- |
| [Kaufland offers](https://www.kaufland.bg/aktualni-predlozheniya/oferti.html) | The public store-specific feed for Sofia branch BG1000 returned article IDs and validity dates. | Join only offers supported by the selected branch and validate the matching displayed price and any loyalty conditions. |
| [Technopolis sample product](https://www.technopolis.bg/bg/Smartfoni-i-mobilni-telefoni/Smartfon-GSM--MOTOROLA-EDGE-70-FUSION/p/509669) | The official page exposes a structured EUR price and a store pickup option. | Confirm branch-level availability and whether the online price also applies in the branch before including it in a local comparison. |
| [Моят магазин locator](https://www.moiatmagazin.bg/magazini) | The public locator returned 288 records. The site says participating retailers set their own selling prices and promotional scope can vary by store. | Validate and deduplicate addresses against canonical localities. Check participation per offer. |
| [Broshura.bg terms](https://s3-eu-west-1.amazonaws.com/public-legal-docs.offerista/offerista-bg/en/tou.html) | The published terms restrict copying significant parts of the database. | Confirm reuse permission before a bulk import or redistribution of catalogue images or data. |
| [Fuelo](https://api.fuelo.net/) | The app repository has a station-price collector and known station listings. The collector requires an API key and eligible plan. | Verify plan coverage and freshness with authorized access. |

## 22 November 2026 — owner TODO

- [x] Drop x86_64 Android packaging and the hosted x86_64 emulator job. Retain signed ARM APK and test-signed AAB checks. Record the change in the development log. Installed Android testing moves to an ARM device.
- [x] Settings left column: Език, Тема, Размер на шрифта. Right column: Общи условия, Политика за поверителност, Изтрий данни.
- [x] Place the location field above the tabs. Keep each original category symbol above its name. Compact the stacked contents with 20 pt icons and 10 pt padding on each vertical edge.
- [x] Shrink the header and the Спестовник wordmark. Align the two slogan lines with the vertical menu and keep the wordmark visibly larger.
- [x] Use transparent, visually consistent thumbnail artwork. Use product-matched references where known and symbolic artwork where needed. Verify that tomato entries do not display banana artwork.
- [x] Горива: two static rows of content-width fuel controls. Top row Бензин 95, Бензин 98+, Обнови. Bottom row Дизел, Дизел +, Автогаз.
- [x] Capture a browser preview screenshot and report verification before Android build approval. [Browser preview](references/preview-10.5-compact-layout.jpg).
- [x] Refresh the grocery directory from the six requested official sources. T MARKET has partial coverage from verified store pages and a closure notice.
- [x] Add verified physical stores for Techmart, Зора, JAR Computers, Техномаркет, Ardes, Технополис and Вали to Търговски обекти and record the source coverage in the handoff.
- [x] Add the six requested Fuelo chains to Търговски обекти and record station coverage in the handoff.
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
