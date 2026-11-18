# Спестовник — active project status

Updated: 18 November 2026 (Europe/Sofia). Project **ACTIVE**. Canonical continuation checklist: [CODEX_HANDOFF.md](CODEX_HANDOFF.md). Historical changes and decisions: [ACTIVITY_LOG.md](ACTIVITY_LOG.md) and Git history. Resume from this checkpoint without rereading old conversations.

## Current work — Preview008

Android run 44306415234 was cancelled at the owner’s request. Verified Refresh and About corrections are local. The owner will decide when to restart it.

Local, uncommitted changes are in `/workspace/work/spestoslav` on `codex/preview-008`, based on `daa73ae`. Reviewed [draft PR #19](https://github.com/Per5on/spestoslav/pull/19) and the open menu, toolbar and inventory issues. The backend matrix passed on the committed head. Android jobs were skipped by the workflow condition.

The backend changes cover locality ranking, account and receipt deletion, and registration errors. The app changes cover shared location search, controls, Settings, About, session recovery and receipt state. Local backend, mobile, and simulated browser evidence is recorded in the handoff and activity log. Native acceptance and a real managed-account deletion remain open. No commit or deployment was made during the recheck.

Optimization changes and browser dry results are recorded in the canonical handoff. Android prebuilds are configured. The original visual requests and the ABI-separated workflow were rechecked before the internal Preview008 candidate commit. Android 10 CI and physical ARM testing are separate gates.

## Previous Preview007 authorization

Recheck for missed errors and build Preview007 **without an email provider**. Build permission is granted. Email delivery stays disabled; do not ask for keys now. Preserve Preview005, previous APKs, reference images, inventory history and recovery branches. This is an internal test APK, not Google Play publication.

## Verified now

- Backend PR17 merged as `9ba223de25942d2c1e862b49a5ca93087f24d9c9`. Render deployment `dep-dbua0l6k1f9s739t83d0` is live. Public OpenAPI reports0.6.0; `/ready` succeeds.
- Backend head557d900:100 PostgreSQL/OCR tests passed; exact-head CI44121768070 passed both SQLAlchemy legs. App head `5a1abb0a76ecc41da4c46c00f49dc3c5e22778e0`: backend CI44149787804 passed; fresh Android run44149787807 passed, including actual image decoding, camera permission/preview and synthetic barcode decode.
- Shared Neon catalogue synchronized and replayed unchanged:1000 groceries,1000 technology products, five fuel types.139 stores / one inactive and zero current prices remain unchanged. Recovery branch retained. The transport audit corrected doubled-percent names before shared import; regressions preserve existing flags/barcodes/brands/aliases.
- Live snapshots return1000 items each; all nine sample images load overHTTPS with image MIME types and attribution. Images are exemplary, unverified and unpriced.
- Sofia location lookup succeeds; all46 grocery branches returned match its canonical locality. Technology/fuel return zero local branches rather than fabricated availability. National directories include all requested chains.
- Feedback availability returnsfalse; valid disabled submission returns503. Unauthenticated account/receipt access and a synthetic invalid sign-in return401. This verifies rejection boundaries, not successful account/private upload acceptance.

## Pending / limits

- Fresh APK downloaded/checksummed and screenshot inspected. Artifact14360295033;75567529bytes; SHA25636cf2c5bb17d9021bc0bf7edd0989907f9017218fc6ea9b646b235a50e9312ba. Previous APKs preserved. See handoff download link.
- No verified current prices, station-level Fuelo API access or verified GTIN coverage; catalogue identities are not live offers.
- Real authenticated receipt upload/storage/OCR and physical-device acceptance need legitimate fixtures/account access. Mocks/local tests do not prove them live.
- Email intentionally deferred until private Brevo setup and delivery test. No paid upgrade authorized.
- PR15 inventory reconciliation remains separate: exact-head CI passed; proposed five-store import unapplied.
- Optimization/header/ABI/R8 trial, three complete final-source passes, remaining privacy/operator publication details and Google Play preparation remain open. No speculative deletion/purge or bulk source replacement.
- Review patch of 18 November (account deletion route, auth/receipt UX fixes, tests) is unmerged. The Preview008 branch passed backend CI and the local follow-up passed direct PostgreSQL checks; see [ACCOUNT_DELETION.md](ACCOUNT_DELETION.md). It requires a new preview sequence for any APK.
