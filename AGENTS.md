# Ongoing BG Prices / Спестовник project

This is an active continuing project, not a new task at each date change.

At the start of a session:
1. Read `docs/PROJECT_STATUS.md` and the latest entries in `docs/ACTIVITY_LOG.md`.
2. Check the current branch, working tree and linked PR/build results.
3. Resume the listed open work within the user's current authorization. Read detailed handoffs or old conversation exports only when a specific missing detail requires them.

Before pausing, update the status and append verified actions, commit/build links, unresolved issues and the exact next action to the activity log. Keep status ACTIVE until the user closes the project. These files preserve continuity; they do not start a background coding process by themselves. Append continuing project communication, owner decisions, corrections, approvals, and user-facing results to `docs/PROJECT_COMMUNICATION.md`.

Tell the owner what is happening now and who owns the next action. After a status update, name the concrete next step, whether work continues or is waiting, and whether the owner needs to do anything. Report changes such as opening a pull request, merging to production, waiting for a scheduled job, or pausing on a blocker as they happen.

Follow `docs/FRONTEND_BRIEF.md` for confirmed design decisions. Latest direct user decisions override conflicting historical documents. Preserve original reference images and numbered previews/APKs; create a new sequence number for a changed released build. Never label demo data as real offers. Check exact-commit CI results before claiming success, and distinguish code, local tests, CI, deployed API and live data coverage.

Use the current FastAPI/Expo architecture. Do not rewrite it to match historical Kotlin/Spring discussions. Credentials stay server-side. Inventory, branch prices, online offers and pending receipt/OCR observations have separate meanings. No invented branches, prices, closure status, GPS/radius or OSM features.
