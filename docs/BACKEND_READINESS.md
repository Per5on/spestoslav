# Backend readiness and frontend contract — 14 November 2026

> **Current checkpoint — 16 November:** deployed backend remains 0.5.0 / `538bd9a` until the 005 rollout is verified. Current source adds migration0007, catalogue/cache, native-session bridge and receipt improvements; local PostgreSQL/OCR tests pass but this is not evidence of deployment. The owner authorized building 005 after final checks. Follow PROJECT_STATUS.md for the live rollout state. Sections explicitly dated 14 November below are historical audit evidence, including the postal preparation later retired by0006.

This historical pass fixed the confirmed failures and adds the missing backend workflows described in the user-provided `app.docx`. At that historical checkpoint frontend implementation was subsequent; the later 003–005 frontend work is tracked in CHANGELOG.md. Current visual decisions and the unmodified reference assets are in `FRONTEND_BRIEF.md`.

## Confirmed fixes

- **Live locality lookup:** the deployed 0.3 service returned 500 because the preview lacked `inhabited_localities.postal_code`. An additive compatibility patch, tested on an isolated Neon branch first, restored `https://spestoslav-api.onrender.com/api/v1/localities?q=Sofia` to HTTP 200 with municipality, region and postal code. New code reads normalized postal links without depending on the legacy single-postal column.
- **Migrations:** repaired the syntax error in 0003 and removed runtime inspection from the fresh-install chain. PostgreSQL 16 upgrades, downgrades, re-upgrades, offline SQL generation and `alembic check` now succeed in disposable schemas. ORM indexes, types and review fields match the migrations.
- **Driver configuration:** standard `postgres://` and `postgresql://` URLs explicitly select psycopg v3. Tested under SQLAlchemy 2.0.44 and 2.1.8. Alembic uses the same normalization and preserves URL-encoded query parameters.
- **Visibility:** inactive products, retailers, branches and categories no longer expose current prices/promotions. Expired, future-dated and unverified records are excluded as appropriate.
- **Freshness:** `current_prices.observed_at` keeps observation time separate from review time. Approving an older observation preserves verified history but cannot replace a newer current price. Database upserts and row locks guard concurrent reviews.
- **Health:** `/health` remains liveness. `/ready` validates the API's actual database projections/tables and returns 503 for an unavailable/incompatible database; it is the appropriate deployment readiness check.

## Implemented API

Public reads:

| Route | Contract |
| --- | --- |
| `GET /api/v1/categories` | Active categories |
| `GET /api/v1/catalog` | Active categories/retailers, independent of published prices; optional `locality_id` and `category_code` |
| `GET /api/v1/localities?q=...` | Canonical BG/Latin/postal suggestions, municipality/region/postal links |
| `GET /api/v1/stores` | Registered active branches; select `locality_id` or `region`, optional `category_code`, bounded `limit`/`offset` |
| `GET /api/v1/products` | Active catalog, `q`, `category_code`, pagination, optional sourced `image_url` |
| `GET /api/v1/products/barcode/{barcode}` | Verified aliases/canonical product; 404 for unknown barcode |
| `GET /api/v1/prices/current` | Verified branch-level prices; product/branch/locality filters and pagination |
| `GET /api/v1/prices/history?product_id=...` | Verified branch observations, including historical/expired observations, explicitly scoped `BRANCH` |
| `GET /api/v1/promotions` | Verified offers within their validity windows |
| `GET /api/v1/national-offers` | Verified retailer-wide online offers, `price_scope=NATIONAL_ONLINE`, `branch_id=null`; never assigned to a physical store |
| `POST /api/v1/baskets/compare` | Stateless decimal arithmetic by branch, with optional separate online quotes; incomplete baskets have no total and cannot win; shipping/travel excluded |
| `GET /api/v1/demo/catalog` | Optional explicit demo photos; `is_demo=true`, `verified=false`, `price_eur=null`; does not seed real prices |

Authenticated user operations (Managed Neon Auth EdDSA JWT, issuer/signature/expiry/subject checked):

