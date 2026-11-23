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

- Restored the original stacked category icons and names with smaller 16 pt symbols and compact padding. Verified standard and narrow browser layouts and retained the build hold.

- Owner requested 4 pt vertical tab padding and a visual preview. Mobile and responsive browser checks passed. Android run 45035896667 was dispatched after misreading the request and cancellation was requested when the owner clarified.

## 22 November 2026 — technology stores and category icons

- Set all four category icons to 20 pt, retaining 10 pt vertical padding. The owner requested no visual preview.
- Verified 174 physical locations from seven official technology retailers and updated the inventory seed and saved directory. All 14 requested Techmart stores were included. The date, counts and source links are in the handoff.
- Passed mobile unit tests, TypeScript, canonical inventory validation, the six-language layout check and browser verification of the saved directory after a simulated API 404.
- Next action is to obtain approval for the revised ARM candidate. Live directory rollout and data import remain pending.

## 22 November 2026 — Fuelo stations in the saved merchant directory

- Matched 724 of 794 Fuelo listings across the six requested brands to canonical localities. Added 722 rows and retained the two existing EKO records with official provenance. Recorded the 70 unresolved locality assignments in the handoff.
- Passed inventory validation, mobile tests, TypeScript and the browser fixture check for all six chains after a simulated directory 404. The directory then recovered to fixture API data.
- Next action is to obtain approval for the revised ARM candidate. Live API rollout and data import remain pending.

## 22 November 2026 — alpha-preview10.6 verification and approval

