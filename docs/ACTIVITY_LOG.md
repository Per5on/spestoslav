## 17 November 2026 — authorized email-excluded recheck and build

- Found two doubled-percent product names in isolated raw SQL transport. Fixed versioned renderer; regression tests round-trip all1000 identities twice and preserve existing aliases, brands, inactive flags and barcodes.100 PostgreSQL/OCR tests and both SQLAlchemy CI legs passed at557d900.
- Retained recovery; applied guarded additive shared sync, replayed identical hash.1000groceries+1000technology+5fuel,139stores/1inactive unchanged,0prices. Inventory PR15 not imported.
- Merged backend PR17 as9ba223de; Render deployment dep-dbua0l6k1f9s739t83d0 live, API0.6/ready verified. No automatic deploy was queued; public-Git-URL services require manual deployment per Render documentation.
- Public snapshots, all nine HTTPS sample images/credits, required national chains, canonical Sofia filtering and rejection boundaries verified. Sofia:46grocery branches,0technology/fuel branches. Feedback deliberately unavailable; no provider/email transmission.
- App5a1abb0 includes exact tested backend and actual decoded-image native assertions plus fivefuel choices. Backend CI44149787804 passed; Android44149787807 PASSED, actual decoded Food/Technology images, five fuel choices, camera and synthetic barcode decode. Artifact14360295033 downloaded, ZIP/APK checksums matched, screenshot inspected; APK75567529bytes/SHA25636cf2c5bb17d9021bc0bf7edd0989907f9017218fc6ea9b646b235a50e9312ba. Preserve previous successful/failed artifacts. Email intentionally excluded, no publication. Optional local Chromium live visual probe blocked by environment certificate trust; not counted as a pass, Android/Python HTTPS checks passed.

# Project activity log

Append dated entries. Keep the current resume point in `PROJECT_STATUS.md`; older entries are historical evidence, not current test/deployment claims.

## 16 November 2026 — Preview 006 code, connections and source checks; candidate build started

