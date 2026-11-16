# Ongoing project handoff

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
