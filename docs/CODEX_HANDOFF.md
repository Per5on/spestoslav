# BG Prices — Codex handoff (2026-11-14)

## Current continuation notes

Backend fixes, verification and rollout state are documented in [BACKEND_READINESS.md](BACKEND_READINESS.md). The latest user-confirmed visual brief is [FRONTEND_BRIEF.md](FRONTEND_BRIEF.md), based on `12.docx`, `app.docx` and the supplied artwork. Latest decisions: green header, orange selections, four category tabs, separate searchable location dropdown and the provided piggy-bank sample logo. Finish backend verification before frontend implementation. These current decisions supersede conflicting older visual notes; historical CI/deployment statements below remain snapshots.

Fuelo is approved as a third-party fuel source. API access is not yet available; the adapter remains disabled, and averages/unknown-certainty prices must not become verified station prices.

## Objective
Continue building the Bulgaria-only national retailer and physical branch inventory, supporting an Android 10+ grocery price comparison app. Android only (no iOS). Original architecture intent: Kotlin backend, PostgreSQL or MariaDB initially undecided; inspect actual repository before changing technology. Hybrid price collection: retailer automation, admin entries, user submissions. Cover grocery categories comprehensively and include large chains, regional franchises, independent stores and Моят магазин. Existing repository may differ from original design; do not rewrite it without approval.

## Authoritative systems
- GitHub: https://github.com/Per5on/spestoslav, default branch `main`.
- Seed: `data/store_branches_seed.csv`.
- Retailer/source registry: `data/retailer_source_registry.csv`.
- Neon existing project `bg-prices-preview`, project ID `long-resonance-77491878`, branch `preview`, branch ID `br-snowy-morning-baym8iw6`, PostgreSQL 16.
- Existing database tables include `catalog_retailers`, `store_branches`, `inhabited_localities`, `locality_postal_codes`, `products`, `product_categories`, `current_prices`, `price_observations`, `price_cache`, `promotions`, `receipt_scans`, `receipt_items`, `user_submissions`, `product_barcodes`, `flyway_schema_history`.
- GitHub commit `969a89b92d6913d1136a045b86bc7e6ea5821a28` was verified as a previous checkpoint. Subsequent commit `38717e5008d87daf7551ef4de6681de2856817a9` added EKO branches; always re-read HEAD.
- Prior successful backend CI: GitHub Actions run https://github.com/Per5on/spestoslav/actions/runs/43585441963, six pytest tests passing on older commit `2bfe968`; **not proof of current HEAD passing**. Last inspected latest commit had no status checks.

## Snapshot at handoff
- Seed CSV: **116** branch rows; no duplicate branch names in the last audit; **38** retailer source-registry entries.
- Neon preview `store_branches`: **116** records, **116** with `locality_id`, **12** distinct retailer codes.
- Counts by retailer: Burlex 75, BILLA 11, ProMarket 11, Klasiko 6, Fantastico 3, HIT Max 2, Lidl 2, EKO 2, Kaufland 1, METRO 1, Technomarket 1, Technopolis 1.
- Last work imported 75 Burlex, 6 Klasiko, 2 HIT Max, 2 EKO branches; their `source_id` values were made unique per branch because `store_branches` has a unique constraint on `(source,source_id)`. For these new rows, `source_id` uses the source directory URL plus a short branch-specific suffix; it is NOT a canonical retailer-issued branch ID. Preserve provenance in the CSV and improve the schema separately if needed.
- A retailer listed in the catalog does not mean its physical branches are inventoried.
- Existing localities: 5,291 rows; names are not globally unique. Match on `name_bg` **and** municipality **and** region; e.g. Bankya, Tervel, Gabrovo have same-name settlements elsewhere. The source dataset uses `OTHER` for locality `type`; do not infer city/village from that value. One settlement is recorded as `Долни чифлик` (lowercase ч), and the seed was normalized to match.
- Last known `store_branches` schema includes `retailer_code,retailer_name,branch_name,city,settlement,locality_type,municipality,region,address,latitude,longitude,active,source,source_id,locality_id,postal_code,last_seen_at`. `locality_type` accepts CITY/TOWN/VILLAGE/OTHER. `source_id` is varchar(100), so avoid oversized URLs/identifiers.
- All 116 branches were marked active in preview at last inspection. This is **not** independent proof that each store is currently open; perform closure reconciliation before presenting as fully verified current coverage.

