# Project activity log

Append dated entries. Keep the current resume point in `PROJECT_STATUS.md`; older entries are historical evidence, not current test/deployment claims.

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

## 17 November — PR #15 reconciliation and compatibility

- Owner explicitly requested closure/relocation/existing-record reconciliation and successful exact-commit CI. Isolated inventory worktree from c791beb4; merged current main39304dc locally and resolved seed conflict by preserving143rows in current13-column no-postal schema. Mobile and Android workflow remain identical to main; no006/007 UI work merged.
- Fresh official HTTP200 checks: Mini Mart current357feed records, nine retained addresses, duplicate feedIDs75/118; HristoBotev75 still pending/inactive, not closure proof. T MARKET four confirmed closures absent from preview; seven alternative branches unchanged; verified new Банско and relocated Тетевен address, former address unspecified and not invented. Nine CBA directory affiliations/addresses checked.
- Fresh read-only139branch baseline produces138unchanged,5insert candidates,1inactive history retained. Row-level snapshot/report/source excerpts committed as reproducible evidence; no shared data writes. Importer now has explicit current/legacy-preview modes, normalized duplicate/closed/pending rejection and bounded lock; tests exercise atomic/idempotent SQL on both schemas and complete139+5local replay with preserved history, second run no-op.
- Next: inspect successful CI on final inventory commit, record its URL and compatibility state. Keep PR draft/import gate until reviewed preview import step. Preview007 build hold remains in force.