- Owner authorized the 10.6 internal build after rechecking the day's changes and requested a visual preview. The app is version 0.5.5, Android version code 12, package sequence 012. Captured the six-screen [browser preview](references/alpha-preview10.6.jpg).
- Passed mobile tests, TypeScript, Expo dependency checks, and six browser suites. Verified the 20 pt icons with 10 pt padding, Settings columns, palette choices, static fuel rows, comparison, directory fallback, barcode scanning and receipt upload, OCR, moderation and deletion on fixtures.
- The inventory seed matches all 1,563 saved directory entries. The local backend suite passed 110 tests and skipped seven that require disposable PostgreSQL. Live API acceptance and installed ARM-device testing remain pending.
- Dispatched the approved [ARM APK and test-signed AAB build](https://github.com/Per5on/spestoslav/actions/runs/45039195640) from `11b6a3b33f003089439912911d437e05b29f90a6`. GitHub reported it in progress. Check this exact run for packaging results and artifacts before physical-device testing.

## 22 November 2026 — fuel toolbar visual revision

- Anchored Обнови at the far right and measured the translated fuel labels before assigning choices to the first row. At 390 px with default Bulgarian text, Дизел fits before Обнови. At 320 px with enlarged Bulgarian text, the remaining choices flow to additional rows. [Browser preview](references/alpha-preview10.6-fuel-toolbar.png).
- Mobile unit tests, TypeScript, and six-language browser toolbar checks passed. The owner approved the left visual as the reference for this commit. The earlier [10.6 ARM run](https://github.com/Per5on/spestoslav/actions/runs/45039195640) succeeded at its original source commit and predates this change.

## 22 November 2026 — Спестовник logo preview

- Applied the approved emerald market-scale design with gold coins and an ivory diamond in the coral шевица to the in-app header and Android launcher assets. Expo prebuild generated the legacy and adaptive launcher resources. Mobile unit tests, TypeScript, and browser toolbar checks passed.
- The [visual preview](references/scale-logo-app-preview.png) pairs a rendering of the generated adaptive icon with a browser screenshot of the header. Next action is to review this preview before Android packaging.

## 22 November 2026 — 8 pt follow-up candidate

- The owner confirmed the existing 10.6 APK installs. Prepared the follow-up with 8 pt category padding, the approved responsive fuel toolbar, and the launcher and header logo.
- Passed mobile tests, TypeScript, Expo dependency and Android resource generation checks, six-language browser toolbar checks, browser catalogue and directory checks, and validation of the 1,563 saved locations. [Candidate preview](references/candidate-8pt-fuel-and-logo.png).
- Next action is owner approval of the candidate commit. The follow-up has not been packaged or installed.
- Narrowed the location field by 16 px in the 390 px browser viewport and highlighted it with a pale green fill and stronger border. Mobile tests, TypeScript, six-language layout checks, and location search and retry checks passed. [Updated candidate preview](references/candidate-location-preview.png). Await owner approval before committing or packaging.

## 22 November 2026 — Preview 010.7 approved

- Prepared build sequence 013 from the owner-confirmed installable 10.6 baseline and the approved fuel toolbar, 8 pt tab padding, highlighted location field, and launcher and header logo. Removed the two unreferenced former runtime logo files.
- Mobile tests, TypeScript, Expo dependency checks, the browser toolbar, location and catalogue suites, and validation of all 1,563 directory entries passed. The owner approved internal Android packaging.
- [Android run 45062475962](https://github.com/Per5on/spestoslav/actions/runs/45062475962) passed on `ebc6ec09d829b30f41ee3f25319f2c00948d145b`. GitHub verified APK signing and both ARM ABIs, validated the test-signed bundle, and uploaded [APK artifact 14770591595](https://github.com/Per5on/spestoslav/actions/runs/45062475962/artifacts/14770591595) and [AAB artifact 14770187615](https://github.com/Per5on/spestoslav/actions/runs/45062475962/artifacts/14770187615). This workspace was denied artifact downloads, so independent checksum verification remains pending.
- Final checks also passed for menu, legal copy, fixture barcode scanning, itemized comparison, receipt upload, Bulgarian OCR and deletion. Backend tests reported 110 passed and seven PostgreSQL-only skips. Next action is to install the APK on an ARM Android 10+ device and check the launcher, header, location field and fuel layout.

## 23 November 2026 — backend cleanup

- Applied the approved import and shared-helper cleanup to the Preview 010.7 source. Added the Ruff 0.17.6 backend CI check, updated archive references, and retained the four historical documentation entry points.
- Local Ruff and inventory validation passed. Backend tests passed 110, with seven disposable PostgreSQL tests skipped. The earlier two-patch trial was isolated. Feedback configuration, expiry handling and receipt sweeping are outside this change.
- The cleanup is ready for commit. Exact-commit backend CI and physical-device acceptance of Preview 010.7 remain pending.

- Reviewed the two follow-up hunks against the cleanup. A focused isolated SQLite test passed with read-only expiry handling. Static review confirmed that the proposed receipt sweep deletes by default. Recorded both adapted changes as next backend commit tasks, with disposable-storage verification pending for the sweep. No sweep ran and no commit was made.

## 23 November 2026 — next beta scope

- Added the owner's header, thumbnails, message, food groups, fuel controls, location scope, grocery directory, price sourcing and beta feature checks to the existing commit checklist. The Моят магазин registry entry is a placeholder and the seed has no branches for it.
- Next steps are to prepare visual previews, review the compact footer mockup, and evaluate merchant price and thumbnail sources. APK packaging requires explicit approval after code review, backend verification and successful dry tests.
- The owner supplied a screenshot for the bottom notices. Prepared a browser mockup for the compact footer and revised header. The mocked footer shows all three notices together for review. App code and packaging are pending visual approval.
- The owner clarified that the previous money-bag logo is for the Android launcher only and the header should show no logo.
- Applied the approved logo-free header with a larger „Сравни и спести“ slogan and reduced vertical padding. Restored the exact 10.6 money-bag asset for the Android launcher. Mobile tests, TypeScript, the resolved Expo icon configuration and a 320 px browser check passed. [Implemented header](references/next-beta-header-implemented.png). The footer and remaining beta tasks are pending. APK packaging requires explicit approval.
- Prepared the next beta catalogue and fuel mockups for one visual review, including smaller cards, matched illustrative WebPs, revised food groups and a one-row fuel selector. Confirmed the Kaufland branch feed, Technopolis product price and pickup signals, and 288 raw Моят магазин locator records. Recorded remaining branch-price, reuse rights and Fuelo access checks in the beta checklist. App changes for these mockups and APK packaging await approval.
- The owner approved the visual set and requested two food groups in the first row, three in the second and the rest in the overflow menu. Implemented that order and the 2 pt card and thumbnail reduction. Six generated illustrative WebPs are bundled for the matching sample products. Browser verification confirmed the six new files loaded and all food buttons fit at 320 and 390 px. Mobile tests and TypeScript passed. Live catalogue thumbnail coverage, footer and fuel implementation remain pending. APK packaging still requires explicit approval.
- Moved the catalogue photo, store-load and saved-catalogue notices out of the scrolling area into a bottom footer. The browser verified the footer stays at the viewport bottom while scrolling, shows applicable notices with 1.5 pt spacing, and is absent on the comparison tab. Mobile tests, TypeScript and catalogue regression checks passed. [Implemented footer](references/next-beta-footer-implemented.png). Fuel controls and live source checks remain pending.
- The owner confirmed that the simulation notice should be absent from the live beta. Added live operation checks as a pre-APK gate and retained the simulation notice for fixture previews. Initial public API probes timed out, so live data and authenticated workflows remain unverified.
- Retried the public API using curl. Readiness and Sofia search returned 200. Grocery and technology catalogues each returned 1,000 products with zero image URLs. Sofia returned 46 grocery branches, zero technology branches, zero fuel stations and zero current prices. The merchant directory returned 404. Feedback availability returned false. These read-only checks leave live beta acceptance pending. Next work is the directory rollout, branch and price data coverage, and end-to-end verification of login, receipts and feedback.
- The owner clarified that a published online price is acceptable as an indication when the merchant has a physical branch in the selected locality. Added locality filtering and branch-quote preference to the isolated backend hotfix. It also restores the paginated merchant directory and returns item prices alongside merchant totals. Both SQLAlchemy CI jobs passed on the PR and on the main merge `9c719592752c09c7740dedf353ee714b26d38ae9`. The APK workflow did not run. [Backend PR 22](https://github.com/Per5on/spestoslav/pull/22) · [Main backend CI](https://github.com/Per5on/spestoslav/actions/runs/45148074857)
- Validated and replayed the Sofia inventory import on an isolated Neon branch before applying the additive change to the shared preview. The public API independently confirmed 34 technology branches across seven retailers and 113 petrol stations across six chains. The shared grocery count stayed at 46. Six grocery products and one technology product now have licensed representative WebP links confirmed through both public catalogue endpoints. [Thumbnail credits](../mobile/assets/produce/SOURCES.md)
- The Burlex public store table has BGN values plus a displayed conversion at 1.95583. Matched official records by exact catalogue code and branch address and published 460 regular prices for Банишора and 415 for Лозенец. The public Sofia price endpoint returned all 875 rows. The imports use a 12-hour freshness window and immutable observations. Replay on the disposable database produced no new rows. [Burlex table](https://burlex.bg/kolkostruva/)
- Checked five exact Techmart SKUs against EUR product-page structured data. Initial live API testing exposed a pre-existing unscoped comparison that returned a Techmart quote in Мадан despite zero technology branches there. Expired only the five pilot offers pending the verified rollout. Tested the published KARAI Fuel Index feed on the cloned database with 17 indicative chain prices for six chains and three supported fuel types. [KARAI methodology and licence](https://karai.bg/fuel-prices/indeks#metodologiya)
- The owner requested retention of project communication in the repository. Added the reconstructed conversation to `docs/PROJECT_COMMUNICATION.md` and linked it from the handoff. Prior assistant messages absent from the available history cannot be transcribed. [Project communication](PROJECT_COMMUNICATION.md)
- Render deployed the exact backend merge at 11:36 Sofia time after automatic deployment did not queue. The paginated merchant directory returned 285 active entries and included all 193 Sofia addresses. The live scoped feeds returned five Techmart prices and 17 KARAI prices across six chains. Sofia returned a two-item Techmart basket at €303.99 (€114.99 and €189.00) with indicative online scope. Мадан returned zero Techmart prices and quotes. A two-item grocery basket yielded separate complete local results at both Burlex addresses. The verified fuel coverage is А95, дизел and LPG. [Live readiness](https://spestoslav-api.onrender.com/ready) · [Backend deployment](https://dashboard.render.com/web/srv-dbs313ei0phs73bvvd00/deploys/dep-dc20hud9fdbs73c2rufg)
- The 390 px web preview used the deployed API with simulation disabled and showed the indicative Techmart item prices and total, the attributed fuel price and the merchant directory. The five single-row fuel choices passed geometry checks at 320 px with a 1.3 font scale in all six supported languages. Mobile tests, TypeScript, Ruff and diff checks passed. [Comparison](references/beta-live-sofia-comparison.png) · [Fuel](references/beta-live-sofia-fuel.png)
- Next actions are to wire recurring source refresh, extend coverage to more merchants and representative thumbnails, and complete authenticated and peripheral workflow checks before requesting beta APK approval. The reviewed collectors are published separately from Android release work.

## 23 November 2026 — grouped fuel results

- Implemented one row per chain using the existing online and station price indexes. The count includes local stations using the shared estimate and those with the same displayed station price. Different confirmed station prices show as address and price within the chain entry. The price expiry timer now also covers indicative offers.
- Live Sofia browser verification found six A95 chain entries for 113 stations, including EKO at €1.51/L for 27 branches. An injected browser-only EKO price of €1.49/L displayed separately with its address and reduced the count to 26. Switching to diesel removed that exception. [Grouped fuel preview](references/beta-live-sofia-fuel-grouped.png)
- Mobile tests, TypeScript, Ruff and diff checks passed. Backend pytest reported 110 passes and seven skips in the local environment. Live readiness, the paginated merchant directory and public auth configuration responded successfully. The unauthenticated receipts request was denied and live feedback returned unavailable. Authenticated live sign-in and receipt acceptance, live feedback delivery and recurring price refresh remain open. APK packaging still requires explicit approval.
- Continued the workflow checks using fresh temporary receipt storage and Bulgarian Tesseract data. The backend suite passed 111 tests, including real Bulgarian OCR, with six checks skipped because they require disposable PostgreSQL. The isolated feedback fixture passed provider acceptance, provider failure and disabled-service checks. Live feedback remains unavailable.
- The full local browser workflow passed with fresh receipt storage. It verified camera and image barcode decoding, sign-in with fixture credentials, receipt upload and Bulgarian OCR, review and deletion, and manual barcode entry after camera denial. The scanner now reports the permission-specific message when the browser rejects a camera stream. Mobile tests and TypeScript passed after the correction.
- Next verify authenticated sign-in and receipt upload against the live service with an authorized test account. Recheck live feedback once delivery is enabled. Recurring price refresh and explicit APK approval are still pending.

## 23 November 2026 — refresh cadence and account recovery audit

- The owner specified two grocery source checks per week, one fuel check per day and a forgotten-password option for signing in on a new device. The owner will report the physical-device result.
- The current Burlex collector uses a 12-hour expiry and KARAI uses 24 hours. The API omits expired prices from live queries. Verified the existing workflow schedules and recorded the need to exercise expiry and a missed refresh at the new cadence.
- The signed-out screen and deployed app API have no password-reset flow. A read-only check of the configured Neon Auth OpenAPI schema confirmed password reset endpoints, including email OTP. Live delivery and the recovery experience are unverified. The basket and preferences use device-local storage.
- Next implement the source jobs and expiry presentation, then add the sign-in recovery control and verify it with an authorized test inbox and a fresh session. Keep authenticated live receipt acceptance and collection coverage in the beta checklist. [Beta checklist](PREVIEW_006_BACKLOG.md#backend-and-beta-acceptance)

## 23 November 2026 — daily price checks and password recovery

- Recorded the updated cadence of one check per day in all three categories. Added a read-only workflow at 11:17 UTC in standalone main commit `73a0be1`. Local runs found 500 raw price rows per Burlex branch, five Techmart offers and 17 KARAI chain prices. The first hosted run passed all three category jobs and generated three reports. A simulated primary failure retained the secondary archive result. Current application price publication remains separate. [Hosted checks](https://github.com/Per5on/spestoslav/actions/runs/45184089105)
- Verified availability of the dated „Колкострува“ archive and inspected 63 downloads in the 22 November ZIP. The Sofia Burlex branches were „Надежда“ and „Свобода“. Verified a GTIN match for a Techmart and Technopolis handset and noted that Technopolis disallows general automated reads. Eco Petrol adds independent chain coverage. Fuelo needs eligible API access. [Source notes](CODEX_HANDOFF.md#daily-price-source-checks)
- Implemented the signed-out recovery flow and managed-provider bridge. The app accepts the email code and a new password, gives a neutral response to a code request and returns to sign-in after reset. Local browser tests passed invalid code, reuse rejection, old password rejection and new password sign-in. Backend tests reported 112 passed and six disposable PostgreSQL skips. Mobile tests, TypeScript, Ruff and whitespace checks passed. [Sign-in](references/beta-forgot-password-sign-in.png) · [Email step](references/beta-forgot-password-email.png) · [Code step](references/beta-forgot-password-code.png)
- Next use the final checks the owner supplies after reviewing the preview. Verify live recovery with an authorized test inbox before APK approval. Live code delivery and price publication are still open.

## 23 November 2026 — public data and responsiveness audit

- Verified the public data candidates in the handoff, sampled the NSI JSON archive and Open Prices country coverage, and reviewed licence and product-identity boundaries. The most direct next import work is an NSI locality cross-reference for KZP branch matching and a small reviewed exact-GTIN batch. The shared database still has zero verified barcode rows and seven image mappings. [Audit](CODEX_HANDOFF.md#public-data-and-responsiveness-audit)
- Read-only Neon diagnostics showed 15 MB total and about 416 kB estimated table waste. Query statistics were unavailable. The live unfiltered Sofia response carried 875 grocery price rows across two pages and about 40 kB compressed.
- The candidate scopes the price feed by category, renders confirmed prices independently of indicative ones, avoids a duplicate catalogue state update and caches normalized search data. Removed six unused translations. A delayed-source browser test and the 2,000-product search benchmark passed. Mobile tests and TypeScript unused-code checks passed. Backend pytest reported 112 passes and six PostgreSQL-only skips. Ruff and whitespace checks passed.
- Next stage the official-code and barcode mappings in a disposable environment, then measure Android tap and scroll responsiveness, first catalogue paint and cold versus warm network timings when the owner supplies the device checks. No shared imports, database maintenance or APK packaging took place.

## 23 November 2026 — Beta_10.8 preparation

- Reviewed six official locality codes and four handset GTINs. Matched 1,358 КЗП regular price rows by retailer code, catalogue name and address across two existing Burlex Sofia branches. The archive identifies 22 November as the source date. Used EUR under the КЗП source rule.
- Applied migration 0009 and the guarded import on a disposable clone. Replay preserved exact counts of six locality mappings, four verified GTINs and 1,358 historical prices. Applied the same transaction to the shared database. Current prices remained at 875, existing locality count at 5,291, product count at 2,005 and branch count at 286.
- Assigned build sequence 014, app version 0.5.7 and candidate branch `Beta_10.8`. Prepared the full [changelog](../CHANGELOG.md). The deployed barcode endpoint returned the right product and verified GTIN for all four codes and their padded aliases. The exact Beta_10.8 source `d7ab470509da5d9799691f0b76f88fba035ca6ea` passed both hosted PostgreSQL test jobs. A live browser scan from a generated EAN-13 image resolved the expected phone. The sample €4.29 КЗП observation appears in history and its current-price result is empty. [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45188574699) · [Draft PR](https://github.com/Per5on/spestoslav/pull/23)

- The initial Beta_10.8 ARM package passed. The owner then added „За приложението → Трети страни“. Moved the visible source credits into the new section and kept source metadata on the data records. The first artifact is retained and superseded. [First candidate run](https://github.com/Per5on/spestoslav/actions/runs/45188561983) · [Browser preview](references/beta-10.8-third-parties.png)

- Beta_10.8 final source `cb8d73636d6f2d477bf4cabccc285ab2a8daf469`. The updated credits screen passed browser navigation, narrow layout, link and attribution checks. Catalogue and fuel retained the illustrative-photo and indicative-price notices. The signed ARM test APK for source `cb8d736` passed Android CI for `arm64-v8a` and `armeabi-v7a`. Both hosted PostgreSQL jobs passed. Physical installation and camera scanning are pending. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45191123258/artifacts/14826956549) · [Android run](https://github.com/Per5on/spestoslav/actions/runs/45191123258) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45191136452) The downloaded archive and APK both verified. APK SHA-256 `ad5886c126f53102767e2b0cef8b1401893abbde8c3e9bae23e533c6f6f7e385`. The draft PR stays open and the beta backend was not deployed. [Changelog](../CHANGELOG.md) · [Draft PR](https://github.com/Per5on/spestoslav/pull/23)

## 23 November 2026 — Beta_10.8 document review

- Compared `check_and_verify.docx` with APK source `cb8d736` and branch head `f8182a9`. Both hosted PostgreSQL jobs passed. The daily job writes reports only. Live publication needs a schedule aligned to source validity, retailer reuse terms, and counts that distinguish a replay from a source-precedence conflict or lost coverage.
- Confirmed no API-side recovery throttling and that the request route can return a provider 422. Sign-in and recovery already trim email. The existing test covers a rejected code and malformed input. Provider attempt limits, account-neutral outcomes, and session revocation need separate validation before deployment.
- Offline malformed KARAI responses reproduced an uncaught timestamp type error and decimal parse error. The missing SQL delimiter check is defensive because the normal renderer inputs are allowlisted or converted to validated numeric strings. A Techmart product with no eligible offer can be skipped today. An HTTP or SKU error still aborts the batch.
- The existing backlog already covers read-only expired submissions and a dry-run-first receipt orphan sweep. The fixed feedback recipient is an existing project decision. Confirmed 14 new screenshot files and about 8 MiB of current tracked reference files. Keep original records and treat repository layout, attribution-link stability, CI dependencies and app decomposition as maintenance.
- Review only. No implementation, patch application, sweep, deployment or new build. The actionable next work, if approved, is price publication validation and recovery endpoint hardening before live rollout. [Hosted checks](https://github.com/Per5on/spestoslav/actions/runs/45191136452)

## 23 November 2026 — bug-fix build 015

- The owner confirmed missing prices and requested a bug-fix build, a check of expiry, password policy and attempt and search limits, a cached price database, and removal of `docs/12.docx`.
- Isolated PostgreSQL validated 875 Burlex matches, five Techmart matches and 17 KARAI matches. An identical replay wrote zero rows. Applied 51 already reviewed branch records to the shared directory in Varna and Veliko Tarnovo and refreshed the 17 KARAI offers. The live API and browser verified coverage in those locations. The SQLite base passed integrity checking with 1,022 staged observations, 2,005 catalogue records and 1,563 directory records.
- Added API request limits, account-neutral reset responses, read-only expired-submission handling, catalogue price prioritization and resume refresh. Local backend tests, mobile tests, strict TypeScript, Expo dependency checks, Ruff and live browser smoke passed. The scheduled publisher is staged. [Build notes](BUG_FIX_015.md) · [Browser preview](references/bug-fix-015-varna.png)

Build 015 completed at exact source `430abff`. Both ARM ABIs, the signature, download checksums and SQLite integrity passed. Confirmed the €314 Varna basket, locality exclusion, live barcode-image lookup, fixture recovery and private receipt workflow. Physical-device and live managed-auth tests remain ahead. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45210084849/artifacts/14836831458) · [Android checks](https://github.com/Per5on/spestoslav/actions/runs/45210084849) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45210224790)


## 23 November 2026 — Велико Търново device follow-up

- The owner confirmed installation and said the camera appears to work. They reported missing prices and identified Велико Търново. Before the data update, the API returned zero grocery and technology prices, and 17 indicative fuel offers. Build 015 rendered six A95 prices from the live API.
- Checked official Burlex public listings for four already verified branches. Matched regular prices by branch address and exact catalogue code and normalized product name. Isolated publication inserted 617 for Чолаковци, 748 for Търговски парк, 729 for Пазара and 619 for Магро. Identical replay published zero updates.
- The same bounded publication added 2,713 current-price rows to the shared branch. Live API pagination confirmed 835 distinct products and four branches. A live two-item basket returned €4.20 and build 015 rendered bananas from €1.10 in the browser after publication. [Official Burlex table](https://burlex.bg/kolkostruva/)
- The one-time observations expire after 12 hours. The next operational step is to enable a cleared recurring price source and check its coverage before expiry. Technology still needs eligible offers from retailers serving the city. The existing Android APK can consume the update.

- The owner confirmed that grocery prices loaded on their phone in Велико Търново after refreshing build 015. This confirms the device check for the one-time publication. Scheduled publication is still pending.


## 23 November 2026 — nationwide directory validation

- The owner reported missing prices in Пловдив and requested completion of the interrupted nationwide validation. The shared database held 337 directory records before and after this validation. Executed the import on isolated Neon branch `br-steep-violet-bazjkpg3`.
- Seed SHA-256 `94fe35dfa96c3e607b3cc9ca0cb9fc19a87039ec6c730a81d778d41b98043771`. Validated 1,563 records for provenance and canonical locality, then applied 16 bounded SQL batches. The isolated directory grew from 337 to 1,586 total rows. It has 1,585 active branches and retains one inactive legacy record. The replay preserved all row counts and full branch-record digests. The normalized active-branch identity query found zero duplicates.
- The isolated result has 724 fuel branches in 241 localities, 687 grocery branches in 108 localities and 174 technology branches in 55 localities. Пловдив has 41 fuel, 45 grocery and 12 technology branches.
- The paired price-coverage audit at about 21:15 Sofia time found eligible prices in 241 fuel, 2 grocery and 10 technology localities in the isolated result. The shared database returned 3, 2 and 2 respectively. Пловдив had three fuel types, five technology products and zero grocery products with eligible prices in the isolated result. Offer counts are time-sensitive. New directory rows make existing eligible offers visible in their locality.
- The validated nationwide import and existing price coverage audit are ready for live rollout review. The next operational work is publishing the validated directory and identifying a fresh matched grocery source for Пловдив and other uncovered cities.


## 23 November 2026 — nationwide rollout and build 016

- The owner requested implementation of the validation findings and preparation of the next build. Published the exact verified 1,563 seed records to the shared branch in 16 bounded batches. Verified 1,585 active branches and one inactive legacy record. Live API returned 45 grocery, 12 technology and 41 fuel branches for Пловдив.
- Recollected the five reviewed Techmart indicative online offers and 17 KARAI chain offers. Published the same statements after isolated matching. Live Пловдив reads confirmed five technology and 17 fuel offers and zero eligible grocery prices. The first verified technology and fuel offers expire at about 09:22 and 21:22 on 24 November, respectively, Sofia time. The available official grocery archive was dated 22 November. [Official grocery archive](https://kolkostruva.bg/opendata)
- Paired source and locality checks showed current price coverage in 241 of 241 fuel localities, 10 of 55 technology localities and 2 of 108 grocery localities. Eligible prices remain time-sensitive.
- Prepared build sequence 016, label 10.10 and version 0.5.9. Added an empty local price notice in the grocery and technology footer and added the reviewed Велико Търново branches to the staged recurring grocery publisher. The scheduler awaits activation.
- Local backend reported 120 passes and seven PostgreSQL-only skips. Ruff, mobile unit checks, strict TypeScript, Expo dependencies and Android public configuration passed. When the initial request timed out, repeated health, readiness and the direct store and price reads. Live browser retry passed for Пловдив grocery, technology and A95 fuel. [Visual proof](references/preview016-plovdiv-grocery.png)
- Android packaging remains the next step for the prepared candidate. Verify the managed recovery settings and grocery-source coverage separately.

- Recorded the build 016 release plan after the owner requested a TODO and future-release changelog. Both hosted PostgreSQL jobs passed for candidate `dcbdea2`. Packaging, device verification, recurring source publication and live account and email checks remain open. [Release TODO](PREVIEW_006_BACKLOG.md#build-016-release-plan) · [Hosted checks](https://github.com/Per5on/spestoslav/actions/runs/45249343835)


## 23 November 2026 — subscription planning and historical defects

- Drafted the future subscription plan with a free comparison tier, a proposed Plus alert tier, tentative pricing, Play Billing integration and launch checks. [Plan](SUBSCRIPTION_PLAN.md)
- The owner asked to focus remediation on historical defects. Reproduced the receipt upload cleanup problem when a database commit succeeds and its reply is lost. The candidate preserves the referenced image in that case, returns a retryable 503 and recovers the original receipt on a same-key retry. A known pre-commit failure still cleans up its image. Storage cleanup errors preserve the original failure result.
- Local backend tests reported 122 passes and seven skipped PostgreSQL-dependent checks. Ruff and whitespace checks passed. Updated the backlog to reflect the existing expired-submission fix and retain a report-only orphan audit, live account/mail checks and price coverage as open. [Remediation TODO](PREVIEW_006_BACKLOG.md#historical-defect-remediation)
- Both hosted PostgreSQL jobs passed for receipt fix source `0c2afb8`. The next check is receipt retry behavior on the deployed backend. [Hosted checks](https://github.com/Per5on/spestoslav/actions/runs/45251812461) Paid checkout and Android packaging remain separate approval steps.


## 23 November 2026 — saved theme at startup

- The owner reported a brief default-theme flash before the saved theme was restored. The candidate waits for saved preferences and dismisses the Android splash after the themed screen is laid out.
- The browser regression deliberately delayed preference restoration and confirmed the header was absent during the read. The first header used the saved custom palette and the location field used dark mode. Responsive checks in six languages, mobile unit tests, strict TypeScript, Expo dependencies and generated Android splash configuration passed.
- Next verify a cold start on a physical Android phone with a saved custom palette and with dark mode after build 016 is packaged.

## 23 November 2026 — catalogue loading and Android background sync

- The owner reported slow catalogue loading, especially „Горива“, and uneven behavior across tabs. The old app saved grocery and technology product metadata. Fuel products, local branches and both price feeds started with network reads.
- Candidate 016 saves fuel product IDs and type mappings and keeps separate caches for local branches, confirmed prices and indicative prices. It shows saved rows by category and exact locality while refreshing and discards expired offers. Cache entries for quotes expire after 24 hours at the latest. It fetches the other tabs after the active tab settles and shares concurrent requests for the same data. A successful empty response replaces old results and a network error preserves usable cached rows.
- Android gets pull-to-refresh on each catalogue tab and a connected WorkManager job targeting a minimum interval of 60 minutes. It fetches public data for the saved town. The server-side source publication schedule remains a separate rollout item.
- The delayed Sofia browser fixture showed a saved A95 price in 140 ms after switching tabs, before the held fuel requests returned. It replaced the saved price when the response arrived and cleared it when switching to Пловдив. The mobile suite verifies same-scope request sharing, expiry, loss of connectivity, erasure and mocked Android task registration. TypeScript, responsive browser checks and Expo configuration, module linking and Android JavaScript export passed.
- Next after packaging approval, verify pull-to-refresh, timed cold and warm loads, and an actual Android background job on an ARM phone. [Release TODO](PREVIEW_006_BACKLOG.md#build-016-release-plan)
- Both hosted PostgreSQL jobs passed for catalogue sync source `504f36b`. A second browser run confirmed that leaving „Храни“ open warmed the fuel and technology caches before either tab was selected. [Hosted checks](https://github.com/Per5on/spestoslav/actions/runs/45254713574)


## 23 November 2026 — release documentation and repository rename

- Amended the unreleased build 016 notes and TODO to list Android pull-to-refresh individually, explain cache-first loading and background sync, and distinguish the browser evidence from the pending physical-device tests. Retained the owner’s request in the project communication log.
- Confirmed repository ID `1457549969`, no GitHub Pages site and no resolved repository at the proposed name. A settings permission check using the existing name returned HTTP 403 from GitHub. The current name and remote still resolve to the existing project.
- The latest available scheduled receipt worker run passed under the current name. The live service rejects unauthenticated worker claims, and the worker identity verifier pins the current slug in the signed subject and workflow reference. Prepared draft PR #25 to support the old and new names using matching claims, the same immutable IDs, and the existing main-branch and GitHub-hosted runner constraints. All 18 focused tests passed locally. The full local suite reported 99 passed and seven PostgreSQL-only skips. Both hosted PostgreSQL checks passed for `67429c0`. [Compatibility CI](https://github.com/Per5on/spestoslav/actions/runs/45255569838) · [Worker run](https://github.com/Per5on/spestoslav/actions/runs/45135180840) · [Compatibility PR](https://github.com/Per5on/spestoslav/pull/25)
- Next, approve and deploy the isolated compatibility patch and rename the existing GitHub repository from a session with Administration write access. Verify the unchanged repository ID, pull requests and scheduled worker, then update the local Git remote and current links. APK approval remains pending. [Rename checklist](PREVIEW_006_BACKLOG.md#repository-rename)


## 23 November 2026 — thumbnail database and visual reconciliation

- The owner deferred the repository rename and reported missing and visually inconsistent product images. They requested inspection, release documentation and backlog closure after build verification.
- A read-only database query confirmed 14 group/category symbols in `spestovnik_thumbnails`, all 160 × 140, totaling 13,600 bytes. The live API was ready and both catalogue snapshots returned 200. Its OpenAPI schema omitted the thumbnail routes and the manifest returned 404. The candidate source includes the route and server-side database configuration. The mobile catalogue renders `image_url` or bundled artwork and has no manifest lookup. [Live manifest](https://spestoslav-api.onrender.com/api/v1/thumbnails)
- The live catalogue snapshots returned 1,000 products per tab. „Храни“ had six links, covering two records each for bananas, lemons and carrots. „Техника“ had one link, for Samsung Galaxy A17. All seven images returned HTTP 200 and decoded as 160 × 140 WebP. The local visual inspection found realistic milk, oil and sugar references, grocery outlines, colored technology pictograms, a cup for kettles, and a sharp product photo for the Galaxy. The database symbols are a further green-outline set.
- Added the production route and app wiring, matched artwork and coverage, cached update behavior, and device acceptance to the release TODO. Mark backlog items resolved after the installed build and applicable live checks pass. The thumbnail work remains pending, and the APK still awaits approval. [Release TODO](PREVIEW_006_BACKLOG.md#thumbnail-reconciliation) · [Future changelog](../CHANGELOG.md#planned-for-the-next-approved-build)
