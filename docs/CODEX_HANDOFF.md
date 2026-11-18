# Спестовник — ongoing project handoff

Updated: **18 November 2026 (Europe/Sofia)**. Project status: **ACTIVE**.

This is the continuing project. Read this checkpoint, `PROJECT_STATUS.md` and the newest `ACTIVITY_LOG.md` entry first; do not restart by rereading old conversations. Handoff files preserve continuity; they do not run a background coding process by themselves.

## Latest checkpoints (newest first)


### Preview008 restarted on the corrected source — 18 November 2026

- Corrected candidate `2b511f09ab1667fee6d2a81715067bd8a0dce021` is on draft PR #19. [Backend CI](https://github.com/Per5on/spestoslav/actions/runs/44307055281) passed. [Android workflow](https://github.com/Per5on/spestoslav/actions/runs/44307049747) is the internal run to inspect.
- Repeated the browser responsiveness and offline sample checks on the corrected source. Median menu time at 4× CPU throttle was 21.0 ms, down from the 63.1 ms baseline. The p95 was 30.1 ms, down from 105.1 ms. All nine sample images decoded with API requests blocked. About contained no product links.
- Acceptance gates are native visual smoke evidence and verification of the signed ARM package size against the 75,567,529-byte Preview007 APK. The same-device ARM responsiveness comparison remains open.
- Android 10 smoke passed on run 44307049747. Its ARM package step failed during Gradle native clean because CMake referenced removed JNI codegen. The follow-up regenerates the Android project before compiling ARM. App source and smoke assertions are identical.



### Preview008 stopped for visual corrections — 18 November 2026

- At the owner's request, [Android run 44306415234](https://github.com/Per5on/spestoslav/actions/runs/44306415234) on commit `687b467` was cancelled. GitHub reports no Preview008 APK artifact.
- Corrected two interpretation errors in the candidate. Refresh has no border in any state and shows keyboard focus through its background. About ends with Feedback and contains no product rows. Licensed sample image credits accompany the corresponding sample cards in the catalogue.
- Reviewed new browser screenshots and checked computed Refresh border and outline widths, Settings, About content, location input, catalogue and sample credits. TypeScript, npm and browser suites passed. Corrections remain local. Wait for the owner to restart Android CI with the corrected source.



### Preview008 candidate build commit — 18 November 2026

- Rechecked the two GitHub uploads and draft PR #19. Its prior head `daa73ae` had no Preview008 APK artifact. This candidate keeps sequence 008 and version 0.5.1 for the first internal APK.
- Phone package uses arm64-v8a and armeabi-v7a. Android 10 CI uses a separate internal x86_64 APK for the Play Services emulator. CI packages the phone APK after the smoke test and verifies its signature, native architectures and checksum. R8 and resource shrinking are enabled for both CI variants. There is no publication job.
- All four original visual requests passed browser verification. Refresh and buttons use green focus styling, Settings uses rounded light-green options, About displays readable image credits, and location search uses a single shared field and queries after two characters. Reviewed actual catalogue, Settings and About screenshots. Android CI captures the same screens separately for inspection.
- Local regression gates passed: 112 PostgreSQL/OCR tests on each SQLAlchemy family, TypeScript, npm, Expo compatibility and browser suites. Android 10 CI and measurement of the signed ARM package are separate gates. The requested mid-range physical ARM profile and real account deletion/receipt storage remain open.


### Preview008 optimization implementation and dry tests — 18 November 2026