## Source status and priority
1. Continue groceries: **Mini Mart** official locator https://mini-mart.bg/nameri-magazin-3/ ; **T MARKET** https://tmarketonline.bg/page/stores-t-market (requires store closure reconciliation); **CBA** official branch source still unresolved. Then `Моят магазин`, ABC Market, and other grocery chains/regional franchises. Avoid generating fake locations.
2. Fuel: EKO official https://www.eko.bg/self-service-terminal-instructions/karta-na-obektite/ (2 branches seeded; source directory has many more); Shell locator https://www.shell.bg/shell-service-stations/shell-station-locator.html ; LUKOIL, OMV, Petrol, Rompetrol, Insa Oil need verified branch locator sources.
3. Home/furniture: IKEA https://www.ikea.bg/stores ; Mr. Bricolage https://mr-bricolage.bg/stores ; Praktiker https://praktiker.bg/stores ; Мебели Виденов https://videnov.bg/stores ; Bauhaus, HomeMax, JYSK, Mondo, Практис need further verification.
4. Technology: JAR Computers https://www.jarcomputers.com/stores/ ; continue Technopolis, Technomarket, Ardes, Plasico, Plesio, Вали, Зора.
5. Burlex directory https://burlex.bg/магазини-бурлекс/ : 75 rows seeded, but retailer homepage says over 80 stores; registry explicitly flags completeness reconciliation. Klasiko six branches seeded from https://www.klasiko.bg/bg/info/i8/За-нас.html . HIT Max two seeded from https://www.hit-max.bg/elements/pages/our-stores/ .
These URLs are starting references from previous work, not guarantees of live accessibility or present-day completeness. Recheck each before ingest.

## Execution instructions for Codex
- Inspect repository tree, app/backend implementation, workflows, schema migrations, tests and seed formats first. Keep existing working functionality; Android preview should load sample products and thumbnails from a connected backend, no Plus tab, Bulgaria-only retailers, Android minimum 10.
- Work in small auditable batches. Prefer a feature branch and PR for code changes; do not overwrite unrelated edits. For data, ensure every branch has actual official-source evidence and a specific locality/address; avoid duplicates, invalid locality links and fabricated prices.
- Keep retailer registry distinct from branch inventory; retain source URLs, last verified date, closure status, and provenance. Prefer an explicit import script or migration with idempotent matching; do not rely on fragile name-only deduplication. Fix unique `source_id` semantics via tested migration if needed.
- Before importing, validate exact locality matches (name+municipality+region) and count mismatches. After importing, verify before/after counts, `locality_id` non-null, uniqueness, categories, and source traceability. Use preview DB, not production, unless separately authorized.
- Validate retailer page content against authoritative live sources, not search snippets alone. If ambiguous, mark pending instead of inventing. Distinguish current official directory listings from historical data.
- Run tests and inspect GitHub Actions on the **current** commit. No CI success claims from old runs. Avoid changes to UI/design unless required and approved.
- Report each batch: files/commits/PR, source URLs, new/updated/closed branches, DB counts, locality validation, CI status, blockers, next target.
- Start immediately with Mini Mart, T MARKET and CBA, then complete remaining grocery, fuel, home, technology inventories.

## Operational notes
A separate ChatGPT automation titled **Daily BG Prices inventory continuation** is enabled, beginning 2026-11-15 at approximately 13:00 Europe/Sofia, recurring daily. This schedule is external to GitHub and does not itself start a Codex coding session. To launch Codex, open the repository in Codex and ask it to follow this file. The automation may continue the research/reporting independently if connectors remain accessible.
