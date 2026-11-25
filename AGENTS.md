# Ongoing BG Prices / Спестовник project

This is an active continuing project, not a new task at each date change.

At the start of a session:
1. Read `docs/PROJECT_STATUS.md` and the latest entries in `docs/ACTIVITY_LOG.md`.
2. Check the current branch, working tree and linked PR/build results.
3. Resume the listed open work within the user's current authorization. Read detailed handoffs or old conversation exports only when a specific missing detail requires them.

Before pausing, update the status and append verified actions, commit/build links, unresolved issues and the exact next action to the activity log. Keep status ACTIVE until the user closes the project. These files preserve continuity; they do not start a background coding process by themselves. Append continuing project communication, owner decisions, corrections, approvals, and user-facing results to `docs/PROJECT_COMMUNICATION.md`.

Follow `docs/FRONTEND_BRIEF.md` for confirmed design decisions. Latest direct user decisions override conflicting historical documents. Preserve original reference images and numbered previews/APKs; create a new sequence number for a changed released build. Never label demo data as real offers. Check exact-commit CI results before claiming success, and distinguish code, local tests, CI, deployed API and live data coverage.

Use the current FastAPI/Expo architecture. Do not rewrite it to match historical Kotlin/Spring discussions. Credentials stay server-side. Inventory, branch prices, online offers and pending receipt/OCR observations have separate meanings. No invented branches, prices, closure status, GPS/radius or OSM features.

Own verification through the release checkpoint. Before a commit, inspect dependency and asset references, run the relevant automated checks and compare the changed behavior or measurable benefit against the baseline. Use the mobile verification workflow and local browser runner for app changes and the existing backend matrix for server changes. Follow up on failures and record any missing test environment with the result. Routine checks, dry compilation and evidence collection do not require owner review. A signed APK still follows the explicit approval already recorded for the candidate.
