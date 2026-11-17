# Inventory reconciliation — 2026-11-17

Related: [Issue #14](https://github.com/Per5on/spestoslav/issues/14), [PR #2](https://github.com/Per5on/spestoslav/pull/2), [PR #12](https://github.com/Per5on/spestoslav/pull/12).

## Proposed integrated seed
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