- `GET /api/v1/auth/config`, `GET /api/v1/auth/me`. Config is public; `/me` requires authentication. Sign-up, sign-in, session restoration and sign-out use Managed Auth, not a home-grown password database.
- `POST /api/v1/submissions/prices`: positive EUR amount, active matching product/branch/category, evidence and a future expiry. Supply an `Idempotency-Key` header. All entries start pending.
- `GET /api/v1/submissions`: owner-only history.
- `POST/GET /api/v1/product-identification-requests`: unknown-barcode requests, bounded valid GTINs, owner-scoped retrieval.
- `POST /api/v1/receipts`: private JPEG/PNG/WebP upload (8 MiB, pixel cap, bounded request stream); returns 202.
- `GET /api/v1/receipts/{id}`: owner-only status/text/unmatched candidate lines. Another user receives 404.
- `POST /api/v1/receipts/{scan}/items/{item}/submit-price`: owner-confirmed product/branch/unit price enters pending review with server-generated receipt provenance.

Administrator/collector operations:

- Admin product creation and sourced product-image updates; duplicate barcode protection and GTIN checksum validation. Fuel products may have no barcode.
- Admin identification queue/resolution creates a verified alias only after product confirmation.
- Admin submission queue and approve/reject transitions. Repeated moderation returns 409. Approval produces permanent history and a freshness-guarded current price.
- Admin receipt retrieval for reviewing extraction evidence.
- Admin national online offers require an official retailer evidence URL and explicit expiry. There is no fabricated branch.
- Admin collection-source registration enables an explicit origin/retailer match. Separate collector credentials can queue observations but cannot verify/publish them.

Admin access is a verified JWT subject in server-controlled `ADMIN_SUBJECTS`, or a separate 32+ character `X-Admin-Key`. Collection uses a distinct `X-Collector-Key`. Neither key belongs in Android or an `EXPO_PUBLIC_*` variable. Pending observations and receipt images are never public current-price data.

## Receipt processing

`python -m app.receipt_worker --once --max-jobs 10` claims jobs with PostgreSQL `FOR UPDATE SKIP LOCKED`, retries failures at most three times, reclaims stale leases and prevents a stale worker from overwriting a newer claim. Tesseract runs out of process with a timeout. OCR text and candidate totals retain low confidence; a user/admin maps product and branch explicitly before price review. Abbreviated descriptions, receipt dates and quantities still require human confirmation; there is no claim of reliable automatic full-receipt understanding.

Private S3-compatible storage is configured through standard AWS variables, SigV4 and path-style addressing. `RECEIPT_STORAGE_DIR` is explicit local/persistent-disk development mode; never use Render's ephemeral filesystem as durable storage.

The scheduled GitHub workflow installs Bulgarian OCR data and processes at most ten receipts every 15 minutes. It authenticates using GitHub OIDC with an exact audience, immutable repository/owner IDs, the approved workflow on `main`, the expected subject and GitHub-hosted schedule/manual-dispatch events. Forks, other branches/workflows and other repositories are rejected. The runner receives only a short-lived, run-bound job lease and one private image, then submits untrusted OCR text. Database/storage credentials and admin keys stay on Render; repository secrets are not required for OCR. `RECEIPT_WORKER_OIDC_ENABLED` on Render is the kill switch. No paid Render worker was introduced. A manual workflow dispatch is also available.

## Fuelo

User-approved source: https://bg.fuelo.net/prices/date/. Checked the live page, developer documentation, OpenAPI and terms. That page shows country/brand averages; region pages also expose locality navigation and regional averages. These are not physical-station observations.

Adapter: `backend/app/collectors/fuelo.py`; command: `scripts/collect_fuelo.py`. API definition checked at https://developers.fuelo.net/openapi.yaml. Station prices require an eligible Pro/Business key. The owner confirmed no API access yet, so integration remains disabled; no subscription or account was purchased/created.

The documented station response has **no reliable reported-versus-estimated flag**. Every observation is conservatively `AGGREGATOR_UNKNOWN`, pending review. Publishing it requires independent official retailer evidence; it is never relabeled as an official retailer feed. Wrong country/currency/station, stale/missing updates and mismatched units are rejected/skipped. API credentials are never put in query strings, redirects are not followed, pagination cannot leak a key to another host, and failures do not fall back to scraping. Source timestamps determine expiry rather than collection time.

`data/fuelo_station_mappings.json` is intentionally empty. Station-to-branch mappings require address plus canonical locality/municipality/region review, not city name alone. The adapter supports inventory retrieval for BG; administrative filtering is done after canonical mapping, not by inventing undocumented upstream region parameters. Website copying is not substituted for API authorization.

