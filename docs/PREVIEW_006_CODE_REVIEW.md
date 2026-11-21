# Preview 006 three-area code review — 2026-11-16

Scope: PR #13, branch `codex/preview-006`, observed head `1b79109c0433d69e5e7eef02b1c28e38b81e9f5f`. Source inspection and read-only Neon database checks; this is **not** a full penetration test, production performance benchmark or feature acceptance.

## Backend / data reviewer

1. **HIGH — product image pipeline has no shared data.** Read-only SQL on Neon shared preview branch `br-snowy-morning-baym8iw6` returned **0 `product_images`** for 1,000 products. `backend/app/catalog_api.py` provides `PUT /admin/products/{product_id}/image` but this does not seed or guarantee delivery. Verify `backend/app/main.py` product serialization, import source rights and real image URLs. Acceptance: licensed/authorized HTTPS thumbnails for representative products, reachable from Android and fallback where absent.
2. **HIGH — fuel branch coverage insufficient.** Shared database contains **7 fuel retailers but only 2 active fuel branches**; grocery 14/134, technology 8/2. `backend/app/catalog_api.py` uses active branch/locality join for filtered retailers. Investigate source registry and verified branch imports before showing nationwide fuel availability. Never invent stations or prices.
3. **MEDIUM — locality SQL may not scale with broad substring search.** `backend/app/main.py:96-148` builds `LOWER(column) LIKE '%term%'` disjunctions, sorted and limited to 20. Normal B-tree indexes generally cannot accelerate leading-wildcard predicates. Measure `EXPLAIN (ANALYZE, BUFFERS)` on read-only representative queries; consider `pg_trgm` GIN indexes or suitable prefix/normalized search strategy, without making migrations before review. Include duplicate-name disambiguation, Bulgarian/Latin variants, and cold-start latency.
4. **MEDIUM — readiness is not data-completeness verification.** `backend/app/main.py:57-76` selects at most one row per model. Successful health/readiness and HTTP 200 do not prove meaningful fuel/image/store coverage. Add non-sensitive inventory count/coverage checks to release acceptance, not a public sensitive diagnostic endpoint.

## Frontend reviewer

5. **HIGH — stores empty when locality absent.** `mobile/src/catalog/useCatalog.ts:107-146` sets stores to [] and only fetches stores under `if (localityId)`. `mobile/App.tsx:616-645` asks for locality when none selected. Confirm expected no-location UX; allow retailer overview distinct from verified branch proximity, or make location requirement clear and persist correctly. Verify actual selected locality has matching branches.
6. **MEDIUM — 60-second API timeouts and serial catalog pagination.** `mobile/src/api.ts:9` and `mobile/src/location/LocationPicker.tsx:42` use 60-second abort timers; the picker clears results at every keystroke. `mobile/src/catalog/cache.ts:90-100` and `mobile/src/catalog/useCatalog.ts:7-20` fetch fallback pages serially. Benchmark, add bounded timeout with retry, keep prior suggestions while loading, use compact server snapshot or cursor/paginated rendering. Avoid unbounded parallel calls.
7. **MEDIUM — Settings design not implemented.** `mobile/App.tsx:743-805` still uses existing screen/choice components. Implement black text/white background, compact font-height icons and adaptive two-column options; preserve minimum 44dp touch target and six languages.
8. **MEDIUM — feedback form still pending.** `mobile/App.tsx:755-758` displays `feedbackPending`, not sender/email/message form. Implement server-side recipient configuration, input validation, rate limiting, provider integration and success/failure UX. Never expose `ivo77@duck.com` as editable recipient or claim delivery without provider evidence.

## Security / CI reviewer

9. **MEDIUM — verify session/receipt boundary with explicit adversarial tests.** `mobile/src/workflows/session.tsx` uses SecureStore and bearer token refresh; `backend/app/receipts.py` scopes private receipt access by current user and validates images. These are good safeguards, but test expired/invalid session, cross-user receipt reads, oversized/decompression-bomb uploads, and provider failures; no exploit has been confirmed.
10. **HIGH release gate (process) — green APK is not feature completion.** GitHub Android workflow run 43871397216 and backend 43871397184 passed at `1b79109c`; Android 10 smoke passed. Workflow `.github/workflows/android-preview.yml:111-150` intentionally skips publication for `codex/preview-006`. Preserve that guard until three full passes on final feature-complete SHA. Earlier failed emulator run 43869099618 is superseded for baseline CI, but image/data gaps and pending Settings/feedback work remain blockers.

## Recommended order and evidence

1. Confirm Render deployed SHA, live endpoint response counts, shared Neon branch and image rights/source coverage.
2. Fix backend fuel/retailer/branch/image availability, measure locality query plans and API latency.
3. Fix frontend no-locality state, image display, location loading/timeout, Settings layout and feedback.
4. Run static/unit/integration; functional live/staging UI and backend; native Android 10 smoke, all on **same final source SHA**. Capture CI links, count and latency before/after, screenshot and evidence of email provider acceptance. Do not merge/release until these pass.

**Review limitation:** This is a targeted source review of selected files, not exhaustive line-by-line review of every repository file. Findings describe demonstrated code paths/data counts or explicit tests to perform, not assumed runtime vulnerabilities.
