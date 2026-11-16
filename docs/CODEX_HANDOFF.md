# Ongoing project handoff

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