## Database paths and rollout

Fresh application databases use the independent Alembic chain through **0007** in the current, uncommitted branch. The shared Flyway preview does not run that baseline: it received the earlier additive `scripts/migrations/preview_backend_workflows.sql` and the tested Home/postal retirement SQL from `backend/migrations/sql/0006_remove_home_postal.sql`. Migration 0007 is currently applied **only to isolated validation**, not shared preview. Never replay a fresh Alembic/Flyway baseline on that database. No missing legacy V5/V6 scripts were invented. Existing branch inventory is preserved.

Neon project: `long-resonance-77491878`. Shared preview: `br-snowy-morning-baym8iw6`. Isolated validation branch: `br-autumn-breeze-baas5auz`. Managed Auth and a private receipts bucket were provisioned on the isolated branch and then prepared on shared preview.

Render target (owner-confirmed workspace): `tea-dbqur9jrjlhs73cga8eg`, service `srv-dbs313ei0phs73bvvd00` (`spestoslav-api`). The service is configured to auto-deploy `main`, but recent rollouts required explicit deploys when no automatic deploy was queued; backend code on a PR is not deployed merely because tests pass. The separate legacy `Per5on/testing` service was not changed.

Before publishing new routes: apply the additive script, configure the variables in `backend/.env.example`, verify readiness, and enable the approved OIDC receipt worker on Render. Keep `FUELO_COLLECTION_ENABLED` off until a key and reviewed mappings exist. An empty production catalog is not solved by inserting demonstration prices; real data enters through authenticated catalog/collection/review APIs. Demo product photos are isolated from all live price tables.

## Verification evidence and limits

- Standalone backend branch: **47 pytest cases pass**, including PostgreSQL 16 migration round trips, no model drift, real transactional approval/upsert, concurrent moderation, legacy missing-postal-column compatibility, active/expired filtering, JWT failures/role escalation, ownership, idempotency, OCR queue behavior, price freshness, national scope, product media, demo separation and basket completeness. The previous 59-test count included twelve inventory-PR tests; that work remains in its separate PR.
- Same 47 cases passed under SQLAlchemy 2.0.44 and 2.1.8. CI now runs both version families against PostgreSQL, rather than relying only on SQLite-created tables.
- Managed Auth on isolated Neon: signup, login, wrong-password rejection, session restoration, logout and JWT-protected API access exercised. Already-issued JWTs remain valid until expiry after logout; no immediate token revocation is claimed. Synthetic test accounts remain confined to that isolated branch.
- Private Neon S3: real upload/download, anonymous-read denial and test-object cleanup exercised.
- Real private S3 image upload → Tesseract → PostgreSQL review queue exercised using an explicit synthetic test receipt in local PostgreSQL, never inserted into shared preview.
- Shared live locality lookup returned 200 after the additive compatibility repair. Direct PostgreSQL TCP from this coding environment to Neon is blocked, so migration tests use local PostgreSQL and branch checks use Neon SQL tools.
- One upstream Starlette/httpx deprecation warning remains, unrelated to functional failures.
- Exact final-commit GitHub Actions and deployment links belong in the PR after they finish. Do not substitute historical green runs for current evidence.


## Rollout continuation

PR #3 was merged as `377d255da64f52944a94124b456404336036c504`; Render deployment `dep-dbs592m7bikc73ekqs30` became live and served API 0.4.0. Both merged-commit CI jobs logged 47 passing tests. Live readiness, localities/postal search, categories, catalog, region-filtered stores, demo product photos and authentication denial were verified. Live product/price tables remain unpopulated until source-backed data is supplied.

The GitHub connection cannot manage Actions secrets/variables (HTTP 403). The OCR continuation removes that dependency using documented GitHub workload identity; no forbidden secret-management API was bypassed. GitHub's current OIDC reference includes immutable subject IDs for repositories created after July 2026. Both documented subject formats are accepted only with exact immutable IDs and all other trust conditions. No secrets are returned by the worker API.

The continuation has 58 local tests passing, including PostgreSQL integration, signed worker-identity trust rejection, run-bound leases, duplicate completion, exhausted retries and runner request validation. Its exact CI/deployment/workflow outcomes are recorded in the associated PR after completion. Fuelo still needs owner-supplied API access.
