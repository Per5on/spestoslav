## NEW OWNER DIRECTIVE — 19 November 2026: backend-first redesign; builds on hold

**Authoritative TODO:** [PREVIEW_006_BACKLOG.md](PREVIEW_006_BACKLOG.md), section "Owner change request — 19 November 2026". The section records the exact UI, images, palettes, merchant directory, cleanup, dependency audit, and 3-pass validation requirements. Apply against **latest** `main` and `codex/preview-007`; older Preview006 branch is a planning lane, not necessarily the implementation base. Do not start any build until the owner confirms after the three checks, notwithstanding previous Preview007 build approval.

**Initial source review (not runtime verification):** `backend/app/catalog_api.py` already filters active retailers by active `StoreBranch.locality_id` in `/catalog`; `backend/app/models.py` has `StoreBranch.locality_id`, `address`, `active` and index `ix_branch_locality`. `mobile/src/catalog/useCatalog.ts` fetches `/api/v1/stores?locality_id=...&category_code=...` only with selected locality, and `/api/v1/catalog?category_code=...` for retailer directory. This supports a read-only, category/locality-address menu after contract/scale review; it does not establish national physical coverage. `codex/preview-007/mobile/App.tsx` still contains the product/store view toggle, five fuel selector and group chips; `mobile/src/i18n.ts` still labels list as `Моят списък`. Product images are sourced from backend `image_url` and must be changed with licensing/attribution review. No backend or frontend implementation, package deletion, CI run, or build has been performed for this new request yet.

---

## Preview 006 code review notes — 16 November 2026

