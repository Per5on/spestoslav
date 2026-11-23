# Bug-fix build 015

Android preview label 10.9, app version 0.5.8. This is an internal ARM test build.

## Price refresh and coverage

- The daily source check produces reports. It cannot keep prices live by itself. The publication candidate checks approved categories every four hours. Burlex and Techmart retain their 12-hour expiry and KARAI its 24-hour source-age cutoff. An expired observation never becomes current merely because the job ran again.
- The cache stages observations with source, observation time, expiry, and branch or chain scope. Its `unexpired_observations` view is time-filtered. Catalogue and directory reference tables include names and sources for matching. The APK continues to request current prices from the API.
- The live fix added 51 already reviewed technology or fuel branches in Varna and Veliko Tarnovo. KARAI published 17 fresh chain offers. Live reads found five technology and 17 fuel offers in Varna and 17 fuel offers in Veliko Tarnovo. Grocery prices remain limited to the matched Sofia pilot. National offer prices remain indicative and require an active store in the selected locality.
- The app prioritizes priced products in normal catalogue browsing, respects the existing order for explicit searches, and revalidates prices when it resumes.
- The staging run captured 1,000 Burlex observations, five Techmart observations and 17 KARAI observations. The isolated PostgreSQL publication matched 875, five and 17, respectively. An identical replay wrote zero rows and recognized the already-current matches.
- Techmart's published terms restrict copying and distribution of site content. Burlex's site identifies its rights as reserved. Neither check established permission for unattended republication of the rates. KARAI's index credits CC BY 4.0. [Techmart terms](https://techmart.bg/obshti-usloviq) · [Burlex table](https://burlex.bg/kolkostruva/) · [KARAI](https://karai.bg/fuel-prices/indeks)

## Price cache and publication

Run the collector from the repository root. The default is a cache-only collection.

```sh
python scripts/refresh_live_prices.py --cache price-base.sqlite --catalogue-base
```

Optional SQL output is available with `--sql-dir`. The publication workflow needs to run from the default branch, with an explicit list of reuse-cleared categories in `PRICE_REUSE_APPROVED_CATEGORIES` and `PRICE_PUBLISH_DATABASE_URL` set to a dedicated price-publication database role. That role needs read access to the product, branch and retailer catalogue and the required inserts and current-price updates. It does not need account, receipt or database-owner privileges. Exercise it against isolated PostgreSQL before activation. The scheduled workflow is staged in this branch. It has not been activated.

## Account and search limits

| Operation | API limit |
| --- | --- |
| Sign in | 10 per email and 60 per client IP in 15 minutes |
| Request a reset code | 3 per email and 20 per client IP in 15 minutes |
| Verify a reset code | 5 per email and 30 per client IP in 15 minutes |
| Locality search | 120 per client IP per minute, 2–80 characters, at most 20 results |
| Product search | On-device text filtering, up to 80 characters, with no per-user quota |

These counters are in memory and apply within each backend process. They have no effect until that backend deploys. A limited API response includes `Retry-After`. Provider-side protections remain important for requests that bypass the app bridge. Keep sign-in and new passwords within the existing 8–128 character contract. The app sets no periodic password rotation. Reset codes have six digits. The managed provider controls actual code lifetime, code reuse and session revocation. Confirm these against the deployed provider and an authorized test inbox. The 15-minute attempt window is independent of reset-code expiry.

Expired pending submissions are shown as expired and omitted from the admin review queue. This status is derived on read and preserves the original record. The receipt-orphan sweep remains a separately tracked dry run.

`docs/12.docx` was removed from this build checkout. The older Git history preserves it.
