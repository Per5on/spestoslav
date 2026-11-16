# Project activity log

Append dated entries. Keep the current resume point in `PROJECT_STATUS.md`; older entries are historical evidence, not current test/deployment claims.

## 16 November 2026 — Preview 006 backlog and initial backend triage

- Owner reported Settings visual requirements (black text/white background, compact button icons, optional two columns), missing stores/stations/images and slow locality search. Created `docs/PREVIEW_006_BACKLOG.md` with backend-first investigation, frontend follow-up and three-pass release gate. Linked it in Codex handoff.
- Source review: `mobile/src/catalog/useCatalog.ts` initializes stores empty and fetches them **only if localityId exists**; fuel skips product loading. `LocationPicker.tsx` debounces 300ms but permits a 60-second timeout. These are code-level findings, not proof of live root cause.
- Render service inspection: `spestoslav-api` is configured to deploy from `main`, not either feature branch; its health-check path remains blank. Recent application logs show successful HTTP 200 for paged grocery products and a fuel stores request, but HTTP 200 does **not** establish nonempty response bodies. Further response-count and latency checks are required before declaring backend healthy.
- Preview 005 release remains published; do not modify its artifacts. The post-preview branch is experimental and not release-ready.

## 16 November 2026 — post-preview branch isolation (not a release)

- Owner instructed: leave Preview 005 verification and realization pending on PR #9, and create separate source tree `Test_postpreview-005` for Issue #10 toolbar/feedback work. Opened draft PR #11 against Preview 005 branch; no application changes or numbered APK publication have yet occurred on the new branch.
- Post-preview candidate may become Preview 006 **only by later owner decision** after three full verification passes and a fresh 006 build with updated metadata; it must never replace or masquerade as Preview 005. Earlier numbered releases remain untouched.
- Added a GitHub Actions job-summary/log note for post-preview builds and disabled automatic numbered release publication on this branch. Preview 005 remains independently pending.


## 14 November 2026 — recovered conversation and backend rollout

- Owner requested handoff/Issue #1 review, latest-main inventory work (Mini Mart, T MARKET, CBA), official-source checks, preview DB sync and PR evidence; preserve Android UI during backend work.
- Backend audit repaired locality/database compatibility, Alembic/model consistency, psycopg URL handling, verified/fresh price visibility and authenticated write/review/receipt flows. Separate PR #2 holds inventory research; PR #3 merged backend work, followed by merged PR #4 for scoped GitHub OIDC receipt OCR.
- Owner explicitly selected Render My Workspace. Deployed API reached 0.4.1; exact earlier test/deployment details are in `BACKEND_READINESS.md` and merged PRs. Historical six-test/47-test claims are superseded by later 58-test coverage, not evidence for future code.
- Owner suggested Fuelo; official API/terms checked, station access requires a key the owner does not have. Adapter remains disabled; pending unknown-certainty observations cannot become verified station prices automatically.
- Owner supplied two DOCX references, the three-screen illustration and gold piggy-bank logo. Confirmed green header/orange selections and four tabs plus separate searchable location dropdown. Preserved original assets and recorded `FRONTEND_BRIEF.md`.

## 14 November 2026 — numbered preview and Android build

- Owner requested a testable artifact and sequential preservation. Created immutable interactive preview 01 using a backend snapshot, supplied logo/photos, four tabs, shared locality, product multiselect, list controls and honest missing-data/scan states.
- Preview interaction checks passed, including narrow widths, state saving and no external runtime requests.
- Owner requested an APK and authorized implementation. Added native screens/live reads, saved basket/locality, manual barcode lookup and standalone APK CI, separate package `bg.spestoslav.preview`. PR #5 opened.
- Fixed two real build failures: obsolete SDK `tools` package in setup action and an incompatible transitive expo-font peer; pinned SDK 54-compatible fonts. A duplicate same-code build was canceled, not claimed successful.
- Final preview 001 build 43600409741 at 5daa807 passed standalone compilation, signing verification and Android 10 launch/tab/basket/scan-label smoke checks. Backend matrix 43600409766 passed both SQLAlchemy families.

