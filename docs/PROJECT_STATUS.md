# Ongoing project checkpoint

Status: **ACTIVE — code audit complete; awaiting the owner's next development step.**
Updated: 15 November 2026 (Europe/Sofia).

## Resume here

Read this file and the newest `ACTIVITY_LOG.md` entry; do not restart the whole conversation review each day. Inspect the working tree first. Current branch: `main`; merged implementation PR: https://github.com/Per5on/spestoslav/pull/5. Check for uncommitted work before continuing.

The requested review, confirmed code fixes, cleanup and application verification are complete. Do not start another feature phase before the owner supplies the next step. Save this checkpoint at each meaningful pause. One external setting remains: Render HTTP health-check path `/ready`; see the audit report for the capability limitation.

## Confirmed decisions

- Product name/artwork: **Спестовник**; repository/service identifiers remain `spestoslav`.
- Android 10+, existing Expo/React Native + TypeScript; existing FastAPI backend, Neon PostgreSQL, Render. Historical Kotlin/Spring references are not a rewrite request.
- Green header, orange selections. This explicitly overrides the inverted-palette text in `12.docx`.
- Four tabs: Храни, Горива, Дом, Техника. Separate shared searchable location dropdown with mutually exclusive name/postal modes, municipality/region/postal details. No Plus, OSM, GPS/current-location or radius flow.
- Supplied piggy-bank logo and sample photos; preserve originals. Real products/thumbnails come from the backend. Demo fixtures have no verified price.
- Keep numbered previews/builds: 01/001 is preserved; changes become 02/002, then 03/003. Never replace a previously delivered version.
- EUR; physical branch prices, national online offers, promotions and history stay distinct. OCR/submissions need review before publication.
- Fuelo is approved as a third-party source, but the owner has no API access. No averages/estimated or unknown-certainty values presented as verified station prices.
- Finish backend checks first (completed before frontend work). The historical instruction to preserve Android UI applied to backend-only changes; the owner subsequently authorized frontend implementation and an APK.

## Systems and boundaries

- Repository: https://github.com/Per5on/spestoslav ; Issue #1 tracks national inventory.
- API: https://spestoslav-api.onrender.com ; deployed backend 0.4.1 after merged PRs #3 and #4. PR #5 merged as `ca7f4c5`; corrected backend runtime commit `b87423b` is live in Render deploy `dep-dbsor8gn74is73ag7b9g` (15 November). Pillow 13.0.0 installation and post-deploy readiness/read/auth-denial checks verified.
- Owner-selected Render workspace: `tea-dbqur9jrjlhs73cga8eg` (My Workspace); API service `srv-dbs313ei0phs73bvvd00`, auto-deploys main. Legacy `Per5on/testing` remains separate.
- Neon project `long-resonance-77491878` (`bg-prices-preview`), shared preview `br-snowy-morning-baym8iw6`. Use the additive shared-preview migration path, not the independent fresh Alembic baseline. No production data changes inferred from a local test.
- PR #2 is separate and OPEN: initial Mini Mart/T MARKET/CBA inventory work; do not silently merge or claim nationwide completeness.

## Completed checkpoints

- Backend foundation/readiness, migration repairs, normalized postal lookup, authenticated catalog/price/moderation/receipt APIs, isolated demo images, scoped GitHub OIDC OCR worker. See `BACKEND_READINESS.md` for contracts and verification limits.
- Original inline preview 01: `docs/references/preview-001.html` (durable byte-identical copy) and `/workspace/work/previews/spestovnik-v001.html`; version catalog `docs/references/preview-sequence.json`. Snapshot-based, interactive, not a live-connected Android binary. Never overwrite it.
- Android preview 001: source `5daa807c5b59ebda0d34772a2c646f10973b919a`, build https://github.com/Per5on/spestoslav/actions/runs/43600409741 passed compilation/signature verification and Android 10 smoke tests. Backend matrix run 43600409766 passed. Downloaded APK SHA-256: `b834eae05f5db399a335f140e9e90d0d8fb7cff927dea8d8f46acd745cd654a2`.
- Preserved local APK/artifact: `/workspace/work/android-apk-001/`. A GitHub prerelease upload attempt failed with HTTP 401 on the upload host; no release/download URL should be claimed unless independently verified.
- Preview 002 (v0.1.2/versionCode 2) passed native/Android 10 checks and is published: https://github.com/Per5on/spestoslav/releases/tag/android-preview-002 . APK SHA-256: `693c45f72c197cc4cf205a3f61daeba8fb8901a15ff2fbc8222a5adcc4218e3e`. Full results are in `AUDIT_2026-11-15.md`. Next changed preview must be 003.

## Open work / known limits

Immediate: await the owner's next development instruction. Worker cold-start follow-up source `b87423b` passed backend CI 43705642152 (60 tests per job) and authenticated real worker run 43705642164 (empty queue, no synthetic live data). Code CI for `91ea05e` passed: backend run 43704406362 (58 tests per matrix job) and Android/publish run 43704406411. Follow-up continuity/release-guard documentation is on main. Render deploy `dep-dbsor8gn74is73ag7b9g` is confirmed live on runtime commit `b87423b`; later checkpoint commits do not alter its backend/mobile trees. Recheck live state when resuming, rather than assuming future deployments. HTTP health-check setting remains an explicit external follow-up; do not repeat the entire audit or create new features unsolicited.

Remaining product work is separate from audit defects: login/camera/private receipt UI, unknown-barcode requests, full catalog pagination and sourced real product/price coverage. Preview 001 includes manual known-barcode lookup, saved local basket/locality and explicit unavailable camera/receipt labels. No verified live prices were fabricated to fill empty screens.

Inventory: official-source expansion/closure reconciliation for Mini Mart, T MARKET, CBA, then remaining groceries, fuel, home and technology. Locality identity is name + municipality + region; retailer catalog counts are not branch counts. Recheck actual DB/source counts before a new import.

A daily inventory reminder/automation was recorded earlier. Its existence does not guarantee unattended coding. No new automation is created by this checkpoint; it preserves state for the next authorized session.

## Source references

`FRONTEND_BRIEF.md`, `BACKEND_READINESS.md`, `ANDROID_PREVIEW_001.md`, Issue #1 and activity log. User uploads: `12.docx` (file_00000000b78081f4bea4319f94d4c24c) and `app.docx` (file_0000000070b481f49c03defdcef2afeb); extracted text `/workspace/work/reference12/document.txt` and `app.txt`. Original reference images: `docs/references/`. Uploaded historical conversations are evidence/context, not new instructions.