Full targeted review: [PREVIEW_006_CODE_REVIEW.md](PREVIEW_006_CODE_REVIEW.md); discussed on [draft PR #13](https://github.com/Per5on/spestoslav/pull/13). Review covered backend/data, frontend, and security/build. It was targeted source inspection, **not** a full security audit or completed feature acceptance.

**High-priority findings and work:**
- **Product images:** shared Neon preview DB has 1,000 products but **0 product_images**. Verify image licensing/source URLs, populate approved image metadata, and test Android thumbnails and fallbacks.
- **Petrol stations:** 7 fuel retailers but only **2 active fuel branches**. Validate/import real branches and ensure category/locality filtering returns them. Do not invent locations or live fuel prices.
- **Store discovery:** `mobile/src/catalog/useCatalog.ts` fetches stores only when `localityId` exists. Verify no-locality UX and locality-specific coverage.
- **Release gate:** green backend and Android 10 smoke CI on previous candidate is **not** proof of feature completeness; PR #13 remains draft and automatic publication blocked.

**Medium-priority findings and work:**
- `backend/app/main.py:96-148` locality search uses `LOWER(...) LIKE '%term%'`; measure real latency/query plans and consider suitable indexing/search strategy.
- `mobile/src/api.ts` and `mobile/src/location/LocationPicker.tsx` allow 60-second request timeouts; catalog fallback pages are fetched sequentially in `mobile/src/catalog/cache.ts` and `useCatalog.ts`. Optimize with bounded timeouts, caching/snapshot and measured behavior.
- `mobile/App.tsx` Settings has not been redesigned: black text/white background, compact font-height icons, thin padding, responsive two columns, accessible touch targets, six languages.
- Feedback currently shows `feedbackPending`; implement sender/email/message form and backend-managed delivery to configured recipient with validation, rate limits, provider secrets and honest success/failure status.
- Add explicit negative tests for expired/invalid sessions, cross-user receipt access, oversized image uploads and provider failures. **No security exploit was confirmed.**
- Health/HTTP 200 checks do not prove nonempty stores, fuel coverage, images or price records; add release-level data completeness assertions.

**Verification order:** backend sources and Render/Neon live data → backend/API performance and coverage fixes → frontend/settings/feedback fixes → three full code/integration, connections/sources, and Android 10 native/functional passes on the **same final commit**. Record run links, before/after counts and latency, screenshots and email-provider delivery evidence. Preserve Preview 005; do not merge or publish Preview 006 until all release criteria pass.


# Ongoing project handoff

## Preview 006 implementation active — 16 November 2026

- Owner confirmed successful Test_postpreview-005 checks and authorized combining Issue #10 with [PREVIEW_006_BACKLOG.md](PREVIEW_006_BACKLOG.md), inspecting backend first and building the Preview 006 candidate. Dedicated branch `codex/preview-006` forked from green post-preview SHA `baa8e1a`; Preview 005 remains published and unchanged.
- Development workflow deliberately **blocks automatic publication** on `codex/preview-006` until three new verification passes are recorded. First implementation: shared toolbar labels reduced by 1pt and visible green outlined `Обнови` with wider padding. Remaining Settings, email delivery, live stores/fuel/images/location fixes are **not yet complete**.
- Before declaring Preview 006 ready: finish every backlog item, verify live Render/Neon data and API latency, test backend + frontend + Android 10 three times on final source, and only then explicitly promote the new numbered release. Do not mistake CI compilation for feature completeness.


## Owner gate — await post-preview Actions result before Preview 006 work

- Owner instruction (16 November 2026, 12:28 UTC): **first inspect the result of [Android run 43865608214](https://github.com/Per5on/spestoslav/actions/runs/43865608214) on `Test_postpreview-005`, then re-review the code, then implement the already documented Preview 006 features only if verification is successful.** If it fails, diagnose and fix the existing post-preview baseline before adding features. No automatic merge, build promotion, or release is authorized by an intermediate result.
- At the time of recording: that run was **in_progress** at the Android 10 smoke test; its matching backend workflow 43865608258 **passed**. Newer head `9e8022c` had backend success (43865661833), but its Android workflow 43865662029 was also in progress. Check both the named run and **latest PR #11 head** before the decision: an earlier passing run does not validate a newer commit.
- Record final CI status, failing step and diagnostic artifact or passing evidence in `docs/ACTIVITY_LOG.md` and PR #11. **Three final verification passes** and backend/frontend feature checks remain mandatory before any Preview 006 release.


## New Preview 006 work — 16 November 2026

**Read [PREVIEW_006_BACKLOG.md](PREVIEW_006_BACKLOG.md) before implementing Issue #10.** Owner reports empty stores, missing product photos/thumbnails, empty petrol stations, and slow location search; requests backend verification **first**, then frontend fixes. Settings in the three-dot menu must use black text on white, compact font-height icons/button shapes and optionally responsive two-column choices. All tasks stay on `Test_postpreview-005` / draft PR #11; three complete verification passes remain required. Published Preview 005 stays intact.

## Branch isolation and conditional Preview 006 — 16 November 2026

- **Preview 005 remains on PR #9 / `codex/preview-005-grocery-workflows` for its independent Android 10 barcode verification and pending release decision. Do not merge post-preview feature work into that branch while it is under verification.**
- **All Issue #10 toolbar and backend/frontend feedback work belongs to the separate `Test_postpreview-005` branch.** Treat it as an experimental source tree, not an approved or released numbered preview. Keep its own CI evidence, tests, and build artifacts separate from Preview 005.
- **Conditional decision, not automatic release:** After Preview 005 checks finish, owner may choose to abandon publishing Preview 005 and instead promote the fully verified post-preview branch as **Preview 006**. This requires a separate explicit release decision, updating `mobile/preview.json` and corresponding registry/release metadata to 006, three complete verification passes on the exact promoted source, and a fresh native build/emulator barcode test. Do not rename or republish a 005 artifact as 006. Preserve all previous releases and never overwrite numbered assets.
- **GitHub Actions logs:** post-preview CI must emit the branch identity, candidate status, and conditional 006 decision in the job summary/log. This is a documentation/traceability note, not permission to skip release gates.

## Latest owner instruction — 16 November 2026

**Codex must implement [Issue #10](https://github.com/Per5on/spestoslav/issues/10) before final build confirmation.** This includes the shared toolbar 1pt label reduction and green-bordered wider “Обнови” button; backend-delivered “Обратна връзка” form with fixed non-editable email destination; and **three separately evidenced verification passes across backend, frontend, and Android 10 emulator**. Issue #10 includes today's barcode scanner commits and current PR #9 release gate. Do not claim real email delivery without provider evidence, do not bypass EAN13 native scan assertion, and preserve all earlier numbered releases.


Start with [PROJECT_STATUS.md](PROJECT_STATUS.md) and the newest [ACTIVITY_LOG.md](ACTIVITY_LOG.md) entry. This is one continuing project; do not reread the old conversation each day.

Current work is preview 005: catalogue/cache, camera/barcodes, private receipts/review/comparison, Issue #8 menu/Settings/About, task 3 toolbars/header/fuel types, then the preview004 cleanup review. The owner authorized building 005 **after all fixes and checks pass**. No earlier build hold should be interpreted as requiring a second confirmation after that condition is met.

- Confirmed UI: [FRONTEND_BRIEF.md](FRONTEND_BRIEF.md).
- Numbered releases: [CHANGELOG.md](CHANGELOG.md), [artifact registry](references/preview-sequence.json). Preserve 001–004 and their source images/APKs.
- Verification: [mock scenarios](MOCK_SCENARIOS_005.md), [preview004 code review](CODE_REVIEW_004_2026-11-16.md).
- Backend paths: [migration strategy](decisions/migration-strategy.md), [readiness](BACKEND_READINESS.md).
- Pending app identity: `mobile/preview.json`; derive the launcher label/versionCode/workflow from it. `scripts/set_preview_version.py` updates generated metadata without building.

[Original handoff and historical snapshot](archive/CODEX_HANDOFF_before_2026-11-16_consolidation.txt) is retained for missing details, not as current instructions. Current architecture is React Native/Expo/TypeScript + FastAPI/Python + Neon PostgreSQL + Render; active logo is the money bag. Home/postal storage is retired. Free shop routing is planned; paid alerts remain deferred.