## 15 November 2026 — continuity and comprehensive cleanup

- Owner requested that the project remain ongoing with persistent notes, then requested a beginning-to-current audit, fixes, unnecessary-code cleanup and readiness before giving the next feature step.
- Reviewed conversation/reference extracts, Issue #1, handoffs, current source/PR/build status. Added repository entry instructions and persistent checkpoint/log rather than relying on a process staying open overnight.
- Downloaded preserved preview 001 via GitHub connector after shell artifact host denied access; checksum matched. Inspected actual emulator screenshot. Prerelease asset upload failed with HTTP 401; publication remains unverified.
- Audit fixes in progress: unused/duplicate Python imports; bounded receipt queue locking; transliteration filtering; basket limit; redundant state/request work; outdated docs/actions; patched Python dependencies; compatible JS dependency fixes and guarded build-tool patches. Preserve 001; cleaned build becomes 002.
- Next: finish/verify corrections, commit/push PR #5, wait for exact-code CI and emulator results, append final evidence and mark audit ready. No new feature phase until owner's next instruction.

### Verified audit completion

- Cleaned application source `91ea05e`: backend run 43704406362 passed 58 tests per PostgreSQL matrix job; Android run 43704406411 passed standalone build/signature/emulator checks and published 002. PR #5 merged as `ca7f4c5` under the existing rollout authorization.
- Published APK 002 digest `693c45f72c197cc4cf205a3f61daeba8fb8901a15ff2fbc8222a5adcc4218e3e` matched the downloaded artifact. Preview 001 and source artwork remain preserved. Browser regression and warm live-read/auth-denial checks passed; real prices remain unpopulated.
- Fixed two canonical region aliases in the seed; all 116 rows validate against locality triples. Updated vulnerable Python/build dependencies and applied tested guarded compatibility/security patches. npm reports the upstream deepmerge version despite the local fix; no zero-advisory npm claim.
- Render monitoring found an empty HTTP health-check path and no recent error-level logs. `/ready` itself passes. The connector cannot edit service settings; this one external configuration item is explicitly unresolved.
- Saved the final checkpoint and an idempotent release guard: documentation-only changes preserve existing app-tree assets rather than overwrite them. The next changed app release is 003.
- Next: verify the latest main CI/deploy state at session close, then **wait for the owner's next development instruction**. Keep this project ACTIVE and resume from status/log, not from the full historical conversation.

### Scheduled-worker final check

- Discovered the latest scheduled OCR run failed on a 30-second read timeout during API startup (run 43699395724). Corrected the runner with a bounded read-only warm-up before identity/claim requests; never retry a mutation that might already have claimed work. Two regression cases cover timeout/503 recovery and bounded failure.
- Next validation gate: current-main backend matrix plus an actual manual-dispatch OCR run; retain their linked outcomes before final readiness. Android 002 source/artifact stays unchanged.

### Runtime verification and pause point

- Worker follow-up `b87423b`: 60 tests per PostgreSQL matrix job passed (43705642152); real authenticated OCR run 43705642164 passed with 0 queued jobs. Cold-timeout behavior has mocked regression coverage, not a claim of full OCR accuracy.
- Render had queued no automatic update; clean rebuild `dep-dbsor8gn74is73ag7b9g` reached live on exact runtime commit `b87423b`, with Pillow 13.0.0 confirmed in build logs. Post-deploy public reads/readiness and authentication-denial checks passed. Final continuation commits are documentation/release metadata only.
- Durable original inline preview copied unchanged to `docs/references/preview-001.html`; `preview-sequence.json` records 001 and 002, next 003. Published APK 002 link/hash are in the checkpoint.
- **ACTIVE, audit complete; await owner's next instruction.** Do not restart history review, implement additional features or claim the unresolved Render health-check setting was changed. Recheck latest CI/deploy state on resume and read only missing detailed references as needed.

## 15 November 2026 — preview 003 requested and implementation started

