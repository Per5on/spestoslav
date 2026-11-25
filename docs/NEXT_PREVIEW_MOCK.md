# Next Android preview mock · 24 November 2026

The local Chromium mock used a 390 × 844 viewport and a fixture API with synthetic prices and accounts. The APK remains pending approval. These timings measure browser behavior on the workspace. Android startup, mobile-network latency and a cold start of the hosted API require separate measurement.

## Fuel cold start

The cold trials started with a saved Sofia selection and empty catalogue and price caches. Each trial selected „Горива“ as soon as its tab appeared. Timing stopped at the first displayed A95 price of 1.45 €/L. Each row summarizes five trials. Added delay applies independently to the fuel requests.

| Scenario | Median from tab selection | Median from navigation | Tab trials under 200 ms |
| --- | ---: | ---: | ---: |
| Cold, loopback API | 83 ms | 627 ms | 5/5 |
| Cold, 100 ms added per fuel request | 159 ms | 716 ms | 5/5 |
| Cold, 300 ms added per fuel request | 359 ms | 847 ms | 0/5 |
| Saved prices, API unavailable | 19 ms | 241 ms | 5/5 |

At 300 ms of added delay, cold tab selection took 352–382 ms. All cold navigation trials exceeded 200 ms. In the slow test, the app displayed „Проверени цени за това гориво още не са налични.“ while the requests were still running, then displayed the price. Switching to Пловдив removed the Sofia price. [While loading](references/next-preview-mock-fuel-pending.png) · [Price loaded](references/next-preview-mock-fuel-prices.png)

Changing the initial batch from 10 to 15 or 20 at 100 ms of added delay gave median tab times of 156, 159 and 154 ms respectively. Keep 15 for the next comparison. The 5 ms spread is smaller than the variation between trials. A separate fast-scroll check mounted further grocery rows for all three values, and a saved 100-item basket initially mounted 10, 15 or 20 rows as configured. Native memory, image requests and frame timing are still open.

The next timing pass should separate app initialization from the first eligible price response. Inspect whether the grade, local station groups and prices can be returned together in a small locality-and-grade response. Measure that path on an ARM phone and give the pending state its own message. The slow mock needed the product, store and price requests to resolve, so a smaller render batch alone has little leverage on this scenario.

## Feature checks

