# Preview 10.9.1-hybrid

26 November 2026 · build 018 · app 0.5.11 · branch `preview-10.9.1-hybrid`

The comparison build uses `bg.spestoslav.preview.hybrid` so it can coexist with 10.9.1. Android separates each app's local session, basket, theme and catalogue cache. Both clients use the same production API.

## Design and research

- Use a local Android-only Expo module, which Expo autolinks across generated projects. Load the module from the receipt screen. [Expo modules guidance](https://docs.expo.dev/modules/get-started/)
- Use ML Kit 16.0.0 with an Activity Result contract. Request one JPEG page to match the existing receipt API. Copy the result to private cache with a bounded stream and validate its JPEG bounds. Keep camera and gallery capture for failed scans and unavailable Play services. Scanner components can download on first use, and the SDK requires at least 1.7 GB RAM. [ML Kit document scanner](https://developers.google.com/ml-kit/vision/doc-scanner/android)
- Build separate signed ARM64 and ARMv7 APKs and verify the ABI of each. Use signed preview 10.9.1, build 017, at 43,965,037 bytes as the size baseline. [Android ABI packaging guidance](https://developer.android.com/build/configure-apk-splits)
- Defer the optional remote thumbnail manifest until saved state is restored and JavaScript reaches an idle period. Use the bundled artwork immediately. Measure first display, first usable screen, first cached price and first fresh price separately. Compare frame timing, memory, scanner launch time and receipt retakes on the same ARM phone. [Android startup measurements](https://developer.android.com/topic/performance/vitals/launch-time)

The staging backend fixture exercises the new fuel path. The production rollout remains separate. The pilot uses the current receipt API and OCR worker.

## Retailer price wording

All six languages use availability wording for products and fuel without a current price. Product cards show published online prices without a source-type label, regardless of the selected town. Basket comparison uses the same prices and includes only retailers with an active local branch. Each eligible retailer appears once. Fuel keeps branch counts and the existing station-price path. Sample products are identified as outside the comparison.

## 26 November — pricing and approval checkpoint

The working tree on `preview-10.9.1-hybrid` includes updated product search, scoped price comparison, a cache-first offer fetch and changes to the price publisher. A suggestion selects exactly one catalogue product. Enter submits the full query. Retailer-published prices for groceries and technology form one nationwide feed. A chain's branch presence in the selected locality determines comparison eligibility. Each eligible chain keeps its published amount across localities, with one quote per chain. A single note under the comparison explains that prices are indicative.

The grocery and technology client reads previously saved, still-valid offers before a network reply. It checks the first time it opens in a new window and at the 06:00 and 18:00 Sofia boundaries while active. The existing Android background task can check in the background when the OS schedules it. Reopening or manually refreshing inside a window uses the saved price snapshot. The source publisher has a separate four-hour cadence so the API can replenish offers before they expire. The public default branch currently lacks that publication workflow.

### Publication and coverage

| Category | Public offers returned at the release check | Inputs verified in the isolated publication exercise |
| --- | ---: | --- |
| Храни | 0 | Burlex branch observations only. A retailer-published online offer feed is still needed. |
| Техника | 0 | Five Techmart online offers |
| Горива | 0 | 17 KARAI chain estimates |

The public merchant directory returned 1,585 branches. This measures chain presence. The previous report described feed and eligibility gaps as missing city prices. For the same product and retailer, the online amount is identical wherever that chain is eligible. Any published offer from an eligible chain can appear in Пловдив, Велико Търново or another locality. Burlex's branch tables remain branch observations and are excluded from nationwide grocery offers. The earlier isolated run promoted 495 branch-derived amounts, which are excluded from this candidate. Broshura.bg bulk reuse and exact product matching remain open.

Public station price checks found zero branch prices in София, Пловдив and Велико Търново. The live combined fuel endpoint returned HTTP 404. The isolated publication replay produced zero duplicate writes.

A licensed Fuelo chain-price export can be supplied to the dry-run publisher with `--fuelo-feed`. The normalized JSON contains `observed_at` as an ISO timestamp, `currency` set to `EUR`, `unit` set to `L`, and a `prices` array of `retailer`, `fuel` and `price`. KARAI corroboration is recorded by exact chain and grade, keeps the Fuelo value on a mismatch or absent secondary, and fills gaps in the Fuelo feed. This path passed a synthetic comparison and database check. Fuelo live reuse and access remain open. Existing station-price reads and ordering are preserved. [Fuelo terms](https://bg.fuelo.net/about/privacy?lang=bg)

### Verification and timing

The 159 backend tests passed with disposable PostgreSQL. Strict TypeScript, mobile unit tests, Ruff, Expo dependency checks, scanner autolinking, Android JavaScript export and seven browser fixture suites passed. The browser workflow exercised catalogue search, locality-restricted basket pricing, camera decoding of a synthetic EAN-13, receipt upload, Bulgarian OCR and sign-in session renewal.

Paired Chromium tests used the existing Expo baseline at `6673ead` and the hybrid preview, with five cold trials per network condition. The entries are medians in milliseconds.

| Scenario | Baseline, from fuel tab | Hybrid, from fuel tab | Baseline, from navigation | Hybrid, from navigation |
| --- | ---: | ---: | ---: | ---: |
| Loopback | 68 | 61 | 295 | 283 |
| 100 ms added per request | 133 | 133 | 360 | 350 |
| 300 ms added per request | 336 | 338 | 565 | 562 |

The fuel tab reached its 200 ms target at 100 ms of injected network delay. Cold navigation did not. The older API fallback was sampled once, at 161 ms from the tab in the baseline and 179 ms in the hybrid, so its performance needs more trials. These browser timings do not exercise the Android Kotlin module.

Before a commit, confirm the checks and get explicit owner approval. Recurring price publication then needs to be enabled on the default branch with the approved categories and dedicated publisher configuration, and checked against the public endpoints through an expiry and renewal cycle. APK packaging requires its own explicit approval once the candidate is ready. The installed ARM comparison still needs same-device Kotlin and existing scanner latency, failure rate, startup and package-size measurements. Browser timing cannot measure Kotlin.

### Retailer publication recovery

T MARKET's online shop publishes structured EUR offers. The collector uses two reviewed catalogue-to-SKU mappings for Сладея and Клио sugar. It reads each public page without carrying a selected store across requests, checks the exact SKU, title, offer URL and currency, and skips unavailable items. The administrative offer API now accepts the official `tmarketonline.bg` storefront for the registered `t_market` retailer. Unrelated hosts and other retailers cannot use that exception. [T MARKET's storefront confirmation](https://tmarket.bg/page/uvedomlenie-za-poveritelnost) · [Сладея](https://tmarketonline.bg/product/zahar-sladeya-1kg) · [Клио](https://tmarketonline.bg/product/zahar-klio-1-kg)

The price publication workflow now reports missing configuration explicitly and reads back the exact newly published grocery and technology offers from the configured public API. It needs the approved category list in `PRICE_REUSE_APPROVED_CATEGORIES` and an insert-scoped database secret in `PRICE_PUBLISH_DATABASE_URL`. `PRICE_PUBLIC_API` defaults to the current API host. GitHub's production default branch currently contains source monitoring without the publication workflow. The integration returned HTTP 403 for GitHub Actions variable and secret metadata, so stored production settings remain unverified.

A disposable PostgreSQL database with a restricted publisher role and separate FastAPI reader verified two T MARKET online offers (€1.32 each), five Techmart offers and 17 KARAI fuel writes from live sources. A replay inserted zero rows. The public readback check matched all seven online product amounts and observation times. The test directory gave София and Пловдив identical T MARKET quotes and excluded that chain in Мадан. The production API still returned zero grocery and technology offers.

The monitoring and publication paths now consume direct online grocery offers instead of the redundant branch-only checks. The standalone branch collector remains available. The mobile app retries an empty offer cache after ten minutes or on manual refresh. Valid populated caches follow the existing 06:00 and 18:00 schedule. Source-commit approval and production activation are the next checkpoints. APK packaging requires separate explicit approval.

### 27 November — two-retailer comparison and production rollout

The scheduled publisher now includes reviewed offers from T MARKET and BulMag for София Мел Екстра 1 kg, plus Techmart and Ardes for the black Xiaomi Redmi A7 Pro 4/64 GB (GTIN 6932554493271). The exact product, current offer and EUR currency are verified before publication. The directory change adds the official BulMag Grand Mall location in Варна. [T MARKET flour](https://tmarketonline.bg/product/brashno-sofiya-mel-ekstra-1-kg) · [BulMag flour](https://bulmag.org/product/brashno-ekstra-sofiya-mel-1kg) · [BulMag directory](https://bulmag.org/magazini) · [Techmart phone](https://techmart.bg/smartfon-xiaomi-redmi-a7-pro-464gb-black) · [Ardes phone](https://ardes.bg/product/xiaomi-redmi-a7-pro-4gb-64gb-black-mzb0n5ueu-529552)

The local pipeline read back four grocery offers and six technology offers collected from retailer pages. For Варна, the flour returned €1.15 at T MARKET and €1.23 at BulMag. The phone returned €114.99 at Techmart and €158.99 at Ardes. The locality-scoped API returned the same values as the nationwide feed. The earlier fuel run published 17 estimates. On 27 November, KARAI returned a source date of 26 November paired with a 27 November fetch timestamp. The validator rejected that inconsistent snapshot.

A clean Expo web export with simulation disabled rendered both comparisons against the isolated API. Product cards showed a published price before the basket was opened. The app displayed both eligible merchants and amounts in Варна. The API replay inserted zero duplicate observations and excluded an unavailable chain in Мадан. The local browser verifier now clears Metro's cache before switching API and simulation settings.

The production comparison check is read-only and the publication job runs it after database and exact-offer verification. It checks that at least two distinct retailers with branches in the same locality have live online offers for the same product, then reads the locality-scoped result back from the API. It fails when either category lacks comparison coverage. The 27 November run against production found zero offers and zero comparable products in both categories. The deployed readiness endpoint responded successfully. GitHub's default branch still lacks the recurring publisher.

After source approval, roll out the publisher and the additive BulMag inventory on the shared production schema. The retailer seed is `scripts/migrations/seed_bulmag_retailer.sql` and the branch import can be generated with `python scripts/prepare_local_inventory.py --all-reviewed --category groceries --retailer bulmag`. Verify the restricted publisher connection and category settings before dispatch. Run the workflow and inspect the saved comparison report, then verify an additional scheduled cycle. APK packaging requires its own approval.

### 27 November — hosted configuration and grocery grouping

The approved source was committed as `e1d0d9e`. The production-only pull request passed both backend CI versions. Its read-only GitHub Actions test confirmed the publisher database secret and the approved category settings are both unavailable to the job. The current GitHub connection cannot manage repository Actions settings. The necessary settings are `PRICE_PUBLISH_DATABASE_URL` and `PRICE_REUSE_APPROVED_CATEGORIES`. [Production PR](https://github.com/Per5on/spestoslav/pull/28) · [Hosted preflight](https://github.com/Per5on/spestoslav/actions/runs/45954276176)

The grocery grouping candidate uses distinct retailers with current online offers to decide whether a variant keeps its exact name. It groups variants sold by up to two chains when the family and package are identifiable. It retains independent units, quantities and egg sizes, and keeps the original names and product codes searchable. A grouped comparison uses the lowest published eligible price per retailer. Original product identities are available for scanning and receipt matching.

A browser run against live retailer data in an isolated API displayed the flour as a grouped item and verified the original comparison amounts of €1.15 and €1.23 in Варна. Technology still showed €114.99 and €158.99 for the exact handset variant. These working-tree grouping changes await their source checkpoint. APK approval remains separate.

### 27 November — production pilot restored and third-party review

The public API responded with HTTP 200 and zero fresh offers before the check. The existing Neon connection confirmed the same database had zero active offers and that the reviewed store locality maps to one canonical Варна row. Using the owner-approved production rollout, one transaction applied the additive BulMag retailer and Grand Mall branch seed and imported four fresh grocery and six fresh technology offers. A transaction guard checked the counts and reviewed branch before commit. The public API independently returned all ten published amounts and timestamps. The same-product comparison check passed for groceries in Варна and technology in three localities. The earliest published expiry is 21:00 Sofia time on 27 November. GitHub Actions configuration remains unavailable, so a scheduled renewal is still pending.

Third-party candidates reviewed:

- Broshura.bg republishes T MARKET retailer brochures, including issues valid through 30 November. The publisher's terms restrict systematic reuse. The retailer, validity dates and product pack need exact matching, and the brochure issue can differ by store or area. [T MARKET brochure](https://www.broshura.bg/cc/80630-t-market-%D0%B1%D1%80%D0%BE%D1%88%D1%83%D1%80%D0%B8/cherven-bryag) · [Broshura terms](https://s3-eu-west-1.amazonaws.com/public-legal-docs.offerista/offerista-bg/en/tou.html)
- Pazaruvaj accepts merchant catalogue feeds. Its indexed Ardes offer for the exact black Xiaomi MZB0N5UEU was €104.99 in the older copy, and the verified retailer page supplied €158.99 in the current run. Use a current authorized feed with offer-level model identity and source time for automated publication. [Pazaruvaj sample](https://www.pazaruvaj.com/mobilni-telefoni-gsm-c3277/xiaomi/redmi-a7-pro-64gb-4gb-ram-dual-p1317945004/) · [Ardes product](https://ardes.bg/product/xiaomi-redmi-a7-pro-4gb-64gb-black-mzb0n5ueu-529552)
- Колкострува distributes open downloads with retailer-submitted store-level values. Those files can be used as branch evidence and remain separate from nationwide online offers. [Official open data](https://kolkostruva.bg/opendata)
