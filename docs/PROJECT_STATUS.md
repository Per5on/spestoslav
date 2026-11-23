# Спестовник — active project status

Updated: 23 November 2026 (Europe/Sofia). Project **ACTIVE**. Canonical continuation checklist: [CODEX_HANDOFF.md](CODEX_HANDOFF.md). Historical changes and decisions: [ACTIVITY_LOG.md](ACTIVITY_LOG.md) and Git history. Resume from this checkpoint without rereading old conversations. The reconstructed and ongoing decisions are in the [project communication record](PROJECT_COMMUNICATION.md).

## Current work — build 016 candidate

The reviewed nationwide directory is live with 1,585 active branches across its three categories. At the verification snapshot, eligible prices were returned for fuel in 241 localities, technology in 10 and groceries in two. Пловдив has 41 fuel, 45 grocery and 12 technology branches. It has 17 indicative fuel offers and five indicative technology offers. A matched fresh grocery feed for the city is still needed.

Candidate 016, display label 10.10 and app version 0.5.9, explains empty local price coverage in the grocery and technology footer. The staged grocery publisher includes the four reviewed Велико Търново branches. Browser checks used the live API and showed the Пловдив grocery notice, five technology offers and six A95 prices. The candidate also restores the saved theme before the first app screen. The delayed browser preference test passed. Android package generation and device cold-start verification are pending. The next steps are recorded in the [release TODO](PREVIEW_006_BACKLOG.md#build-016-release-plan) and [unreleased changelog](../CHANGELOG.md#unreleased--build-016--app-059). [Preview](references/preview016-plovdiv-grocery.png) · [Rollout evidence](ACTIVITY_LOG.md#23-november-2026--nationwide-rollout-and-build-016)

The candidate now saves catalogue results by selected town, including fuel products, branches and valid prices. It prepares the other tabs after the current tab loads and schedules connected Android background updates with a one-hour minimum interval. Pull-to-refresh uses the same data loading in all three categories. A delayed browser check confirmed that saved fuel prices appear before the network reply, fresh results replace them and a locality change hides the previous town's prices. The next check is actual Android job execution and refresh behavior after packaging approval. [Catalogue sync checks](ACTIVITY_LOG.md#23-november-2026--catalogue-loading-and-android-background-sync)

The owner reported that product thumbnails still fail to populate consistently and mix visual styles. The dedicated database has 14 seeded symbols, but the live thumbnail manifest returns 404 and the current catalogue screen does not read it. Only seven of 2,000 live catalogue products have individual image links. The open release tasks cover production delivery, verified matching, a unified style and installed-app acceptance. [Thumbnail release tasks](PREVIEW_006_BACKLOG.md#thumbnail-reconciliation)

The owner deferred the GitHub repository rename to `Per5on/spestovnik`. The receipt-worker compatibility patch remains in draft. [Compatibility PR](https://github.com/Per5on/spestoslav/pull/25)

The future subscription proposal documents a free comparison tier and a possible paid alerts tier. Current remediation targets historical defects. Receipt commit-response recovery is implemented in the candidate and verified locally. Backend rollout remains pending. [Subscription plan](SUBSCRIPTION_PLAN.md) · [Remediation TODO](PREVIEW_006_BACKLOG.md#historical-defect-remediation)

## Bug-fix build 015

Prices now appear in live verified Varna technology and fuel and Veliko Tarnovo fuel after the reviewed directory additions and the KARAI refresh. Sofia grocery availability remains a pilot. The four-hour publisher and account/search safeguards are staged. The signed ARM APK and both hosted PostgreSQL jobs passed for source `430abff`. The owner confirmed installation and reported that the camera appears to work. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45210084849/artifacts/14836831458) · [Android checks](https://github.com/Per5on/spestoslav/actions/runs/45210084849) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45210224790) [Build notes](BUG_FIX_015.md) · [Browser evidence](references/bug-fix-015-varna.png)

**Велико Търново device report.** The city had no current grocery or technology prices when the owner tested. After a focused Burlex publication, the deployed API returned 2,713 current prices for 835 products across four branches. Build 015 rendered those prices in a live browser check. The owner then confirmed that refreshing on their phone loaded grocery prices. The browser check also showed six indicative A95 prices. Technology coverage and recurring grocery publication are open. The first new grocery observations expire at about 08:26 on 24 November, Sofia time. [Activity log](ACTIVITY_LOG.md)

**Nationwide directory validation.** The isolated database accepted all 1,563 reviewed seed records in 16 batches. A complete replay preserved every stored branch. The result includes 41 fuel, 45 grocery and 12 technology branches in Пловдив. The test snapshot supported indicative fuel prices in 241 localities and technology prices in 10. Grocery price coverage was still two localities. See the current build notes above for the follow-up rollout. [Validation evidence](ACTIVITY_LOG.md#23-november-2026--nationwide-directory-validation)

## Beta_10.8

The owner requested the Beta_10.8 build and a changelog covering all versions. It uses sequence 014 and app version 0.5.7. The shared API database now contains six official locality mappings, four corroborated GTINs and 1,358 historical grocery observations. The isolated import replay preserved IDs and current prices. The refreshed candidate adds „За приложението → Трети страни“ and puts attribution links there. [Changelog](../CHANGELOG.md) · [Browser preview](references/beta-10.8-third-parties.png)

**Beta_10.8 APK ready for device testing.** The signed ARM test APK for source `cb8d736` passed Android CI for `arm64-v8a` and `armeabi-v7a`. Both hosted PostgreSQL jobs passed. Physical installation and camera scanning are pending. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45191123258/artifacts/14826956549) · [Android run](https://github.com/Per5on/spestoslav/actions/runs/45191123258) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45191136452) Live password recovery still needs the beta backend deployed. Feedback delivery still needs its production mail setup and a live test.

The owner requested an applicability review of `check_and_verify.docx`. It confirmed that the daily workflow monitors sources without publishing prices and that the candidate recovery endpoints rely on provider-side limits. Recorded the release priorities, corrections and existing backlog in the [activity log](ACTIVITY_LOG.md#23-november-2026--beta_108-document-review).

### Preview 010.7 and beta preparation

Backend cleanup is prepared in the working tree. It consolidates catalogue and receipt review helpers, tidies imports, and adds a pinned Ruff check to backend CI. Local checks passed. [Activity log](ACTIVITY_LOG.md).

The next backend commit tasks include a read-only expiry fix and a dry-run-first receipt orphan sweep. The expiry variant passed a focused SQLite check in isolation. The sweep is queued for adaptation and disposable-storage verification. [Commit tasks](PREVIEW_006_BACKLOG.md#23-november-2026--next-commit-and-beta-checklist).

The owner added the header, catalogue, fuel, locality, and live price requirements for the next beta. Visual review comes before including the changes in the build or APK commit. APK packaging requires explicit approval after code review, backend verification and dry tests. [Next commit and beta checklist](PREVIEW_006_BACKLOG.md#23-november-2026--next-commit-and-beta-checklist).

The live Sofia catalogue now has 34 technology branches, 113 petrol stations, 875 regular grocery branch prices and seven source-backed WebP links across the two product catalogues. A backend-only fix that restricts nationally published prices to retailers with active stores in the selected locality and restores the merchant directory passed CI and merged. Render is live on the exact merge. A real two-item Techmart basket returned €303.99 in Sofia and no Techmart quote in Мадан. The live API also returns 17 indicative chain fuel prices across six retailers. Scheduled refresh, wider price and image coverage, and beta APK approval remain pending. [Backend PR 22](https://github.com/Per5on/spestoslav/pull/22) · [Comparison](references/beta-live-sofia-comparison.png) · [Fuel](references/beta-live-sofia-fuel.png).

The fuel candidate groups shared chain estimates into one row with the local branch count. Confirmed station prices that differ appear below the estimate with their address. Live Sofia data and an injected exception passed the browser checks. The isolated browser workflow also passed camera and barcode fallback, sign-in, receipt upload, Bulgarian OCR, review and deletion. Live sign-in and receipt acceptance require an authorized test account. Live feedback remains unavailable. [Grouped fuel preview](references/beta-live-sofia-fuel-grouped.png).

The price-source workflow is now on the default branch with daily checks for „Храни“, „Техника“ and „Горива“. The first hosted run passed for all three categories and generated reports. Live publication and validated fallback matching remain open. „Забравена парола“ is implemented in the app and backend candidate with a passing local browser workflow. Live code delivery is unverified. The owner will report the physical-device check. [Beta checklist](PREVIEW_006_BACKLOG.md#backend-and-beta-acceptance) · [Recovery preview](references/beta-forgot-password-code.png).

A data and performance audit verified public sourcing candidates, measured the 15 MB database, and identified cross-category price overfetch. Candidate changes narrow the price feed, decouple confirmed and indicative responses, and index product search. Local browser and code checks passed. The reviewed locality and barcode pilot is recorded above. On-device responsiveness remains pending. [Audit](CODEX_HANDOFF.md#public-data-and-responsiveness-audit).

The candidate implements the approved itemized comparison, both group pop-ups, palette removals, and the licensed thumbnail pilot. Pre-build checks passed. The owner approved internal ARM packaging after the 10.6 verification. Live API rollout, physical-device acceptance, and broader product-image coverage remain pending. [Handoff](CODEX_HANDOFF.md) · [Comparison preview](references/preview-10.5-comparison.png)

22 November layout and artwork update passed local checks. x86_64 packaging and hosted emulator verification were removed. The next approved build will package ARM only. Installed smoke requires an ARM device. [Browser preview](references/preview-10.5-compact-layout.jpg).

22 November follow-up. Category icons are 20 pt with 10 pt top and bottom padding. The saved merchant directory includes 174 technology locations from seven retailers and the earlier grocery update. Next release steps are ARM packaging, API rollout and data import, then physical-device acceptance. [Source counts and decisions](CODEX_HANDOFF.md).

The saved directory now also includes 724 stations from the six requested fuel chains. The source counts and locality exclusions are in the [handoff](CODEX_HANDOFF.md).

The owner approved the left fuel toolbar preview. Обнови is anchored at the right edge and Дизел moves up when it fits. [Browser preview](references/alpha-preview10.6-fuel-toolbar.png).

The market-scale logo is configured for the launcher and in-app header. [Visual preview](references/scale-logo-app-preview.png).

The owner confirmed the existing 10.6 APK installs. The follow-up candidate combines 8 pt tab padding, the approved responsive fuel toolbar, and the market-scale launcher and header logo. The location field is slightly narrower and highlighted. The Preview 010.7 ARM build passed. Physical-device installation is pending. [Android run](https://github.com/Per5on/spestoslav/actions/runs/45062475962). [Candidate preview](references/candidate-location-preview.png).

## Verified baseline — Pre-alpha 010

**Internal 010 build successful. Live testing pending.** [Run 44923545071](https://github.com/Per5on/spestoslav/actions/runs/44923545071) at `2d19a0c984215cd052e6e7ad341c5aa938605592` passed Android 10 emulator smoke, ARM phone APK verification, and test-signed AAB validation. App version 0.5.3 and Android version code 10. Physical-device and live API/data acceptance remain open. Next work is product-matched Food/Technology WebPs and itemized merchant basket comparison. See the [handoff and proposed layout](CODEX_HANDOFF.md) and [TODO](PREVIEW_006_BACKLOG.md).

## Baseline — Pre-alpha 009

Added «Изтрий данни» with offline guest reset and authenticated cloud erasure. The owner authorized the internal APKs and AAB. The source, backend and browser checks passed, and the Android workflow runs the installed emulator APK before packaging the ARM APK and test-signed AAB. The daily summary and live-data limits are in the handoff.

Added and verified the «Облик» preferences locally. The dedicated Neon thumbnail database is seeded and checked, and the API-to-database path passed in the local dry test. Render linkage and the live Brevo inbox test remain pending.

Local branch `codex/pre-alpha-009` is based on verified Preview008. The candidate shows bundled sample photos by default with a persistent off switch. The feedback form reached a local authenticated TLS SMTP receiver through the actual API. Live inbox delivery awaits a verified Brevo sender and Render secret. Local evidence and the next device checks are in the handoff.

## Preview008 and follow-up

Locality search ordering is ready for backend review and deployment. Prefix matches appear first, with alphabetical ordering within both result groups. The app currently has no associated website or web deletion link.

Preview008 passed Android 10 smoke and ARM packaging on run 44309388382. The verified internal APK is 43,321,725 bytes, 42.7% smaller than Preview007. Production AAB signing, real account/receipt acceptance, and physical ARM checks remain open.

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