- Owner removed Home and its related data, lower ribbon and postal search/storage; ordered upper tabs Food/Technology/Fuel/My list. Requested three-dot settings, six interface languages, saved font size, compact header/search/location, larger photos, one-second green add feedback, money-bag sample logo and an actual snapshot. This supersedes earlier visual decisions.
- Added source migration 0006; isolated Neon transaction on br-crimson-feather-balgu231 removed Home/postal while retaining all 5,291 localities and 139 branches. Catalog went 38 to 29 retailers (nine Home entries), with no Home products/branches/receipts to remove in the actual shared snapshot. Created no-compute recovery copy br-frosty-star-badgjcyw. Shared DB is unchanged until new API rollout.
- Implemented the UI and extracted money-bag logo from the supplied reference. Old active piggy asset removed; historical source images/001/002 artifacts preserved. Added complete UI dictionaries for six languages, font preferences, name-only picker and larger product photos without taller default cards.
- Local TypeScript/model checks and real-API browser regression passed, including flash duration, preserved selection/basket/preferences, all six languages and narrow/large-font layouts. Final native/PostgreSQL CI, staged shared migration and snapshot remain the next gates.

### Preview 003 completed; owner refined the catalog row for 004

- PR #6 source 293c4be: PostgreSQL CI 43709020828 passed 61 tests in both SQLAlchemy jobs; native build/signature/Android 10/publish run 43709020956 passed. Published immutable 003, APK digest bf02e1ec78f6d1b140fa6b92ff702a30c3aa2fa2279f2cabf465d688a7837f58, and inspected actual emulator image.
- Merged 538bd9a and deployed API 0.5.0 as dep-dbsppd8n74is73aimkc0. Only after version/readiness/name-only checks passed was the tested shared retirement transaction applied. Verified 5,291 localities/139 branches unchanged, 29 retailers, Home zero and postal storage zero. UUID/address digests match pre-change; locality CSV identity digest matches DB.
- Owner asked Products/Stores to move before Refresh on one row, then asked automatic button-font sizing. Implementing as 004 to preserve already published 003. Compact toolbar removes one full row; shared button/tab text fits readable single-line labels while retaining 44-point targets. Live-API browser tests passed all languages at 320px and 130% font, plus prior functionality; native 004 checks and final snapshot are next.
- Architecture question answered: React Native/Expo/TypeScript + Python/FastAPI; Neon PostgreSQL and Render. Node.js is app/build tooling, not the API backend.

### Preview 004 delivered; next step pending

- PR #7 source bbc7b9a merged as 332ae57 after backend 43711564924 (61 tests per matrix job) and Android 43711564982 passed. Verified downloaded APK checksum 20e0e265ce8ed0e421c3a4b5d72f8bdcabb1cfe6b132bcc7e7a041230fbfc5e9 and inspected actual Android 10 image. Release android-preview-004 is public; 001–003 remain unchanged. Catalog and durable snapshots updated; next version 005.
- Shared backend/data/scripts are identical to live 538bd9a; public readiness passed, no repeated migration/deployment. Updated stale checkpoint Home/postal/deployment wording.
- Owner deferred other tab button layouts and asked about comparison/API complexity. Explained existing comparison foundation, need for reliable verified feeds and product matching, and retailer-by-retailer access uncertainty. Do not start new integrations without the next instruction.
- ACTIVE, current requested refinement complete. Resume from this checkpoint and linked results, preserving all numbered artifacts.

## 15 November 2026 — grocery categories approved; monetization under review

- Owner approved the proposed grocery category structure. Target remains 1,000 verified grocery records, with generic search groups, exact product identities and retailer offers separated. No bulk import or source integration has been executed under this review.
- Reviewed uploaded monetization notes (Поставен текст.txt, file_000000001ba0821087dde4ea5ff6b08a). Owner is considering paid price alerts; pricing and feature limits are proposals, not approved implementation.
- Recommendation for evaluation: useful free comparison/scanning/list with 5 tracked products and a digest; Plus hypothesis EUR2.99/month or EUR24.99/year with 50 tracked products, thresholds and notifications after verified source updates. No guaranteed instant delivery, invented historical lows or promised retailer affiliate access. Route optimization remains outside current scope.
- Official Google Play service-fee page checked: EEA auto-renewing subscriptions currently show 10% service plus 5% Play billing; paid digital features need compliant billing. Firebase Cloud Messaging itself has no usage charge; ingestion, operations and subscription verification still cost money. Affiliate commission/feed access requires individual program verification.
- Next: finish review of owner's instructions and source feasibility before altering app/database. Categories approved; monetization not approved. Preserve preview004 and next build005.