- Applied local app changes on `codex/preview-008`: isolated overflow state and removed the modal fade, indexed prices by product and branch with expiration invalidation, skipped hidden search work, kept scoped catalogue data visible during refresh, and fetched stores and prices concurrently. Price applicability still depends on the visible locality's branches.
- Bundled all nine opt-in sample thumbnails and their credits. Replaced the runtime header with a 25,788-byte WebP and added 59,266 bytes of WebP samples. Compared with the prior 1,008,792-byte runtime header this is a net source-asset reduction of 923,738 bytes. Launcher icon and original artwork are preserved. Added bounded, URL-versioned native thumbnail caching for supported HTTPS images. Shared production catalogue still has zero assigned real photos and source reuse permission remains open.
- Same local Chromium setup, 16 opens per setting. Click to menu mount plus two animation frames at normal/4×/6× CPU throttle improved from medians of 36.1/63.1/91.1 ms to 21.0/22.2/31.3 ms. p95 went from 51.5/105.1/198.9 ms to 32.1/34.0/39.9 ms. A fresh browser context decoded all nine assets with app API requests blocked and showed About credits. TypeScript, unit checks, browser menu/layout/catalogue/network tests and mocked native thumbnail cache checks passed.
- Generated Android Hermes bundle and the Android 10 prebuild configurations for ARM64, x86_64 and ARM64 with R8/resource shrinking. Opt-in flags are `SPESTOVNIK_DRY_ANDROID_ABI=arm64-v8a` (or `x86_64`) and `SPESTOVNIK_DRY_ANDROID_SHRINK=1`. The default distribution configuration keeps its existing ABI support.
- Host is x86_64 and lacks Android emulator tooling and `/dev/kvm`. Available workspace storage was about 3.5 GB. The requested mid-range ARM, 8 GB RAM, 256 GB storage run and signed package-size measurements are pending. Use a matching device or an ARM-capable test host, repeat native menus, offline assets, cache and camera/receipt checks, and measure signed variants before changing default release packaging. No commit, push, deployment, or signed build.



### Preview008 performance, image and package investigation — 18 November 2026

- **Responsiveness.** Menu open is local. The overflow state lives in the top-level component, so opening it re-renders the catalogue, filters and groups up to 1,000 products, recreates the visible cards, and repeats per-card price/store scans. The native modal also fades. Local Chromium with a simulated catalogue, eight opens per setting, measured click to menu mount plus two animation frames at 33 ms median / 44 ms max at normal CPU and 67 ms / 91 ms at 4× throttle. These are browser smoke timings. Android frame profiling is pending. Separately, real catalogue snapshot reads returned 411 KB and 439 KB in 3.44 s and 3.12 s during the probe. A separate gzip probe transferred 42,850 and 55,131 bytes respectively. The app parses, validates and rewrites snapshots, resets visible data on some switches, and serializes stores then prices. Retried reads can extend loading during outages.
- **Recommended app work.** First isolate overflow state, memoize catalogue render inputs, and index eligible prices once per locality. Keep the last valid scoped snapshot visible while revalidating and fetch only data needed by the active screen. Measure before virtualizing the larger lists. Profile menu fade separately from the time to the first frame and to interaction readiness.
- **Images.** Shared Neon read-only counts and live catalogue snapshots agree on zero linked images for 1,000 groceries, 1,000 technology products and five fuel types (fuel count from Neon). The nine checked-in JPEGs belong to the server's opt-in sample catalogue. All nine public URLs returned HTTP 200 and fully decoded. A local browser decoded a sample with the API present and lost it when sample API requests were blocked. The mobile catalogue cache stores metadata and image URLs. The app has no guaranteed persistent thumbnail cache or bundled sample gallery.
- **Recommended image work.** Bundle only the existing approved sample gallery for offline first use, preserve sample labels and credits, and keep those records separate from offers. A scratch 240 px WebP conversion of the nine files reduced 256,833 bytes to 59,266 bytes. Visually check that conversion on device. Three Techmart product pages exposed image URLs and their source images decoded over HTTPS. The originals weighed about 0.90–1.14 MB each and reuse permission is unverified. For real products, pilot a small set of manufacturer or retailer images with exact product-code matching, documented reuse permission and source attribution. Store versioned, resized files under an owned HTTPS origin and cache them on device by content version, with a bounded disk budget and eviction. Fresh offline devices can show bundled samples. Real thumbnails become available offline after downloading. Missing or expired files keep a placeholder.
- **APK.** Downloaded and SHA-256 verified Preview007 before reading its APK ZIP directory. The signed universal APK was 75,567,529 bytes. Packaged native libraries by ABI used 18,103,152 bytes on arm64-v8a, 12,331,636 on armeabi-v7a and 19,517,112 on x86_64. DEX used 20,232,248 bytes. Removing both non-ARM64 library sets accounts for about 31.85 MB, implying about 43.72 MB before repackaging, signing and shrinking effects. A scratch header conversion from 1,008,792 bytes to 25,788 bytes shows a secondary saving. Preserve original icon and reference art.
- **Dry-test gate.** Before any real commit or release build, compare a clean baseline and isolated changes with the same Android 10 and ARM64 target configuration. Measure menu and Settings first frame/settled times, p50 and p95, frame overruns, and cold versus warm tab/load times. Exercise fresh offline samples, warm offline real thumbnails, failed image recovery, and price/store separation. Size trial sequence is universal baseline, same-source ARM64-only and x86_64-only packages, then R8 and resource shrinking, then derived header assets. Compare signed APK bytes, per-device AAB download and installed sizes separately. Recheck camera, image barcode decoding, receipt picker, localization and permissions with shrinking enabled. Keep x86_64 for emulator verification and 32-bit support if required. Review the Kotlin reference on the same ABI, signing and measurement basis before claiming a threefold comparison. No app/configuration change, commit, database write or build was made in this investigation.


