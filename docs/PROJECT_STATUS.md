# Ongoing project checkpoint

Status: **ACTIVE — 005 final local checks complete; starting authorized Android CI build and preview rollout.**
Updated: 16 November 2026 (Europe/Sofia).

## Resume here

Read this file and only the newest ACTIVITY_LOG entry; do not reread the historical conversation. Branch:`codex/preview-005-grocery-workflows`, based on current main`c91f356` (README-only update fast-forwarded without a new commit). Source changes are still uncommitted at this checkpoint.

**Authorization:** the owner initially held commits/builds, then explicitly authorized building preview005 after all checks pass. Do not ask for the same confirmation again. Complete final checks, commit/review through a PR, run native CI and inspect actual artifacts before claiming delivery. Preserve001–004.

Completed in order:
1. Initial1,000 official Burlex grocery identities/six approved groups; catalogue metadata caching, complete pagination and word/unit search; camera/image/manual GTIN lookup and unknown-code review; managed session bridge; private receipt upload/OCR/confirmation/moderation/deletion; basket comparison; free-routing plan/mock.
2. [Issue#8](https://github.com/Per5on/spestoslav/issues/8): five-item overflow order, nested Settings, Feedback inside About and direct About with native version metadata and exact Vimp notice. No Profile section. Feedback submission channel remains unconfigured, explicitly stated in UI.
3. Header15→10 padding, “Техника”, shared stores/products/refresh rows and five fuel choices. Equal first two buttons; Refresh text+0.5pt padding,44pt touch height.
4. Preview004 audit and both supplied cleanup patches (identical). See CODE_REVIEW_004_2026-11-16.md. `cheapest: unknown` retained on the owner's correction.

## Verification and next action

- **79 backend tests pass locally under SQLAlchemy2.0.44 and2.1.8**, including real PostgreSQL16 migration cycles/model checks, whole-file SQL execution, repeated ORM/SQL catalogue imports and actual Bulgarian Tesseract OCR.
- TypeScript, model/search/GTIN/cache/dependency-patch/preview-metadata tests pass; inventory validation116 source branches/29 registry entries/5,291 localities, no duplicates/unmatched localities. npm audit has no moderate/high/critical findings; existing low Expo/deepmerge tooling finding has the reviewed backport/regression coverage.
- Reproducible browser scripts under`mobile/scripts/test-browser-*.py` pass workflow, menu/preferences and three-toolbar checks at320px/130% in six languages. Tests use the explicitly localhost-only scenario server. Real managed Auth was separately tested on isolated Neon (sign-up/sign-in/JWT/restore/sign-out).
- Browser proofs:`/workspace/work/preview005-final-workflows-01/`, `preview005-final-menu-01/`, `preview005-final-toolbars-01/`. Mock images:`/workspace/work/preview005-mock/`; scenario server8774 and development Metro8775. No fake data entered shared preview.
- **Next:** finish visual capture/native smoke preparation, commit once final checks are green, open PR and run005 native build. Verify actual Android camera permission/decoding, OS storage, image picker and About metadata. Then perform the authorized shared-preview/API rollout, verify live results and deliver APK/snapshot. No005 APK/PR/deployment exists yet in this checkpoint.

## Systems and data boundaries

- Repo`Per5on/spestoslav`; current stack React Native/Expo54/TypeScript + FastAPI/Python + Neon PostgreSQL + Render. Candidate metadata is`mobile/preview.json` (005,0.3.0/code5); workflow/app labels derive from it. `scripts/set_preview_version.py` derives registry/package fields without building.
- API`https://spestoslav-api.onrender.com`; last verified deployed0.5.0 at`538bd9a`, Render`dep-dbsppd8n74is73aimkc0`. Selected workspace **My Workspace**`tea-dbqur9jrjlhs73cga8eg`; service`srv-dbs313ei0phs73bvvd00`. Auto-deploy is configured but earlier pushes queued none; inspect before manually deploying. Do not deploy docs-only changes unnecessarily.
- Neon project`long-resonance-77491878`, DB`bgprices`, shared preview`br-snowy-morning-baym8iw6`. **0007 and the1,000 names are currently isolated only** on`br-ancient-shadow-balr2n5l`:6groups/1,000identities/5,291localities/139branches/0prices/0barcodes. Source-freeze JSON is versioned; retailer product codes are not GTINs. Existing shared remains unchanged by005. Use additive SQL, never fresh Alembic on Flyway history.
- Home/postal storage removal0006 is already live. All5,291 locality IDs and139 branches were retained;29 retailers remain. Recovery`br-frosty-star-badgjcyw`;003validation`br-crimson-feather-balgu231`. Do not rerun retirement/recreate postal data. Empty deprecated postal response field remains for unretired001/002 clients.
- Direct TCP to Neon is unavailable here; local PostgreSQL and connected SQL service are the verified paths. Task-owned credentials live outside git under`/workspace/work/`; never print or copy them into docs/app.

## Confirmed scope and limits

Green header/orange selections; money-bag logo; upper tabs Храни/Техника/Горива/Моят списък; name-only locality; no lower ribbon/Home/postal storage. Six languages and saved font/basket/locality. Saved-list key stays`spestovnik-preview-001`.

Keep the app free. Paid alerts/subscriptions deferred. Free real shop routing is planned, not enabled: mock uses a synthetic matrix; real origin/coordinates/provider/road costs still need work. Fuelo public extraction returned403 here; no API key exists, no station/average price is fabricated. Other retailer feeds, verified GTIN/price coverage and product images need further sourcing; the first1,000 records are not a balanced nationwide top1,000 claim. Demo photos remain clearly separate.

PR#2 inventory expansion is separate/open; do not silently merge it. Mini Mart/T MARKET/CBA official-source expansion and closure reconciliation remain inventory work, distinct from this feature batch. Existing Render HTTP health-check setting is not claimed changed.

## References

FRONTEND_BRIEF.md · CHANGELOG.md · MOCK_SCENARIOS_005.md · CODE_REVIEW_004_2026-11-16.md · decisions/migration-strategy.md. Original visual/doc references and numbered artifacts remain preserved. Historical full notes are archived; they are evidence, not newer instructions. This checkpoint preserves continuity, not an unattended coding process.
