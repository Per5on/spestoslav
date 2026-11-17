# Inventory reconciliation — 2026-11-17

Related: [Issue #14](https://github.com/Per5on/spestoslav/issues/14), [PR #2](https://github.com/Per5on/spestoslav/pull/2), [PR #12](https://github.com/Per5on/spestoslav/pull/12).


## Current reconciliation and compatibility result

The owner authorized reconciliation and exact-commit CI, **not a shared Neon import, APK build or merge**. Work is isolated on PR #15; Preview006/007 UI work remains separate.

- Re-read preview139 records and linked canonical locality identities read-only on17November. Reproducible snapshot: `data/evidence/2026-11-17-preview-baseline.json`; row-level plan: `data/evidence/2026-11-17-reconciliation.json`; fresh official-source excerpts/hashes: `data/evidence/2026-11-17-official-recheck.json`.
- Resolved the main conflict by retaining all143 inventory records in main's current **13-column, no-postal** seed schema. Preserved both Fantastico region corrections, all9CBA records and current main's retired Home/postal decisions. No mobile code or APK workflow change relative to main; no Preview006 branch merged.
- All143seed records pass canonical locality/provenance/duplicate validation. Reconciliation: **138unchanged active matches;5insert candidates;1existing inactive record outside seed retained unchanged**. No updates, reactivations or deletions are proposed. Count subtraction alone would have suggested4, incorrectly.
- Five reviewed candidates: T MARKET Банско, ул. Пирин92в-г; T MARKET Тетевен, ул. Марин Темелски3; CBA Банско, ул. Глазне39; CBA Благоевград, ул. Катина и Николай Хайдукови27; CBA Благоевград, ул. Ал. Стамболийски30. Exact original spelling/source/date/identity in `data/batches/2026-11-17-reconciled-additions.csv` and the row-level plan.
- Mini Mart current public locator feed returned357records, not deduplicated national physical stores. All9retained seed addresses are represented. Feed IDs75and118 still duplicate Patriarch Evtimiy61; retain one branch. Hristo Botev75 remains absent from the current feed and present in the older official page; **retain its existing inactive UUID/source identity as pending, not confirmed closed**. No other Mini Mart closure inferred from feed changes.
- T MARKET official closure notice was retrievedHTTP200: four addresses closed5October2026. None appears in existing preview or seed, so no closure update is needed. Seven offered alternatives remain the existing seven unchanged branches; they are not seven proven one-to-one relocations.
- T MARKET official new-store article was retrievedHTTP200: Банско Пирин92в-г is a new store; Тетевен Марин Темелски3 is explicitly a relocation. The article does not identify the former address, and preview contains no T MARKET in Тетевен. Add only the verified new physical address; do not invent a former address or overwrite another branch. This is not a complete national closure audit.
- CBA official directory was retrievedHTTP200; all9address/name entries (including six named Bolero affiliates) are retained once under the existing CBA code. No duplicate normalized physical address in the full preview snapshot. Directory affiliation is evidence of listing, not a claim about legal ownership or guaranteed real-time operation; national affiliate reconciliation remains partial.

## Importer safeguards and local replay

`prepare_branch_batch.py` generates SQL only; it never connects. Default `--schema current` targets current Alembic columns; **the existing shared preview requires explicit `--schema legacy-preview`**, which preserves its required denormalized fields. Neither path restores postal storage or changes schemas. Historical reviewed22-row CSV was projected to the same13columns; all original inventory source IDs remain unchanged.

Batch loading rejects closed/pending rows and normalized duplicates (Unicode case, whitespace, punctuation and number marker); city+municipality+region must identify exactly one locality. SQL locks branch writes, refuses other-source physical matches, source identity collisions and inactive-row reactivation, and leaves existing rows untouched. Unknown address abbreviations or ambiguous identities require review rather than fuzzy merging. Lock/statement timeouts bound waits. The current schema lacks the legacy source-identity unique constraint, so its path checks under the same table lock rather than assuming that constraint exists.

Local disposable PostgreSQL tests exercise **both schemas**, inactive/collision refusal and late-error rollback. Full139-record snapshot replay plus reviewed5-row batch yields **144total/143active**, retains every original record byte-for-byte at selected columns, and a second run changes nothing. These are **local simulation results, not shared Neon counts**. Tests also cover closed/pending exclusion and normalized duplicate input. Final exact-head GitHub CI must pass before any import; report CI externally so the tested commit stays immutable.

Next import gate: after this PR's exact-head CI succeeds and the reviewed import is authorized, re-read live baseline/affected identities and canonical links, ensure no drift from this plan, capture a recovery/rollback plan, then execute only the5-row batch transaction on the explicit preview target. Verify expected net change, retained inactive history, unique source identities/locality links and second-run no-op. **No shared Neon writes have been performed in this work.**

## Original integration snapshot (before current-main reconciliation)
- Base: PR #2 `codex/verified-grocery-inventory` (140 rows, 14-column schema including `postal_code`).
- Add the three CBA rows unique to PR #12: Банско — БГ МАРКЕТ 13; Благоевград — МАРКЕТ 10; Благоевград — МАРКЕТ 2 Пазара.
- Final: **143 rows**, **9 CBA rows**, all **14 columns**, no duplicates by normalized retailer + city + municipality + region + address, and no blank addresses/source URLs.
- Normalize two Fantastico rows' region from `Софийска` to `София` to match the existing Neon locality reference.
- All **35 distinct** (city, municipality, region) combinations matched **exactly one** row in Neon `inhabited_localities`.
- The CBA source registry in PR #2 already contains `https://www.cba.bg/shops.php` with affiliate reconciliation flagged, so retain that more cautious status instead of replacing it with a blanket completeness claim.

## Direct source verification
The official CBA directory at https://www.cba.bg/shops.php lists:
- Банско, БГ МАРКЕТ 13, ул. Глазне №39
- Благоевград, МАРКЕТ 10, ул. Катина и Николай Хайдукови №27
- Благоевград, МАРКЕТ 2 – ПАЗАРА, ул. Ал. Стамболийски №30

## Preview database baseline
Neon `bg-prices-preview`, `preview` branch queried 2026-11-17: **139 rows, 139 locality-linked, 138 active, 15 retailer codes**; includes 6 CBA, 10 Mini Mart, 7 T MARKET. These three CBA addresses were not in the queried CBA rows. CSV has 143 rows but the preview DB already contains some inventory rows not in the CSV (e.g. one inactive Mini Mart). **Do not equate CSV minus DB counts with net-new insert count.**

## Import gate — pending
**No Neon writes were performed in this reconciliation branch.** Before import:
1. Inspect the PR #2 import logic, branch closure handling, T MARKET relocated stores, and the existing inactive Mini Mart. Preserve inactive historical rows and never reactivate them by default.
2. Confirm current official source listings for all affected rows, especially T MARKET closures/relocations and CBA affiliate status. Source directory listings are not by themselves proof of real-time open status.
3. Compare normalized address + retailer + locality and source identity against preview DB, including inactive rows; identify net-new vs updated vs retired records.
4. Ensure idempotent import with unique `(source,source_id)` and correct `locality_id`. Run import twice and verify second run creates zero rows.
5. Run tests/CI for the **integration PR head**, not just `main`; only merge after review. Keep Preview 006 frontend work separate.

## Known unrelated work
Open PR #9 (Preview 005), #11 (postpreview tests), #13 (Preview 006) should not be modified or merged as part of inventory reconciliation.