The original direct-add mock below was superseded by the [product search follow-up](#product-search-follow-up).

| Item | Mock result and performance impact |
| --- | --- |
| „Обнови цени“ | Passed in „Храни“ and „Техника“. Catalogue controls fit standard and narrow widths in all six languages. The label adds no requests. „Горива“ retains Android pull-to-refresh, which still needs handset verification. |
| Lazy lists | Virtualization covers groceries, technology, fuel and basket. The mock rendered more grocery rows as the user scrolled, and the seeded basket respected the initial batch. Catalogue payloads were unchanged. Android scheduling of the background sync needs device verification. The catalogue sync checks passed locally. |
| Add from search | Added directly in both product tabs. The checkbox continues to control filtering. Two presses on one result produced quantity two, clearing filters preserved the basket, and a full 100-product basket blocked a new item. Four grocery click-to-local-save observations ranged from 64 to 101 ms, with zero write requests. |
| Repeated sign-in | Mocked a protected read returning 401. The app requested one provider refresh and retried the read. The retry returned 200 and kept the user signed in. A separate refresh 401 returned the user to sign-in. The reported device case remains open. Renewal adds network traffic when needed. |
| Password hashing | Managed Neon Auth handles hashing. Better Auth documents scrypt as its default, and the branch exposes no custom hash setting. The mock provider did not measure hashing or inspect stored hashes. |
| Document camera | The browser prototype opens in document mode, previews two selected receipt sections, falls back to one photo when the scanner is unavailable, and rejects an extra page and a 25-megapixel image. Android camera launch, automatic edges and multipage processing need native implementation and verification. The existing single-photo upload and Bulgarian OCR passed separately. |
| Receipt QR | Decoded a synthetic Bulgarian fiscal QR locally into fiscal ID, receipt number, date, time and total. A QR with an invalid date cleared the extracted fields. Currency and item rows still require the receipt image or another supported receipt source. The prototype runs on demand and made no upload. |

[Add from search preview](references/next-preview-mock-search.png) · [Receipt and QR preview](references/next-preview-mock-receipt.png) · [Password hashing reference](https://better-auth.com/docs/reference/security) · [Backlog](PREVIEW_006_BACKLOG.md#next-preview-preparation)

Strict TypeScript and the mobile test suite passed. The browser regression suite also passed itemized basket comparison, camera and image decoding of a synthetic EAN-13, manual entry after camera denial, receipt upload, Bulgarian OCR, review and deletion.

## Product search follow-up

„Приложи“, „Изчисти“ and the search selection checkboxes were removed along with their selection state, handlers and translations. In „Храни“ and „Техника“, the whole suggestion row adds one unit to the local basket. Enter opens the virtualized results list across the active tab's product groups. Clearing the input restores the catalogue. [Tap to add](references/next-preview-search-tap-to-add.png) · [Results after Enter](references/next-preview-search-enter-results.png)

At 320 px, the „вино“ test started from the dairy group, opened all 154 fixture matches on Enter and reached every match by scrolling. The list initially mounted 15 cards. A query with zero matches showed the empty state, and deleting it restored the catalogue. The six-language toolbar, catalogue and receipt workflow regressions, strict TypeScript and mobile tests passed.

| Action | Previous median | Revised median | Difference |
| --- | ---: | ---: | ---: |
| „Храни“ add to local basket | 13.05 ms | 12.25 ms | −0.80 ms |
| „Техника“ add to local basket | 12.90 ms | 11.60 ms | −1.30 ms |
| „Храни“ show matching list | 6.50 ms | 5.95 ms | −0.55 ms |
| „Техника“ show matching list | 6.40 ms | 6.90 ms | +0.50 ms |

Twelve warmed Chromium trials per action, per tab and per version used the same fixture catalogues and viewport. The timer started at the click or Enter event and stopped when the basket update reached local storage or the matching card appeared in the DOM. The previous version used the separate cart icon or „Приложи“, respectively. Differences of 0.50–1.30 ms are within run-to-run variation. Neither version made a network write in the timing run. These are browser interaction times. Android keyboard and device timing remain pending.

## Preview 10.9.1 fuel and thumbnail checks

The candidate requests fuel grades, local stations, verified prices and indicative chain offers in one locality-scoped response. Existing per-category caches stay readable. Older servers use the four original reads. The delayed browser check saw a loading indicator before the price and verified the old endpoint fallback and removal of the Sofia price after switching to Пловдив.

| Delay per request | Previous tab-to-price median | Candidate tab-to-price median | Candidate navigation-to-price median |
| --- | ---: | ---: | ---: |
| Local fixture | 83 ms | 78 ms | 392 ms |
| 100 ms | 159 ms | 137 ms | 392 ms |
| 300 ms | 359 ms | 334 ms | 595 ms |

Each candidate row has five cold browser runs. The previous medians are from the earlier mock and may include normal workspace variation. With the updated API, the test observed one fuel request per cold load. The 200 ms target was reached from tab selection under the 100 ms profile. The 300 ms profile and full browser navigation stayed above it. A handset and deployed server still need measurement.

Thumbnail checks exercised all 2,000 fixture products and the named regressions. The candidate uses neutral placeholders for 381 grocery and 134 technology entries where the resolver cannot confidently assign a type. The active bundle has 49 distinct WebPs totalling 103,624 bytes, an increase of 41,718 bytes over preview 10.8.1. The new digest comparison avoids downloading identical bundled and hosted WebPs. The external product photo URLs are already pinned to a repository commit. Live route delivery and finished APK size remain open.