## 16 November 2026 — recovery/status check for unfinished 005

- Owner asked whether yesterday's work finished. Inspected actual branch/files and handoffs; older checkpoint had not captured the latest implementation, so corrected both entry points now.
- Branch codex/preview-005-grocery-workflows has uncommitted catalogue/schema, cache, authentication, camera and receipt changes. Official Burlex source yielded 1,000 grocery records in six groups, excluding household/tobacco; no imported prices, no verified GTINs. This is retailer-scoped source coverage, not a balanced nationwide top-1,000 claim.
- Isolated branch br-ancient-shadow-balr2n5l and synthetic Auth session probe prepared; provider requires signed session cookie for JWT exchange. No shared preview alteration for 005.
- Last attempted isolated migration/import stopped with KeyError DATABASE_URL before SQL. Full tests/simulation, Bulgarian OCR, native camera verification, PR/build/rollout remain unfinished. Earlier local passing tests are intermediate evidence only.
- Owner clarified free shop routing should be planned. Keep paid alerts/subscriptions deferred. Next action: fix isolated configuration loading and complete current-tree verification, including private receipt ownership, review-before-price publication, scanning permissions/decoding, cache freshness and comparison. Keep numbered previews intact.

### 16 November — resumed; build hold and next issue

- Owner explicitly requested no build commits/builds until fixes are complete or permission is given. Keep all source changes uncommitted and do not compile/publish APKs or start release CI until the owner confirms. Continue local verification only.
- Owner queued Issue #8 after current feature work: exact overflow-menu order, nested Settings, Feedback and About with dynamic installed Android version and exact Vimp ownership notice. Read issue and retain it as next task; no Profile section.
- Fixed isolated environment loading by parsing configuration as data (connection URL contained shell metacharacters). Direct Postgres transport is unavailable here; applied additive 0007 only to the isolated Neon branch through the connected SQL service. Local disposable PostgreSQL16 container is available for actual ORM/migration tests. No shared preview changes.

### Owner queue — task 3 after Issue #8

- Sequence: complete current catalogue/scanning/receipt/comparison fixes and local tests; then Issue #8 overflow/Settings/Feedback/About; then requested tab/header refinements. Build/commit hold remains effective.
- Task 3: reduce empty header padding above title by one third; Bulgarian Technology caption Техника; grocery toolbar Магазини, Продукти, Обнови; first two equal widths, Refresh intrinsic label width plus 0.5 logical points while retaining accessible touch height. Clone row to Technology, replacing prior controls. Fuel toolbar Бензиностанции, Гориво, Обнови, with fuel dropdown Бензин 95, Бензин 98+, Дизел, Дизел +, Автогаз. Source reference Fuelo, no invented live prices.
- Confirmed task 3 is clear; camera is native phone functionality, backend handles identification/validation/private receipt workflows. No redundant second camera implementation planned.

## 16 November — feature/UI checks and preview004 cleanup complete; build authorized