- **Code:** CI backend run 43869099648 passed at `7b861b0`. Android run 43869099618 failed at Android 10 smoke/emulator startup (`adb` exit 255); APK artifact uploaded, but no passing native smoke proof. Do not count this as a green release gate.
- **Connections:** Render `spestoslav-api` serves from `main`, not candidate branch. Recent request logs show HTTP 200 for product and fuel store endpoints, but response-body completeness and real-world performance remain unverified.
- **Sources (shared Neon preview branch):** read-only SQL returned 29 retailers, 139 store branches, 1,000 products, 5,291 localities, **0 product_images**. By category: fuel 7 retailers/2 active branches, groceries 14/134, technology 8/2. Missing images are confirmed backend data deficiency; petrol station coverage is minimal. No production data was modified.
- **Build initiation:** candidate metadata changed to `006` / `0.4.0` in `mobile/preview.json`, `mobile/package.json`, lockfile and preview registry. GitHub Actions Android run [43871290741](https://github.com/Per5on/spestoslav/actions/runs/43871290741) and backend run [43871290244](https://github.com/Per5on/spestoslav/actions/runs/43871290244) started at candidate SHA `452ef0c`. Automatic publication stays blocked on `codex/preview-006`.
- **Release blocked** until data gaps, Settings, feedback email and location performance are fixed and three complete green verification passes are documented on final code.

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

## 17 November — restored latest remote handoff; uploaded report assessment

- Owner requests analysis/comments and a concise action list before implementation of uploaded `You need to identify and.txt`. Treat document instructions as proposals to review, not authorization to delete data, branches or receipts, or start another release.
- Local checkout7862c18 and its modified PROJECT_STATUS are stale; preserved them. Fetched remote refs and read latest handoff/review/backlog directly from origin/codex/preview-006 at8526eb8 (draft PR#13). Preview005 is actually published: release android-preview-005; PR#9 remote head063f4b5 has green Android43859570901/publish and backend43859570734. Earlier failure43844195267 is historical, not current release status. PR#13 remains draft, publication skipped; green baseline CI does not prove pending data/Settings/Feedback acceptance.
- Report observations: technology market shares/rankings lack cited evidence; compile verified representative SKUs rather than claim national top1,000. Existing metadata cache contradicts basket/locality-only storage statement. Product.barcode is used by lookup/admin/write APIs, so removal requires staged migration. Confirmed current universal3ABI workflow, unminified config and1,008,792byte header/logo asset. Expo SDK54 official docs list both proposed minification/resource-shrinking flags. Keep expo-system-ui and active web-preview dependencies.
- Recommend functional/source/deployment checks first, then measured ABI/R8/logo optimization; defer locality/table/index deletion pending usage/size/plan evidence. Preserve receipt images/text for review and user receipt storage; design retention separately. Retain original provenance assets and recovery branches until recovery/retention review. No code/schema/deploy/build changes performed in this assessment. Next: present observations then ordered actions to owner; implement only within subsequent agreed scope.

## 17 November — dry tests complete; implementation approval pending

- Owner explicitly permits dry tests and findings only; actual implementation requires approval. Later “ok” accepted the aligned order, not a removal of this gate. No build/deploy/shared-write/commit/push performed.
- Immutable Preview006 snapshot8526eb8 tested outside checkout. Receipt actual-handler synthetic delayed I/O reproduced203–307ms event-loop gaps versus5.8–5.9ms for isolated worker comparison. Demo default remains true; metadata/price isolation tests pass.
- All116 CSV branch identities exist in139 shared records;23 DB-only records need provenance review. Shared0technologyproducts/0images/0barcodes/0prices; only2technology and2fuel branches. Existing indexes inspected; warm locality plans3.329–5.156ms do not justify speculative index changes. All5,291 live name/name_bg pairs differ.
- Render and HTTP confirm liveAPI0.5.0; snapshot endpoint404, firsthealth25s timeout. Candidate expects0.6 snapshot and falls back to serial pages. Backend74passed/5skipped with external DB env unset; TypeScript/npm checks pass.
- Preserved failed-attempt005 APK accounting suggests42.2% theoretical removal of non-ARM64 native library bytes, not a new build measurement. Separate256pxWebP trial17,236bytes vs original1,008,792; source untouched. SDK54 validates R8/shrink flags, runtime still untested.
- Findings, limits, evidence and proposed approval scope: docs/DRY_TEST_FINDINGS_2026-11-17.md. Exact next action: owner approval/adjustment before implementation; preserve all numbered releases, shared data, backups and receipts.

## 17November — implementation authorized;006 findings moved to to-do;007 prepared

- Owner instructed execution in stated order and preparation of007, superseding assessment-only approval hold. Confirmed +1pt applies to actual app text at every saved font setting. Dedicated codex/preview-007 worktree from0068526eb8 preserves original local edits and published005.
- Added006to-do/007plan and refreshed active handoff/status. Candidate007 metadata synchronized without building; automatic publication blocked for007 until three final verification passes and promotion.
- Required technology sources Zora, Technopolis, Technomarket, Techmart, Vali, Ardes, JAR Computers; fuel Lukoil, Petrol, Shell, EKO, OMV, Rompetrol. Source verification/catalogue implementation follows font change. Deferred destructive actions remain excluded.

## 17November — mock verification, image and policy additions in007

- Owner confirms actual font +1pt, illustrative photos need not match real products, fixed recipient ivo77@duck.com, no CAPTCHA, and developer IvayloYovchev with EU/GDPR framework. Generated BG/EN Terms+Privacy draft from one in-app JSON source; Settings entries and form privacy link added. Other UI languages show an explicit BG/EN-document fallback. Do not invent postal/member-state/provider/retention details or claim completed compliance.
- Sample image catalogue: preserved3grocery photos plus6licensed Commons technology examples, credits/licences and content hashes. Visual review rejected unrelated event/adapter examples and selected clearer illustrations. No exact SKU-photo association or price is asserted.
- Source-backed technology freeze:1,000distinct retailer codes and display names from Techmart, with five groups and per-product source links; no prices/GTINs. Required7technology/6fuelchains written to retailer priorities and Markdown; real national branch coverage remains a separate task. No synthetic branch or price entered shared Neon.
- Local mock scenario covers source-backed catalogues, actual locality reference list, requested chains and synthetic stations/fuel prices, camera/image/manual barcode, private receipt Bulgarian OCR/review/deletion, comparison, cached metadata, font/language controls and Feedback mock success/failure/unavailable. Existing workflow and new functional/menu suites passed without JS errors. Narrow320px/130% six-language toolbar suite passed after equal-height/wrap handling. Black browser outline removed from Refresh; thin green border retained.
- Local PostgreSQL16/SQLAlchemy2.1 suite86passed with real Bulgarian OCR and additive0008technology migration. Final same-source repeated verification/screenshot refresh follows latest policy/photo updates.
- **Explicit new build hold:** user must confirm007 build after reviewing all dry tests/screenshots. Workflow only builds on explicit dispatch/confirm_build; publication separately gated and007excluded. Do not start native build or publish automatically. GooglePlay test build follows007 and requires real source/email/location/device, signing/privacy/account-deletion readiness.

## 17 November — completion-status verification

- Checked active branch/worktree and stored test evidence. Implementation remains uncommitted on codex/preview-007 at8526eb8; overall process is not complete. Legal browser test passed Terms/Privacy, bilingual illustration disclosure and unsent feedback draft preservation, with no JavaScript errors. Stored PostgreSQL suite86passed; narrow six-language toolbar suite passed. These are local evidence, not final-source CI/native/live acceptance.
- Pending: refreshed screenshots after latest assets/policy changes; optimization/native trials; three complete final-source passes; live backend/source/branch reconciliation, real price coverage and configured SMTP delivery; final operator/privacy/account-deletion readiness for GooglePlay. No007 build authorized or started in this status check. Next action: refresh clean functional screenshots, then complete remaining dry-test/optimization gates without building until explicit owner confirmation.

## 17 November — inventory statement checked and pending work consolidated

- Read PR #15, Issue #14 and reconciliation document at exact c791beb4. PR remains open/draft; direct commit-status and Actions queries both returned empty arrays. GitHub reports mergeable=false; base compatibility needs investigation before merge. The documented143-row seed/9CBA/35locality triples and139-total/138-active baseline are not a fresh Neon recount in this check.
- Added consolidated outstanding work to PROJECT_STATUS.md: official closures/relocations/source identity reconciliation, inactive-history safeguards, explicit import diff/current-schema compatibility, exact-head CI, transactional idempotent preview import and second-run verification; plus screenshots, final-source/native checks, live price/location/email and privacy/GooglePlay gates. Inventory remains separate from Preview006/007 UI. No import, merge, GitHub message, build or publication performed. Next inventory action: inspect importer and row-level reconciliation before any preview write; continue independent functional dry tests within existing authorization.

## 17 November — requested inventory reconciliation and CI complete

- PR #15 inventory branch now at15ea1f61e4b4f8ab86d0cb89d6a5b6b3063fdb7b; merged main39304dc and resolved seed conflict without restoring postal/Home fields. GitHub reports MERGEABLE/CLEAN; remains draft pending separate import/review gate.
- Fresh read-only preview snapshot139total/138active/139linked:138active seed matches unchanged,5reviewed insert candidates (two T MARKET, three CBA),1inactive Mini Mart retained. Confirmed T MARKET closures absent from existing records; Teteven former address unspecified and not invented. Mini Mart HristoBotev75 remains pending/inactive, not confirmed closed. Current official feed has357raw records; IDs75/118 duplicate one retained physical branch. All9CBA/Bolero directory entries checked.
- Importer rejects normalized duplicates, closed/pending input, inactive reactivation and identity collisions. Explicit current/legacy-preview modes; no schema restoration. Full139+5local replay on both schemas:144total/143active, every original record preserved, second run unchanged; atomic failure rollback verified. Local full backend80passed. Exact-head CI https://github.com/Per5on/spestoslav/actions/runs/44096315610 succeeded on SQLAlchemy2.0 and2.1. Mobile/APK workflow unchanged from main; no APK job ran.
- No shared Neon writes, PR merge, deploy, APK build or publication. Next inventory step is separately scoped preview import after live-baseline drift check and recovery plan, using only data/batches/2026-11-17-reconciled-additions.csv with explicit legacy-preview target. Preview006/007 UI remains separate and007still requires explicit build confirmation. Detailed committed evidence: docs/INVENTORY_RECONCILIATION_2026-11-17.md on PR #15. Inventory worktree is clean; app worktree changes preserved.

## 17 November — owner authorizes Preview007 build with live functionality

- Owner explicitly authorizes commit/build; do not ask for the same approval again. All real connections, images, filters/options required; no claim that mock success establishes live acceptance. Yahoo SMTP chosen; sender provided, app-password secret still needs private deployment configuration. No credentials added to code.
- Fresh final-source checks:86backend tests passed with PostgreSQL/Bulgarian OCR, TypeScript/npm/legal sync checks passed; functional browser mock suite passed without JS errors. API initial25s read timeouts thenhealth200/OpenAPI0.5.0; catalogue groceries/technology snapshot and feedback availability404. Render reports live538bd9a, not candidate. Log service returned503; do not infer application exceptions from unavailable log retrieval.
- Next: commit candidate, exact-head CI, then live backend/catalogue/SMTP reconciliation and native readiness; never package simulations as verified live functionality. Existing numbered releases preserved; no APK publication.

## 17 November — native failure diagnosed; bounded recovery and rollout trials

Owner authorization to commit/build remains active; do not request it again. PR16 candidate3867e5e compiled/signed successfully in Android run44098576002, but native smoke failed finding Sofia after75seconds. Captured screen shows both location/catalogue network errors; APK has INTERNET permission and real HTTPS API URL. This failed candidate is preserved, not a release. Do not label it fully live.

Follow-up changes: bounded safe-GET retries covering response body timeouts and cancellation, no automatic POST/upload replay; privacy-safe location error class logs; public-endpoint CI diagnostics. Unit/browser regression proves transient recovery without manual retry and bounded permanent failure/manual retry; functional mock suite still passes. New source needs exact-head CI/native rerun. Owner-approved007PR builds may run automatically on this same repository branch; publication remains blocked.

Yahoo SMTP is blocked on the current Render Free service (official https://render.com/docs/free.md), regardless of password. Non-password settings saved, delivery explicitly disabled; owner decision pending on free HTTPS provider versus reviewed paid SMTP hosting. No upgrade or real email sent. Preserve private credentials; no password is needed in chat.

Isolated Neon branch br-polished-unit-bafzpcnc validates additive0008 and1000technology identities; repeat compiled model upserts leave counts/product hashes identical. Grocery/store hashes match shared preview;139branches/1inactive preserved. Source-backed metadata only, no GTIN/price invention. Shared preview remains unchanged at1000groceries/0technology/0prices. New group index benchmark for4-record group:3buffer hits versus47sequential; tiny timing results noisy, not a general latency claim. Direct shell PostgreSQL unavailable; connector SQL transaction fallback used. Recovery/history retained; no inventory PR15 import, purge or deletion.

Next: commit corrective source; inspect exact-head backend and Android results; fix any native failure without weakening assertions. API rollout remains pending (currently0.5.0, candidate snapshots/feedback404), along with real auth/storage/email/price verification and three final passes. Local evidence outside repo: preview007-native-attempt-01, preview007-network-regression-02, preview007-neon-validation-evidence.json. Preview007 is not yet fully live/ready; no publication.

## 17 November — complete handoff task/result register

Owner requested all tasks/results in handoff. Replaced CODEX_HANDOFF.md with a complete current register covering design decisions, inventory PR15, successful007APK/CI/SHA, failure/fix evidence,1000grocery/technology metadata, required chain/fuel setup, camera/barcode/receipts/comparison, cache/gallery/settings/privacy, freeHTTPS feedback decision, optimization/release/GooglePlay gates and exact next actions. Copied the checkpoint into all active/preserved app checkouts. Latest backend metadata code has98local PostgreSQL/OCR tests passed; it and this checkpoint require commit/exact-head CI. Shared preview remainsunchanged, API still0.5, no APK publication. Brevo account/key setup remainsowner action; no credentials recorded.

## 17 November — verified handoff results finalized

Complete CODEX_HANDOFF.md register updated with exact backend codef28fe642 CI44115959801 success (98local PostgreSQL/OCR tests), app48c7442 Android44105274182 success, artifact/SHA/size, first native failure and correction, all task statuses and explicit outstanding gates. Directory/fuel metadata trial ran twice on isolated br-polished-unit-bafzpcnc:1000technology,5fuel types,1active Techmart identity,139stores/1inactive,0prices. Shared preview remainsunchanged; no API rollout or publication. Owner selected freeBrevoHTTPS but has not yet configured account/sender/key; unavailable state remains intentional. Updated canonical handoff and copies in app/older checkout; keep projectACTIVE and resume shared-sync/backend-rollout checks without inventing live coverage.

## 17 November — backend-only Preview007 rollout prepared

Backend-only branch `codex/preview-007-live-api` prepares tested API0.6 from application source48c7442. Local PostgreSQL/OCR suite87passed; all active API model columns match the isolated Neon clone after0008. One unused legacy user_submissions.locality_id column differs; no route uses it and no speculative change is applied. No mobile/native source or numbered APK/release changed here. App PR16 native run44105274182 passed Android10 after bounded safe-read retry correction; previous failed run44098576002 remains preserved.

Read `PREVIEW_007_API_ROLLOUT.md`. Prepare backup and additive schema/catalogue sync before API deploy; preserve139stores/1inactive and grocery hashes; do not import inventory PR15's five addresses as part of this lane. SMTP delivery remains explicitly disabled because Render Free blocks Yahoo SMTP465/587; owner provider choice pending, no paid upgrade. Sample endpoint is opt-in client-side, labelled unverified, never priced/compared. Published005 and earlier APKs remain immutable. Existing app development continues in `/workspace/work/spestoslav-preview007`; this branch isolates service readiness from APK distribution.

## 17 November — free HTTPS feedback adapter

Owner selected free HTTPS instead of paid SMTP hosting, and confirmed account/key are not yet configured. Implemented Brevo HTTPS adapter with fixed recipient, server-only key, verified sender configuration, generic errors and explicit disabled state. Tests cover provider acceptance, rejection/rate-limit/unavailability/malformed201, missing credentials and no secret/recipient injection. Render FEEDBACK_PROVIDER saved asbrevo, delivery staysfalse. No email sent, no paid upgrade, no credentials logged. Official API/pricing docs retrieved successfully. Native APK48c7442/run44105274182 is signed, checksum verified and Android10passed; client contract unchanged by provider adapter.

## 17 November — fresh error-miss audit; email excluded from build

Owner authorizes rerun and APK build without email service. Feedback staysdisabled; no provider credentials needed/requested. Fresh98-test PostgreSQL/OCR baseline and TypeScript/mobile/legal checks passed. Exact clone-content audit caught two doubled-percent product names in scratch raw-SQL rendering; corrected via versioned renderer, with regression tests forpercent/apostrophe/backslash round trips and complete1000-row content/idempotence. Preserve unknown-brand/alias fields rather than erasing verified values. Shared preview untouched. Continue full checks, controlled non-email backend readiness and newAPK; record final CI/artifact evidence before delivery.

## 18 November — external review patch (no build, no CI yet)

Reviewed branch `codex/preview-007` (app `5a1abb0`; backend unchanged from main). Offline evidence only: relative imports resolve, no new TypeScript diagnostics versus the unpatched branch (React/React Native types were not installed, so this is not a full typecheck), `test-network`, `test-cache`, `test-errors` and `test-preview-metadata` pass, and all six languages share the same 187 message keys. Backend tests were **not run** (no FastAPI/SQLAlchemy in the review sandbox).

Changes: session restore warm-up and one transient retry; typed `ApiError`/`httpStatus`; specific auth, sign-out and delete-account messages; receipt upload separates "upload failed" from "refresh failed"; camera-denied and no-barcode notices; `submitted` flag resets per receipt; retried 5xx bodies cancelled; `signIn` no longer orphans a server session when SecureStore fails; new `DELETE /api/v1/account` (receipts and stored images erased, pending contributions deleted, reviewed ones unlinked, then provider `/delete-user`) with seven tests.

Correction to earlier entries: the Yahoo SMTP path recorded on 17 November was abandoned; Brevo HTTPS is the chosen provider and delivery stays disabled. Entries above are preserved as history.

Next action: owner reviews the patch, applies it on a new branch (suggested `codex/preview-008`), reads exact-head backend CI (PostgreSQL) and the Android run, and verifies `/delete-user` against a throwaway real account before any claim of working account deletion. Legal text still needs the deletion procedure and the "approved prices stay anonymous" decision before public testing.


## 18 November — Preview008 backend-first recheck

- Rechecked [draft PR #19](https://github.com/Per5on/spestoslav/pull/19), backend CI [44287192549](https://github.com/Per5on/spestoslav/actions/runs/44287192549) and skipped Android runs [44287192548](https://github.com/Per5on/spestoslav/actions/runs/44287192548) and [44292063248](https://github.com/Per5on/spestoslav/actions/runs/44292063248). Changes remain uncommitted on top of `daa73ae`. The candidate workflow no longer contains a publish job.
- Fixed two-character locality ranking and literal wildcard matching, corrected PostgreSQL receipt foreign-key order, tested provider deletion confirmation and duplicate registration status, then updated location input, app button styling, Settings, credits, auth retry and receipt feedback paths. Kept the existing thin green Refresh border and added green keyboard focus for browser pressables.
- Disposable PostgreSQL 16 and Bulgarian OCR: 112 tests passed per SQLAlchemy family. Direct PostgreSQL account/locality checks: 16 passed per family with mocked identity provider. TypeScript, npm tests, Expo dependencies and simulated browser checks passed. Read-only public baseline probes returned HTTP 200 and the Neon Auth schema listed the deletion endpoint.
- Android prebuild in a scratch directory confirmed versionCode 8, versionName 0.5.1, minSdk 29 and the camera permission. Android 10 device and end-to-end real account/private storage evidence are pending. No new commit, push, deployment, APK or release. Resume from the active local checkout and keep the release gate and feedback setting recorded in the handoff.

## 18 November — pre-build optimization audit

Checked local render and offline image paths, read-only live catalogue image counts, decoded all nine live samples, and verified the existing Preview007 package by checksum before measuring ABI entries. The handoff records the findings and proposed Android dry tests. No new build or code commit.

## 18 November — optimization implementation and dry checks

Applied menu and catalogue rendering changes, bundled sample thumbnails, added a bounded native image cache, and generated ABI and shrink configurations. Browser timings, offline decoding and Android bundle export are recorded in the handoff. The requested Android emulator run and signed package comparison require a capable test environment. No commit or release.

## 18 November — Preview008 candidate commit checks

Reconciled the two uploaded commits, verified rendered catalogue, Settings and About screens, and prepared an ARM phone APK lane with a separate x86_64 emulator smoke lane. Browser and backend checks passed. Continue by checking native CI on the candidate SHA and recording its signed artifact evidence.

## 18 November — stopped build and corrected Refresh and About

Confirmed [run 44306415234](https://github.com/Per5on/spestoslav/actions/runs/44306415234) was cancelled with no Preview008 APK. Removed the Refresh border and focus outline and moved image credits to sample cards. Browser screenshots and functional tests verified both corrections. Wait for the owner to restart Android CI with corrected source.

## 18 November — corrected Preview008 native smoke and ARM packaging retry

Android 10 smoke passed on run 44307049747. The following ARM pack step hit React Native JNI codegen during Gradle clean. Changed the workflow to regenerate the Android project before assembling the phone APK. Exact-commit browser measurements and offline samples passed and are recorded in the handoff.

## 18 November — verified Preview008 APK and reviewed AAB readiness

Run 44309388382 passed. Verified artifact 14429854071, inspected native screenshots and compared APK bytes against Preview007. Rechecked the app, build and regression suite and recorded release/cleanup findings in the handoff. Next is a separate signed AAB lane and its Play internal testing gates.

## 18 November — locality search ordering

Updated the local API to sort starts-with matches first and keep both groups alphabetical. Passed the full 113-test backend suite and nine direct PostgreSQL locality tests. The app has no web deletion URL. Next action is to include the search change in the authorized backend rollout.

## 18 November — Pre-alpha 009 images and feedback checks

Verified all nine sample assets in the signed 008 APK. On local Pre-alpha 009, enabled first-launch visibility and verified offline decoding and persistent opt-out. Sent synthetic feedback end to end through the API and authenticated STARTTLS into a loopback mailbox. Live catalogue has zero real image links, and external delivery remains unavailable. Next action is to verify the gallery on the next authorized APK and exercise live delivery after configuring the sender.

## 18 November — appearance, symbolic thumbnails and feedback routing

Checked profile secret storage. Verified 14 symbolic assets and the API on local PostgreSQL before implementing the UI, then verified the separate Neon database. Tested the eight palettes and persistent Images and Dark mode switches. Brevo regression confirmed fixed delivery to ivo77@duck.com and different Reply-To addresses. Next wire the thumbnail DSN and verified Brevo sender/key in Render for live testing.

## 18 November — Pre-alpha data deletion and daily consolidation

Added a guest-capable local data reset and an authenticated cloud erasure route that retains the sign-in account. Backend, browser and Android prebuild lanes passed. Consolidated today’s actions in the handoff. Await the next APK build instruction and verify the live route with a disposable account before promising cloud erasure to users.

## 21 November 2026 — Codex pre-alpha 010 preparation

- Reconciled Codex pre-alpha 009 handoff with [exact-head Android evidence](https://github.com/Per5on/spestoslav/actions/runs/44348096077). Started the 010 candidate directly from the 009 commit.
- Both PostgreSQL/SQLAlchemy legs returned 115 passed and one Bulgarian OCR skip each. Installed the Bulgarian language data and reran the OCR selection separately, yielding four passes. Inventory validation, package metadata, mobile tests, TypeScript and Expo dependency checks passed.
- Next verify Android 10 smoke, ARM APK and test-signed bundle on the final 010 candidate. Preserve 009 artifacts.
- Owner paused Android builds. GitHub confirmed [010 run 44917016393](https://github.com/Per5on/spestoslav/actions/runs/44917016393) cancelled. The prepared source and source-check evidence are retained.

## 21 November 2026 — 010 candidate verification and build hold

- Added the nationwide merchant directory and implemented the requested catalogue, fuel, comparison, images and palette changes to candidate source. Removed stale toolbar code and restricted chain requests to their remaining fuel-overview caller. Resolved dependency tree and Expo plugin audit found no safe runtime removal.
- Backend matrix passed 117 tests per leg on local PostgreSQL 16 with Bulgarian OCR. Mobile checks and six Chromium dry-run suites passed. Verified Android config and smoke script syntax independently of packaging. [Dry-run captures](references/pre-alpha-010-dry-run.jpg).
- Next action is owner acknowledgment of the exact candidate commit. Keep Android dispatch and backend rollout on hold.

- Follow-up for 010: renamed Theme, removed both image switches, bundled grocery fallbacks and moved Dark mode above palettes after the prior native smoke failure. Repeated the backend matrix, mobile checks, six browser suites and Android configuration preflight. Await revised commit acknowledgment before dispatch.

- Run 44922323093 verified the emulator APK but stopped before installation at ADB unlock (exit 255). Replaced the runner startup step with explicit AVD discovery and bounded readiness and unlock retries. Syntax and local simulated retry/crash checks passed. Wait for approval of the new exact SHA before starting Android CI.

- Confirmed [Android run 44923545071](https://github.com/Per5on/spestoslav/actions/runs/44923545071) passed on approved source `2d19a0c`. Recorded the artifacts and live-test pending status. Queued product-matched WebPs and itemized comparison with a proposed merchant-card layout.

- Prepared preview 10.5 with itemized comparison, pop-up group menus, palette removals and 7 product-linked representative photo references. Backend 117 tests per leg, six browser suites and source/preflight checks passed. Await exact-commit build approval. Live deploy and device acceptance are pending.

- Final 10.5 change: unified Food and Technology thumbnail framing and disambiguated duplicate catalogue names. Repeated full PostgreSQL, browser and mobile/preflight checks. Await exact-SHA build approval.

- 10.5 regression check: reproduced live merchant-directory HTTP 404. Verified the dated 116-address fallback and recovery to fixture live data. Added tap-to-enlarge and representative group photos. Repeated backend, mobile, browser and Android configuration checks. Await exact-SHA approval.

- Preview 10.5 run 44930361440 attempt 3 failed provisioning the Android 10 Play Store image ZIP. Added bounded SDK installation and emulator startup retries, locally checked success and persistent failure paths. Await approval of the revised workflow SHA.

## 22 November 2026 — ARM-only Android candidate

- Removed the x86_64 APK and hosted emulator steps. The workflow builds ARM64 and ARMv7 and checks both ABIs, APK signatures and test-signed AAB structure. Installed smoke testing now needs an ARM Android device. The previously verified artefacts remain historical evidence.
- Reordered Settings, compacted header and tabs, relocated the locality field, and made fuel controls static. Verified transparent product artwork and tomato mapping. Both backend legs and all six browser suites passed. Captured the browser preview and left Android dispatch at the exact-SHA approval gate.
