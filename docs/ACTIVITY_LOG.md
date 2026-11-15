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

## 15 November 2026 — continuity and comprehensive cleanup (in progress)

- Owner requested that the project remain ongoing with persistent notes, then requested a beginning-to-current audit, fixes, unnecessary-code cleanup and readiness before giving the next feature step.
- Reviewed conversation/reference extracts, Issue #1, handoffs, current source/PR/build status. Added repository entry instructions and persistent checkpoint/log rather than relying on a process staying open overnight.
- Downloaded preserved preview 001 via GitHub connector after shell artifact host denied access; checksum matched. Inspected actual emulator screenshot. Prerelease asset upload failed with HTTP 401; publication remains unverified.
- Audit fixes in progress: unused/duplicate Python imports; bounded receipt queue locking; transliteration filtering; basket limit; redundant state/request work; outdated docs/actions; patched Python dependencies; compatible JS dependency fixes and guarded build-tool patches. Preserve 001; cleaned build becomes 002.
- Next: finish/verify corrections, commit/push PR #5, wait for exact-code CI and emulator results, append final evidence and mark audit ready. No new feature phase until owner's next instruction.