### Preview008 recheck — 18 November 2026

- Active checkout: `/workspace/work/spestoslav`, `codex/preview-008`, based on `daa73ae` ([draft PR #19](https://github.com/Per5on/spestoslav/pull/19)). The committed head passed [backend CI](https://github.com/Per5on/spestoslav/actions/runs/44287192549). The [PR Android run](https://github.com/Per5on/spestoslav/actions/runs/44287192548) and [latest manual run](https://github.com/Per5on/spestoslav/actions/runs/44292063248) were skipped. The Android workflow auto-builds Preview007 PRs only and requires `confirm_build: true` on manual dispatch.
- Local backend changes prioritize exact and prefix locality names before substring matches, fix the foreign-key order for deleting receipt rows, require an explicit provider deletion confirmation, and map the provider's duplicate-registration response to HTTP 409. The deployed API still uses the earlier locality ranking. The live Neon Auth schema lists `/delete-user`; an authenticated real deletion has not been exercised.
- Local app changes replace the location dropdown with one shared input that searches after two characters, keep green focus styling in place of black button outlines, give Settings light-green rounded options, and present image credits as titles with links. Session restore offers a retry after an outage, sign-out retains the session when server revocation could not be confirmed, receipt upload distinguishes an accepted upload from follow-up read failures, and submission feedback belongs to the selected receipt. Reviewed the existing typed errors, image and permission notices, and retry body disposal.
- The local Android workflow is APK-only. No commits, pushes, deploys, APK builds, or publication were made during this recheck. Keep the review patch and this recheck separate from the verified Preview007 artifact below.
- Evidence: 112 backend tests passed locally on each SQLAlchemy family with disposable PostgreSQL 16 and Bulgarian OCR. The 16 targeted tests passed against PostgreSQL directly on both families. TypeScript, npm tests, Expo dependency checks, simulated Chromium workflows and public API read probes passed. Android prebuild in a scratch directory produced versionCode 8, versionName 0.5.1, and minSdk 29. Browser evidence is under `/workspace/work/spest-browser-*`; the direct account provider checks used mocks.
- Next gate: complete release-grade Android 10 checks on the final source and use an authorized throwaway account to verify real-provider deletion and private receipt storage. Account deletion during a concurrent upload and the retention/legal decisions in [ACCOUNT_DELETION.md](ACCOUNT_DELETION.md) remain open. Keep feedback delivery disabled.


### Review patch — 18 November 2026 (not yet built or verified in CI)

Applied on top of Preview007 source `5a1abb0`; **no sequence/version bump and no build was made** (sequences are immutable; a build needs a new sequence and the owner's confirmation). Details: [ACCOUNT_DELETION.md](ACCOUNT_DELETION.md) and the 18 November entry in [ACTIVITY_LOG.md](ACTIVITY_LOG.md).

- App: session restore warms the API and retries once after cold starts; typed `ApiError` and specific sign-in/sign-out/delete messages in six languages; receipt upload no longer reports failure after a successful upload; clearer camera-denied and no-barcode messages; retried 5xx bodies are cancelled.
- Backend: new `DELETE /api/v1/account` with tests (`tests/test_account_deletion.py`). Not run locally against PostgreSQL; the identity-provider `/delete-user` call is unverified against real Neon Auth.
- Tests: `test-cache.cjs` pins `esModuleInterop`; new `test-errors.cjs` is part of `npm test`.


### Latest verified artifact — Preview007

- App/runtime source `5a1abb0a76ecc41da4c46c00f49dc3c5e22778e0`; backend CI44149787804 and Android44149787807 passed. Final native log explicitly confirms decoded Food/Technology images and five fuel choices, ordered tabs, shared location, camera permission denial/preview, synthetic barcode-image decoding, language/About metadata. No fatal app exception asserted. This is not three complete release passes.
- [Download artifact ZIP](https://github.com/Per5on/spestoslav/actions/runs/44149787807/artifacts/14360295033). Signed test APK `spestovnik-preview-007.apk`,75567529bytes, SHA256 `36cf2c5bb17d9021bc0bf7edd0989907f9017218fc6ea9b646b235a50e9312ba`.
- Downloaded ZIP digest verified: `363266ab7a7125d1d1e91f5f04d8ec8193ede546854988eb063447236a527081`. Safely extracted to `/workspace/work/preview007-native-pass-03/`; embedded APK checksum matched; captured Android screenshot inspected. Prior attempts/artifacts preserved. Artifact expires17December2026; keep downloaded copy.
- Optional local browser live visual aid was blocked by this environment's Chromium trust store (`ERR_CERT_AUTHORITY_INVALID`); no TLS validation was disabled and this is not counted as a passing browser/live test. Python HTTPS asset checks and actual Android gallery tests passed. Existing mock browser checks remain separate evidence.
- No public release/tag or Google Play upload. Email intentionally disabled. Live-price/GTIN and successful real-account/private upload acceptance limitations below remain open.

### Current recheck checkpoint — 17 November 2026

Live evidence: API0.6, readiness,1000+1000 snapshots, five fuel labels, nine HTTPS images and credits passed. Sofia filtering returns46 grocery branches and zero technology/fuel branches; no fabricated local availability. Disabled feedback503; unauthenticated account/receipt access401; synthetic invalid sign-in401 (not successful account acceptance). Email intentionally excluded.

- Owner explicitly authorized the APK without an email provider; keep delivery disabled.
- App source `5a1abb0a76ecc41da4c46c00f49dc3c5e22778e0`: backend CI run44149787804 passed. Fresh Android run44149787807 is in progress; previous successful APK is retained.
- Native checks now require decoded sample images in both Food and Technology, plus all five fuel labels; these passed on Android10. Do not weaken assertions to mask deployment or image failures.
- Backend source `557d900819d5c7194f49402ac11e09b75f37010a`:100 PostgreSQL/OCR tests and both SQLAlchemy CI legs passed; merged via PR17 as `9ba223de25942d2c1e862b49a5ca93087f24d9c9`.
- Found/fixed raw SQL transport doubling percent signs in two isolated trial product names. Versioned renderer now uses named-parameter dialect; tests cover all1000 source identities and repeated transport preserving existing flags/barcodes/aliases/brands. Shared import used corrected SQL only.
- Actual shared sync is complete, repeatable, and contains no price or barcode inventions. Inventory PR15 remains separate.

### Latest owner instruction: rerun checks and build without email

Build authorized; email provider intentionally excluded from this preview and is NOT a build blocker. Keep FEEDBACK_DELIVERY_ENABLED=false. Preserve the provider adapter for later private setup; do not ask for keys now. Rerun and inspect actual tests/native artifacts, retain previous builds and report live data limitations. Source transport audit corrected two doubled-percent catalogue names on isolated validation only; versioned renderer/regressions now pass100PostgreSQL/OCR tests. API0.6readiness and catalogue sync must remain explicit; no live-price claims from metadata.


## Current outcome and authorization

- The owner **authorized committing and building Preview007**, with real functionality and connections. Do not ask for the same build permission again. Do not describe mocks, metadata or green CI as proof of complete live readiness.
- **Preview007 APK built, signed and passed Android 10 smoke tests.** It is an internal test artifact, not a published release and not yet a fully live acceptance result.
- The connected API serves **0.6.0** after backend PR #17 merged as `9ba223de25942d2c1e862b49a5ca93087f24d9c9`; Render deployment `dep-dbua0l6k1f9s739t83d0` is live and `/ready` succeeds.
- The owner chose **free HTTPS email delivery**. Brevo adapter implemented; owner explicitly answered **“Not yet”** to account/sender verification and private API-key setup. Email delivery must stay unavailable until those steps and a real delivery test complete. No paid upgrade is authorized.
- Shared Neon catalogue sync completed in one guarded transaction and was replayed unchanged: 1000 groceries, 1000 technology products, five fuel labels; 139 stores / one inactive and zero current prices. Original grocery/store hashes preserved. Recovery `br-ancient-wildflower-bambdbd4` retained. PR #15 five-store inventory import remains unapplied.
- Preserve published Preview005 and all previous APKs/reference images. Preview006 work remains separate. Google Play testing follows Preview007 and has additional release/privacy/signing gates.

## Branches, worktrees and PRs

| Lane | Worktree / branch | Current evidence |
|---|---|---|
| Android/app | `/workspace/work/spestoslav-preview007`, `codex/preview-007` | [PR #16](https://github.com/Per5on/spestoslav/pull/16), app commit `5a1abb0a76ecc41da4c46c00f49dc3c5e22778e0`; backend CI44149787804 passed, Android44149787807 passed. Previous48c7442 native pass retained. |
| Backend rollout | `/workspace/work/spestoslav-preview007-api`, `codex/preview-007-live-api` | [PR #17](https://github.com/Per5on/spestoslav/pull/17). Head `557d900819d5c7194f49402ac11e09b75f37010a` passed100 tests and both SQLAlchemy CI legs44121768070; PR merged as9ba223de, deployed live. |
| Grocery store inventory | `/workspace/work/spestoslav-inventory`, `inventory/reconcile-pr2-pr12-20261117` | [PR #15](https://github.com/Per5on/spestoslav/pull/15), `15ea1f61e4b4f8ab86d0cb89d6a5b6b3063fdb7b`, exact-head CI passed. No shared import. |
| Older preserved checkout | `/workspace/work/spestoslav` | Older005 source and local assessment notes. Use the active worktrees above; do not reset/delete this checkout or its edits. |

Main was `39304dc` when the rollout branch was prepared. Check current refs/working trees before editing. PR #15 inventory and PR #16 app must not overwrite the newer HTTPS feedback implementation when branches are later reconciled.

## Confirmed design and product decisions

- Keep Expo54 / React Native / TypeScript and FastAPI / Python / Neon PostgreSQL / Render. No Flutter or architecture rewrite.
- Green header, orange selections; golden money-bag/coins logo. Piggy-bank artwork and old previews remain archived, not active branding.
- Four upper tabs: **Храни, Техника, Горива, Моят списък**. No Home category or lower ribbon. Location search is by settlement only; no postcode UI/storage or invented GPS/radius/directions.
- Three-dot menu with scan, login, receipts, Settings and About; Feedback is inside About. Font/language/Terms/Privacy are in Settings.
- Six interface languages: Bulgarian, English, German, Spanish, French and Russian. Actual app text increases by1logical point at every saved size setting. Legal text currently has BG/EN versions with an explicit fallback in the other interface languages.
- Photos are illustrative examples and need not depict the exact product. Keep attribution and clear labels; never convert an illustration into a verified SKU/price claim.
- No CAPTCHA or CAPTCHA verification. Feedback recipient is fixed server-side to **ivo77@duck.com**. Credentials stay out of chat, source, APK and logs.
- Developer: **Ivaylo Yovchev**. Legal framework: **EU**. Do not invent a specific member state or postal address. Operator/contact/retention/provider details still need finalization before public testing.

## Complete task checklist and current results

| Task | Result / status |
|---|---|
| Remove Home and postal functionality | Already retired through0006; do not rerun retirement SQL. Empty deprecated `postal_codes` response field remains only for older-client compatibility; no postal search/storage restored. |
| Four tabs, My List moved up, lower ribbon removed | Implemented and checked in browser/native navigation. “Техника” uses title case. |
| Narrow header/location/search controls | Header top padding15→10; compact shared settlement-only picker and search. Existing approved layout preserved. |
| Food/technology action rows | Stores precedes Products, then snug Refresh; first two controls share available width. Responsive labels and wrapping passed narrow320px/130% checks across six languages. |
| Fuel action row and five choices | Stations / Fuel / Refresh; five choices implemented. Underlying canonical grade metadata passed local tests and two isolated Neon imports; not yet imported into shared preview. No prices inferred. |
| Remove black Refresh outline | Done; thin green border/focus styling retained. Native screenshot inspected. |
| Larger thumbnails and cart feedback | Thumbnail component/failure fallback implemented; adding to list flashes green for one second. Sample galleries verified in browser and all nine live HTTPS assets fetched successfully; enhanced native decoded-image checks passed in run44149787807. |
| Product search and selection | Typed-query-only apply, multi-selection, pending selections across queries and clear/category reset fixed; regression tests passed. |
| Actual font +1pt and button autosizing | Implemented for actual app text at every setting. Font/model tests and narrow layout checks passed. |
| Settings, languages, About, Feedback placement | Implemented; menu and persistence tests passed. Native language/version/About checks passed. |
| Grocery catalogue |1,000 source-backed Burlex identities, six approved groups, bounded metadata caching/pagination. Shared preview has these identities. This is not1,000 verified barcodes or current offers. |
| Technology catalogue |1,000 distinct Techmart codes/names, source URLs and five groups documented. Isolated Neon import repeated with identical product hashes; shared preview still has0technology products. |
| Required technology chains | Zora, Technopolis, Technomarket, Techmart, Vali, Ardes, JAR Computers documented. Existing shared directory has six of these; new Techmart directory insertion passed local and repeated isolated-Neon tests; shared Techmart identity inserted safely; no locations invented. Preserve other existing chains and inactive state. No synthetic branches imported. |
| Required fuel chains | Lukoil, Petrol, Shell, EKO, OMV, Rompetrol all exist in the shared directory; other existing chains retained. Physical coverage and verified prices remain partial/absent. |
| Five fuel records | Owner-approved Бензин95, Бензин98+, Дизел, Дизел+, Автогаз taxonomy added in `data/fuel/types.json` / `scripts/import_fuel_types.py`; four safety tests and two isolated-Neon imports passed. No shared import yet; no station/GTIN/price claims. |
| Sample image database |3original grocery references preserved plus6licensed Commons technology illustrations;9assets/credits/hashes checked. Sample mode defaults off. Server endpoint availability was saved after proving explicit opt-in, `is_demo=true`, `verified=false`, no price and comparison exclusion. Configuration saving is not deployment verification. |
| Barcode and camera | GTIN validation, manual/image/camera paths, unknown-code review and denied-permission fallback implemented. Native camera denial/preview and actual synthetic-image decode passed. Browser synthetic camera decode passed. Real GTIN coverage remains0; physical-phone testing still needed. |
| Receipts and OCR | Private upload, async I/O, idempotent request handling, Bulgarian OCR, item confirmation/moderation and owner deletion tested locally/mock. Actual managed-account/private-storage/worker flow after deployment still needs live evidence. |
| Comparison | Full-basket/unit-price/location isolation and missing-coverage behavior tested with synthetic data. Shared preview has0current prices; do not claim live cheapest-store coverage. |
| Free shop routing | Planned; synthetic4km matrix simulation tested. Real GPS/navigation/route service is not implemented. |
| Feedback transport | SMTP adapter tested, but Render Free blocks465/587. Owner chose Brevo HTTPS; adapter and failure/privacy tests passed. Sender/key setup not done; delivery explicitly disabled. Never claim inbox delivery from provider acceptance alone. |
| Terms and privacy | BG/EN draft generated from one app JSON source; Settings links, illustration clause and unsent feedback-draft preservation tested. Final operator/provider/retention/transfer/account-deletion details remain pre-Google-Play gates. |
| Native networking failure | First007build compiled/signed but location lookup failed after75s; screenshot showed catalogue/location network errors. Added bounded safe-read retries covering body timeouts, cancellation and transient502/503/504; writes never automatically replay. Failure-injection browser/unit tests passed; corrected Android run passed. No TLS bypass or weakened location assertion. |
| Code/CI cleanup | Empty schemas module removed, duplicate httpx dependency cleaned, imports/router inclusion organized, preview metadata centralized, generated diagnostics ignored and artifact upload uses warn. Keep intentional imports/web dependencies/Expo system UI/saved-list storage key. Do not remove used `comparison.cheapest`. Archive/changelog consolidation remains secondary pending work. |
| Optimization trial | Asset/ABI accounting and SDK flag validation done only. Derived header17,236bytes versus1,008,792original; non-ARM64 native bytes about31.85MB. ABI-separated signed builds, R8/resource shrinking and runtime measurements are NOT implemented/verified yet. |
| Pricing/push monetization | Core/free approach retained; paid notifications deferred. No payment/push rollout performed. |
| Final three-pass release gate | NOT complete. Individual backend/browser/native checks are evidenced; do not relabel them as three complete final-source/live passes. |
| Google Play test preparation | Pending after007: verified sources/links, real account/receipt/email/location checks, final privacy/account deletion, signing and release review. No publication performed. |

## Inventory reconciliation result — separate lane

- PR #15 merged current-main compatibility into its branch and resolved the retired postal-column conflict. Integrated seed:143rows,13current columns,9CBA,35uniquely matched locality triples, no normalized duplicates.
- Fresh shared baseline:139stores,139linked,138active. Row-level result: **138unchanged,5net-new candidates,1inactive Mini Mart retained outside seed**. Do not infer additions by143minus139.
- Mini Mart Hristo Botev75 is still absent from the current locator and present in the older page: pending/inactive, **not confirmed closed**. Current feed357raw records; IDs75/118 duplicate Patriarch Evtimiy61, retained once.
- Four officially closed T MARKET addresses are absent from the seed/preview. Seven suggested alternative stores are not seven proven one-to-one relocations. New Bansko address and relocated Teteven address verified; old Teteven address unspecified and not invented.
- Five candidates: T MARKET Bansko/Teteven and three CBA Bansko/Blagoevgrad addresses. Safeguarded local replay139+5→144total/143active on both schemas, every original row retained, second run unchanged. Shared import still pending.
- Evidence: [Issue #14](https://github.com/Per5on/spestoslav/issues/14), [PR #15](https://github.com/Per5on/spestoslav/pull/15), [exact-head CI](https://github.com/Per5on/spestoslav/actions/runs/44096315610), reconciliation document on that branch. Keep the importer’s explicit `legacy-preview` mode for this shared legacy schema.

## Exact verification and artifacts

| Evidence | Result |
|---|---|
| App source48c7442 backend CI | [44105274087](https://github.com/Per5on/spestoslav/actions/runs/44105274087), SQLAlchemy2.0/2.1 passed. |
| First native attempt3867e5e | [44098576002](https://github.com/Per5on/spestoslav/actions/runs/44098576002): APK compiled/signed; failed Sofia lookup. Retained for diagnosis. |
| Corrected native source48c7442 | [44105274182](https://github.com/Per5on/spestoslav/actions/runs/44105274182): passed Android10navigation, real locality selection, camera permission/preview, image barcode decode and language/version checks. |
| Successful007artifact | [Download ZIP](https://github.com/Per5on/spestoslav/actions/runs/44105274182/artifacts/14338178842). APK75,567,381bytes; test signing, not Google Play upload signing. |
| Successful APK SHA256 | `3c39c2e386fd42908d4da36a4c3c3d78a3b4b5df3877d82d20cffc3c0a77f664` — downloaded checksum verified. |
| Backend rollout43b239d | [44112851589](https://github.com/Per5on/spestoslav/actions/runs/44112851589), exact-head CI passed. |
| Latest backend metadata codef28fe64 | **98local PostgreSQL16/Bulgarian OCR tests passed**; [exact-head CI44115959801](https://github.com/Per5on/spestoslav/actions/runs/44115959801) passed. |
| Frontend checks | TypeScript, model/cache/metadata/font/network/legal-sync tests passed. Functional, menu, legal and complete workflow browser suites passed without JS errors; injected transient/permanent network failures verified. These use labelled simulations. |

APK preview metadata: sequence007, app version0.5.0, versionCode7, nameСпестовник07. API version0.6.0 is independent of app version. Use the007branch workflow, not main’s older Android workflow. No007GitHub release/tag or Google Play upload exists.

Local evidence: `/workspace/work/preview007-native-pass-02/`, failed `/workspace/work/preview007-native-attempt-01/`, `preview007-network-regression-02/`, `preview007-functional-network-fix-01/`, `preview007-neon-validation-evidence.json`, and `preview007-api-final-metadata-tests.log`. Keep sequences immutable.

## Deployment and database state

- Render: owner-confirmed **My Workspace** `tea-dbqur9jrjlhs73cga8eg`, service `srv-dbs313ei0phs73bvvd00`, https://spestoslav-api.onrender.com . Live source9ba223de/API0.6.0, deployment dep-dbua0l6k1f9s739t83d0. Readiness, both1000-item snapshots, nine HTTPS images and feedback availability verified after deployment. Initial transition probes timed out; subsequent full probes passed.
- Service tracks **main**. Although metadata says autoDeploy=yes, no automatic deploy queued; public-Git-URL services require manual deployment per Render documentation. Backend PR #17 merged as `9ba223de25942d2c1e862b49a5ca93087f24d9c9`; Render deployment `dep-dbua0l6k1f9s739t83d0` is live, API0.6 and readiness verified. Deployment was monitored to `live`; public workload/endpoints verified against the resulting source.
- Saved configuration: Brevo provider, deliverydisabled; sample endpoint enabled only after opt-in/isolation evidence was accepted by automatic review. Existing unrelated variables preserved. No password/key values recorded here; a saved setting is not proof it is active in the running deployment.
- Neon project `long-resonance-77491878`, database `bgprices`, shared preview `br-snowy-morning-baym8iw6`: checked after guarded sync:1000groceries,1000technology,5fuel products;139stores/1inactive;5291localities;0current prices. Techmart identity inserted without any invented stores; existing grocery/store hashes unchanged.
- Isolated validation `br-polished-unit-bafzpcnc`:0008+1000technology identities/products tested twice. Product hashes identical; grocery/store hashes match shared preview. Techmart/five-fuel additive statements passed twice on this clone:1000technology products,5fuel grades,1active Techmart identity,139stores/1inactive and0prices. Shared application completed with repeated-import catalogue hash `3a0e57412404b37aab7fde8c0f190bc2`; original grocery hash `3fba65f409a580ac675785c9b3de05b9` and store hash `04e63b3a71007f354ce79db77a06d8be` preserved.
- Recovery copy `br-ancient-wildflower-bambdbd4` (`recovery-before-preview007-a96f741`), no compute, retained before shared writes. Older recovery `br-silent-leaf-bajr7isp` retained. No branch deletion/purge authorized.
- Runtime model/schema comparison found only unused legacy `user_submissions.locality_id` absent; no active route uses it. Do not add/drop speculative legacy fields.
- Fuelo public access/API key remains unavailable; no verified station-price integration. Official directory links/chain identities are not proof of real-time price/stock coverage.

## Exact next actions

1. Fresh Android run44149787807 passed for app5a1abb0; APK, logs/XML/screenshot inspected and checksum verified. Provide artifact14360295033 to owner. Email is explicitly excluded; do not block on setup or ask again for build permission.
2. Handoff/status/activity updated with final source, test and artifact evidence; preserve these checkpoints. Backend557d900/100tests/CI44121768070, shared repeatable sync and live API0.6 deployment9ba223de are complete. Do not repeat shared writes just to resume work.
3. Keep deliverydisabled. Brevo private account/sender/key setup and real delivery acceptance are later work, not this APK's gate.
4. Successful managed-account/private receipt/storage/worker acceptance and physical-device testing remain to be evidenced with legitimate fixtures. Rejection boundary checks, mocks and local tests are not successful live account/upload proof.
5. Complete measured optimization/header/ABI/R8 trials and three separately evidenced complete final passes before claiming full release readiness. Preserve all numbered releases and do not publish to Google Play as part of this build.
6. PR15's separately reviewed five-store inventory import remains unapplied. Complete privacy/account-deletion/signing/verified-price-source requirements before the Google Play test build after007. There are currently zero verified live prices and no verified GTIN coverage; do not misrepresent catalogue metadata as live offers.

## Guardrails and useful references

No fabricated branches, coordinates, GTINs, live prices or closure status. No CAPTCHA. No automatic paid upgrade. No bulk seed replacement, locality/barcode/table/receipt purge or recovery-branch deletion without a separately approved measured proposal. Keep saved-list key `spestovnik-preview-001`. Do not remove `comparison.cheapest`, active web-preview dependencies or intentional package imports.

See `PREVIEW_007_API_ROLLOUT.md`, `FEEDBACK_SETUP.md`, `TECHNOLOGY_1000.md`, `RETAILER_SOURCES_007.md`; app-branch `PREVIEW_007_PLAN.md`, `PREVIEW_006_BACKLOG.md`, `TERMS_AND_PRIVACY.md`, and inventory reconciliation docs on PR #15. Shell GitHub REST credentials expired during this session, but git push and the GitHub connector still work; use connector tools for CI/PR/artifact reads rather than exposing tokens. Direct shell PostgreSQL failed; connector transactions worked. Keep credentials private and distinguish local, CI, deployed and live-data evidence in every status report.