- Completed current catalogue/camera/receipt/comparison work, then Issue#8, then task3 in the owner's order. Browser scenario decodes actual synthetic camera frames/image EAN, submits unknown-code review, privately uploads a receipt, runs real Bulgarian OCR, confirms unit price, moderates, updates comparison, deletes privately and restores metadata cache. Permission-denial/manual fallback and private-session isolation pass. No JavaScript errors. Separate menu/preferences and320px/130% six-language toolbar checks pass.
- Real isolated managed Auth signup/login/JWT/restore/logout passed. Source-backed data imported idempotently on local PostgreSQL and isolated Neon0007 only:1,000names/6groups/5,291localities/139branches/0prices/0barcodes. Shared preview remains unchanged. Initial environment-loader/TCP issue resolved via data parsing plus connected SQL service; no shell-sourced secret URI.
- Backend suite79 passes in both SQLAlchemy2.0.44 and2.1.8 locally. Latest existing-main CI43734792143 atc91f356 also passed both version families; stable2.1.8 exists on PyPI. Fast-forwarded the branch to that README-only main commit without creating a new commit.
- Applied cleanup effects and reviewed conditional items. Both uploaded patches are byte-identical SHA2560efb53858304f3456a4196addfd23b78d6690b382ec38cd1e4f2716ff9004f20. `cheapest: unknown` explicitly retained after owner correction. SQL scripts execute intact online/offline, artifact diagnostics warn, workers share API URL with a receipt opt-out, empty schema module/duplicate dependency/default React imports removed, smoke output sequence required, main router setup consolidated. Keep postal shim, active web dependencies, saved-list key and legacy bootstrap reference for documented reasons.
- Consolidated active release notes in CHANGELOG; original details/handoff preserved under archive. Introduced mobile/preview.json as candidate metadata source; Expo/workflow/registry checks prevent numbering drift. Config inspection resolves Спестовник05,0.3.0/code5,minSdk29 without building.
- Owner explicitly lifted the earlier build hold: build005 after all checks pass; do not request confirmation again. Preparing actual Android permission/camera/image-decoder/About checks before the first005 build. No005 PR/APK/deployment yet at this entry. User requested an immediate browser screenshot while the APK is not ready.

## 16 November — Feedback moved into About

- Latest owner instruction supersedes Issue #8's original top-level Feedback position: overflow now contains Scan, Receipts, Sign in, Settings and About. About contains the translated Feedback button; Back from Feedback returns to About. Existing unconfigured-channel message is preserved.
- Updated browser regression to check nesting and Back navigation in Bulgarian and English. Preview005 remains the unreleased candidate; no published artifact was overwritten.

## 16 November — preview005 build started on owner authorization

- Owner confirmed to proceed after cleanup. Final TypeScript, npm model/cache/metadata checks, native smoke Python compilation, preview metadata consistency and git whitespace checks passed. Bulgarian/English browser menu regression passed including Feedback nested in About and Back navigation, with no JavaScript errors.
- Preparing the feature commit/PR to run native Android build and exact-source backend CI. Local79-test matrix results are recorded above; Android005 compilation/runtime remain pending until CI completes. Earlier001–004 artifacts remain preserved.

### Preview005 first native run and shared migration

- PR#9 source e7e591c passed backend CI43840887386 (both SQLAlchemy legs). Android43840887400 compiled/signed successfully but smoke stopped at a barcode-field assertion: native hint text took precedence over accessibilityLabel in the test helper. Updated matching to inspect both attributes with a bounded wait; added always-captured XML/screenshot/log diagnostics. Node24 now matches the web decoder dependency's declared engine. No005 release was published by the failed gate.
- Created no-compute recovery branch br-silent-leaf-bajr7isp before shared-preview additive0007 migration. Connected SQL requires one prepared statement per entry, so the initial whole-file transaction was rejected without changes; parsed the committed script with sqlparse and applied all six statements atomically. Imported22 bounded catalogue statements. Verified shared1,000identities/6groups/5,291localities/139branches/0prices/0barcodes. Added and verified only the API origin in the existing managed Auth trusted origins. API0.6 deployment remains pending merge.

### Native rerun — gallery fixture navigation

- Android43842287361 passed compilation/signing, scan navigation, native camera denial/manual fallback and camera preview. It stopped because AOSP DocumentsUI Recent had no fixture image; diagnostics capture confirmed the empty system picker. No application crash or release publication.
- Seed a JPEG fixture into Downloads (Android10 Exif handles JPEG), scan its canonical storage path, and browse Downloads when the system Recent view is empty. The test still requires actual ML Kit decoding of the synthetic EAN; no gate is skipped. Backend43842287282 passed both legs.
