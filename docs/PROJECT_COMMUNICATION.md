# Спестовник project communication

This is the repository record of the project conversation available through 23 November 2026 in Europe/Sofia. The older thread was unavailable when the conversation resumed. Earlier decisions are reconstructed from the owner's visible messages and the saved handoff. Earlier assistant replies are represented by their documented results where the text of the reply is unavailable. Approval applies to the specific preview, change or build named in the conversation. [Handoff](CODEX_HANDOFF.md) · [Activity and verification log](ACTIVITY_LOG.md) · [Current status](PROJECT_STATUS.md)

## Resume from the handoff and prepare 010

- The owner could not find the previous conversation. They asked to read the handoff, then the TODO and `chatgpt/pre-alpha-009.1`, consolidate a single document, then inspect the hardening branch and report findings before implementation. The owner later directed us to continue from pre-alpha-009 with the handoff and exclude the chatgpt branch and hardening notes.
- The Android emulator action terminated with `adb` exit 255 after configuring and launching the AVD. The owner asked to rerun it with fixes, verify the checks and prepare pre-alpha_010. They then said “do not build yet.” They reserved approval for the 010 build commit until the implementation checks and dry run passed.
- Rename “Моят списък” to “Сравни цените”. Remove “Магазини” and “Продукти” from “Храни” and “Техника”. Put the light-green product search field immediately left of “Обнови”. Remove the captions “Група храни” and “Група продукти”. Use two rows of content-width group buttons and a final horizontal overflow. For “Техника”, the example was “Всички продукти”, “Телевизори и компютри” on row one, then “Умен дом”, “Малки уреди”, “Големи уреди” and overflow on row two.
- Unify the thumbnails across the app. Replace the old technology imagery with colourful, clean representations like groceries. In “Горива”, remove “Бензиностанции” and “Гориво” and align the narrower fuel field with “Обнови”. Add “Търговски обекти” to the vertical header menu, with merchants organised by category and locality and their existing physical addresses.
- Keep the default theme and add the specified palettes. The supplied pairs were `#b9ceac/#f2eee7`, `#f8c7fb/#c181f3`, `#022f40/#38aecc`, `#a29f61/#383615`, `#f7da83/#073368`, `#edede2/#ebbdd3`, `#1B263B/#FF7F50`, `#1B263B/#F4C7C3`, the repeated `#f8c7fb/#c181f3` and `#806380/#ffc6ff`.
- Put the tasks in the existing TODO. Work through the backend, frontend, obsolete code and dependencies, then run the three-way check and await build approval. The owner specifically requested thumbnail database, barcode scanner and receipt-storage checks.
- The owner approved the build commit after the findings were recorded. They requested a mock comparison across several products and merchants on “Сравни цените”, then said to wait for the build. They asked for evidence of code cleanup, dependency reduction, response time changes and removal of obsolete button code.
- The next change renamed “Облик” to “Тема” and removed the “Изображения” toggle. Keep thumbnails visible and use a small, accessible asset store. The owner approved the commit. Another emulator run failed with `adb` exit 255. The owner authorised investigation, then confirmed the build succeeded with the live device test still pending and asked for that result in the handoff.

## Preview 10.5

- Find missing recommended-size WebPs for “Храни” and “Техника” that closely represent the product. In the price comparison, show each selected product price and the total per merchant. The owner accepted the suggested visualisation and requested a sample.
- Match grocery group-button sizing to technology and use pop-ups for both horizontal overflow menus, following the vertical header menu pattern. The owner approved the ordering and visual design and requested removal of palettes 14, 17, 2, 3, 4, 5, 7, 8 and 10.
- Implement the TODO, itemised comparison and palette changes, rerun checks and report before building “preview-10.5”. Match the illustrative style of “прясно мляко”, “слънчогледово олио” and “захар” across both categories. Distinguish same-name products using a barcode or a clear product label, for example “банани” and “био банани”.
- Recheck “Търговски обекти”, which was failing to load. Make thumbnails zoomable on press if possible and use a representative photograph. The owner approved the commit with an explicit disclosure that images are illustrative, then approved the revised version.
- The release build failed while resolving `com.google.code.gson:gson:2.9.1` via the Foojay 0.5.0 dependency at Android `settings.gradle` line 21. The owner provided a further Expo Camera emulator log and noted recurring regressions. They authorised the fix.

## Alpha Preview 10.6 and Preview 010.7

- Drop Android x86_64 and record it in the development log. Place language, theme and font size in the left settings column, and terms, privacy and data deletion in the right. Move location above the categories. Shrink the header and make the app name clearly larger than the two-line slogan. Use correctly matched symbolic thumbnails without a background. The owner specifically reported banana thumbnails appearing on other items, including tomatoes.
- Keep a two-row fuel selector, with “бензин 95” and “бензин98+” preceding “Обнови” and remaining fuel types on row two. Provide a visual preview. Record that the concise introduction describing the app and features is to be written after final beta and before first release. Add the work to the TODO for the day.
- The owner rejected category tabs without the original icon-and-label arrangement. Restore both, then preview at 4 pt padding, followed by 10 pt. The owner asked for a visual preview, with no APK run. They settled on 20 pt icons and 10 pt padding and requested the decision in the handoff without another preview.
- Research official grocery locations for Kaufland, Lidl, BILLA, Fantastico, T MARKET and METRO and add them to “Търговски обекти”. The retailer links were supplied in the conversation. [Branch sources](../data/retailer_source_registry.csv)
- Add technology branches for Techmart, Зора, JAR Computers, Техномаркет, Ардес, Технополис and Vali. The owner supplied official retailer pages and 14 Techmart branch names. Add Rompetrol, Lukoil, Petrol, Shell, Eko and OMV stations using the supplied Fuelo brand pages. Record both in the handoff. [Saved branch inventory](../data/store_branches_seed.csv)
- Recheck the day's changes before the approved “alpha-preview10.6” commit build. The owner requested a visual preview and corrected the fuel layout. Anchor “Обнови” at the far right and add “Дизел” on the first row when space permits. Distribute the fuel labels across the row without crowding. The owner asked whether the physical stores and stations had been added and selected the left fuel-toolbar version for the commit. [Approved fuel toolbar](references/alpha-preview10.6-fuel-toolbar.png)
- Suggest a memorable purpose-fit name and logo. The owner asked for a Bulgarian cultural reference and found the two price tags with a check mark too generic. They requested more attractive colours, then an alternate eye-shaped symbol inside the шевица. They chose the preceding version, reviewed further proposals and approved the selected launcher and header artwork for that candidate.
- The owner confirmed 10.6 was installable. They requested 8 pt tab padding, the approved far-right “Обнови” arrangement missing from that APK, the new logo and all outstanding approved changes. They requested a summary before commit, then a slightly narrower, highlighted location field and a preview before approval. They approved and requested a code review and cleanup, then Preview 010.7 based on 10.6, and asked to resume where work stopped. [Preview 010.7 checks](PROJECT_STATUS.md)

## Next beta preparation

- Review the uploaded `cleanup.patch` and `bugfixes.patch` for applicability. The owner approved the cleanup, imports, shared helpers and Ruff. They requested a check of expired submissions and receipt orphan cleanup, adding successful work to the next commit tasks without executing the sweep.
- Restore the old logo and change the slogan to “Сравни и спести”. Increase its legibility and shrink the header. The owner clarified the restored logo belongs only to the Android launcher and reported seeing an unwanted header logo in the first correction. The corrected header was accepted.
- Shrink product and thumbnail fields by 2 pt and unify their representation style. The owner suggested Broshura and WebP for both catalogues. For the next beta, connect real price sources, keep comparison, search and cart locality-bound, and dry-test authenticated and guest workflows including scan, receipts and feedback. Add “Моят магазин” if still missing. The owner supplied its store locator and accepted either official retailer pages or Broshura for prices.
- Put “Основни храни и консерви” after “Всички храни” and move “Подправки и напитки” into overflow. The owner approved the overall visuals and refined “Храни” to two buttons on the first row and three on the second. They reported the old cached thumbnails, then accepted the photos. They corrected the footer position again. The original three notices were the illustrative-photo disclosure, store-load failure and saved catalogue status. Put the concise notice at the bottom and use 1.5 pt spacing between lines. Hide “данните и изпращането са симулирани” in the verified live beta.
- For the next beta fuel view, remove “Обнови”, use a single row of five fuels and show stations for the selected fuel. Remove product search and the basket from fuel. Retain search and basket for “Храни” and “Техника”.
- The owner requested a concrete status and any actions needed from them. Visual previews come before including changes in the APK commit. APK approval remains explicit and follows backend verification, code checks and dry testing. [Beta checklist](PREVIEW_006_BACKLOG.md)

## Live data and locality rule

- Initial live Sofia checks found zero current prices, technology branches and petrol stations. Both catalogues returned 1,000 records without image URLs. The owner asked to fix live availability using the existing sources.
- Owner clarification. “Even if there are no local prices, you can still use the main online publication prices. the important is to have a store in that local area - the prices are indicative”.
- The Sofia import was tested and replayed on an isolated Neon branch before applying it to the shared preview. The public API returned 34 technology branches from seven retailers and 113 stations from six chains. Seven licensed WebP links were confirmed across the two catalogues. The initial grocery source batch yielded 875 regular branch prices from Burlex in Банишора and Лозенец. Its public table declares the BGN-to-EUR conversion.
- The five exact Techmart offers were confirmed from official product structured data and tested against the public API. The deployed comparison route leaked them into Мадан, where the merchant had no listed branch. The pilot batch was immediately expired in the shared database. The separate backend change restricts both retrieval and comparison to active local stores and keeps itemised prices and totals with the quote scope intact.
- The owner said, “Keep all communication history in the repository as it reflects the project changes made.” Add incoming decisions, outgoing status, approvals, disagreements, reported failures and verification results here as work continues. Keep the concrete evidence and next action in the activity log. [Activity log](ACTIVITY_LOG.md)

- The backend-only fix passed both SQLAlchemy CI jobs and was merged and deployed to Render. The live Sofia check returned five Techmart offers and a two-item total of €303.99. The same comparison and offer listing returned no Techmart result for Мадан. The merchant directory now returns 285 active entries, including all 193 Sofia entries. A two-item grocery comparison produced complete local quotes from each Burlex address. [Backend PR and checks](https://github.com/Per5on/spestoslav/pull/22)
- Sofia also returned 17 published chain-level fuel prices, covering six chains and three of the five fuel choices. The app candidate keeps a station quote when available and labels chain values as “Ориентировъчна цена за веригата”. Petrol 98+ and Diesel+ have no feed values in this pilot. [KARAI source and licence](https://karai.bg/fuel-prices/indeks#metodologiya)
- The source refresh commands are recorded for repetition. There is no scheduled job yet. Coverage beyond the pilot and the remaining live workflow checks are beta acceptance tasks. No APK was built.
- The candidate was checked through a browser against the deployed API. The comparison and fuel previews show the live quote labels. The fuel selector keeps all five choices on one row at 320 px in every supported language. [Comparison](references/beta-live-sofia-comparison.png) · [Fuel](references/beta-live-sofia-fuel.png)

## Grouped fuel results

- The owner asked to show one indicative fuel price per chain, with a count such as “15 клона” or “8 клона”, and to show any different station price as an additional entry. The count covers the selected fuel and locality. A confirmed station price that differs from the estimate appears below it with its address.
- The web preview used the live Sofia inventory of 113 stations across six chains. EKO appeared once at €1.51/L for 27 branches. A test-only €1.49/L station price appeared with its address, reduced the estimate group to 26 branches, and disappeared when the selected fuel changed to diesel. [Grouped fuel preview](references/beta-live-sofia-fuel-grouped.png)
- The owner asked to continue the checks. After fixing the browser scanner's message for a denied camera stream, the full isolated workflow passed for barcode scanning, sign-in, receipt upload, Bulgarian OCR, review, deletion and manual barcode fallback. Live signed-in acceptance and feedback delivery remain open.

## Refresh and recovery requirements

- The owner specified automatic price checks twice per week for „Храни“ and daily for „Горива“. They asked for a forgotten-password option to regain sign-in access when changing devices, and said they would report the physical-device check.
- The audit confirmed that the deployed app has no reset entry point and the configured Neon Auth provider lists reset endpoints. The grocery pilot's 12-hour freshness window is shorter than the interval between checks. Scheduling, the display of price age and the live recovery flow remain open. [Beta checklist](PREVIEW_006_BACKLOG.md#backend-and-beta-acceptance)

## Daily checks and forgotten password

- The owner changed the cadence to daily for „Храни“, „Техника“ and „Горива“, asked for alternative sources that can become backups, and requested implementation and a visual preview of „Забравена парола“. The owner will specify the final checks after this work is confirmed.
- The daily checks and the official grocery archive probe passed locally. The workflow was added to the default branch and keeps reports for each category. The first hosted run passed. [Hosted checks](https://github.com/Per5on/spestoslav/actions/runs/45184089105) Techmart and Technopolis were matched by GTIN on one handset. The archive has distinct Sofia Burlex branches. Eco Petrol publishes its own chain prices, and station-level Fuelo needs eligible access and source mapping.
- Browser fixtures confirmed invalid and consumed password codes and successful sign-in with the new password. Live email delivery remains to be checked. [Sign-in](references/beta-forgot-password-sign-in.png) · [Email](references/beta-forgot-password-email.png) · [Code](references/beta-forgot-password-code.png)

## Public sources and app responsiveness

- The owner requested a public-portal audit, code cleanup and options to reduce database size and interaction delays. Confirmed the available sources and reviewed metadata and pricing identity. The shared database measured 15 MB, with small estimated bloat. Prioritized narrower requests, search indexing and measured device performance. [Audit](CODEX_HANDOFF.md#public-data-and-responsiveness-audit)
- The candidate's confirmed prices rendered while a secondary source was held. Indexed search matched the prior ordered results and was faster in desktop filtering measurements. Shared data and deployed behavior have not been changed by this candidate.

## Beta_10.8 data, build and changelog

- The owner requested the reviewed public-data import, a small batch of exact GTINs for live scanning, verification and the Beta_10.8 commit. They also requested a changelog of all versions after the build.
- Tested and replayed the import on a disposable branch. Applied six official locality mappings, four corroborated GTINs and 1,358 historical КЗП grocery observations to the shared database. Current prices and existing entities were preserved. [Handoff](CODEX_HANDOFF.md#beta_108-public-data-pilot) · [Changelog](../CHANGELOG.md)

- While Beta_10.8 was packaging, the owner requested „Трети страни“ inside „За приложението“ and asked that data and app credits move there. The normal catalogue and fuel views still show merchant names, price scope and the illustrative-image notice. The candidate includes grouped links to data, address, image and software sources. [Browser preview](references/beta-10.8-third-parties.png)

- Delivered Beta_10.8 build 014 with the new credits section and the changelog for all 14 recorded versions. The signed ARM test APK for source `cb8d736` passed Android CI for `arm64-v8a` and `armeabi-v7a`. Both hosted PostgreSQL jobs passed. Physical installation and camera scanning are pending. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45191123258/artifacts/14826956549) · [Android run](https://github.com/Per5on/spestoslav/actions/runs/45191123258) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45191136452) [Changelog](../CHANGELOG.md)

## Beta_10.8 follow-up review

- The owner asked whether the findings in `check_and_verify.docx` apply. Reviewed the document as assessment material and recorded applicable release work and corrections in the [activity log](ACTIVITY_LOG.md#23-november-2026--beta_108-document-review).

## Bug-fix build 015

- The owner confirmed that prices were not populating and authorized the bug-fix build. They asked for expiry, password policy, attempts and search limits to be reassessed, a cached database to be created from collected data, and `docs/12.docx` to be removed from the pack. [Build notes](BUG_FIX_015.md)

Delivered the build 015 pack with the APK, SQLite base and checksums. The four-hour price publisher and authentication safeguards remain staged. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45210084849/artifacts/14836831458) · [Android checks](https://github.com/Per5on/spestoslav/actions/runs/45210084849) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45210224790)


## Велико Търново device report

- The owner confirmed that build 015 installs and that the camera appears to work, and reported no visible prices in Велико Търново. Verified the local coverage gap and published 2,713 validated grocery branch prices from the Burlex public table. Technology coverage remains open. [Verification record](ACTIVITY_LOG.md)

- The owner confirmed that prices appeared after refreshing build 015 on their phone in Велико Търново.


## Nationwide directory validation

- The owner asked to finish the interrupted nationwide run after reporting widespread missing prices. Completed isolated import and duplicate-free replay of the 1,563 reviewed records. Recorded the remaining grocery price gap and live rollout status. [Evidence](ACTIVITY_LOG.md#23-november-2026--nationwide-directory-validation)


## Nationwide rollout and build 016

- The owner asked to implement the nationwide validation findings and prepare the next build. Published the directory, verified Пловдив fuel and technology and prepared build 016 for packaging. Grocery price coverage remains open in Пловдив. [Rollout record](ACTIVITY_LOG.md#23-november-2026--nationwide-rollout-and-build-016)

- The owner requested that the next steps be written in the TODO and the future release changelog. Build 016 is listed as unreleased. [Release TODO](PREVIEW_006_BACKLOG.md#build-016-release-plan) · [Changelog](../CHANGELOG.md#unreleased--build-016--app-059)


## Subscription plan and remediation focus

- The owner requested a future subscription plan and asked that remediation focus on historical errors. Prepared the plan and began remediation with the receipt commit-response failure. Retained the existing release and rollout status in the TODO. [Subscription plan](SUBSCRIPTION_PLAN.md) · [TODO](PREVIEW_006_BACKLOG.md#historical-defect-remediation)

- The owner reported a default-theme flash on launch with a custom theme selected. Added the startup fix to candidate 016 and recorded the Android cold-start check in the release TODO.

- The owner reported slow catalogue loading and uneven refresh across tabs, with „Горива“ the slowest, and requested background sync. Candidate 016 now opens with saved catalogue data, refreshes all three tabs through the same path and schedules Android background sync. The browser test showed a saved A95 price before the delayed network response and replaced it with the fresh response. Background execution and performance on a phone will be checked after build approval. [Verification](ACTIVITY_LOG.md#23-november-2026--catalogue-loading-and-android-background-sync)


## 23 November 2026 — release notes and repository name

The owner wrote:

> amend the todo and the changelog for the future release with the fixes  including the pull-to-refresh. Change the name of the repository to Per5on/spestovnik
> Keep the history of this chat

- Updated the build 016 release TODO and changelog with the fixes, the completed checks, and the remaining phone checks. The catalogue fixes include pull-to-refresh in all three tabs, faster repeat loads for fuel, and Android background sync. The previous exchange and test results are preserved in the project logs. [Release TODO](PREVIEW_006_BACKLOG.md#build-016-release-plan) · [Changelog](../CHANGELOG.md#unreleased--build-016--app-059)
- GitHub returned HTTP 403 for the repository settings write. The live receipt worker still authenticates using `Per5on/spestoslav`. Prepared a draft compatibility patch so the same repository can authenticate under either name during the transition. The rename awaits production rollout approval and GitHub settings access. [Compatibility PR](https://github.com/Per5on/spestoslav/pull/25)


## 23 November 2026 — thumbnail database and post-build backlog

The owner wrote:

> the name is not that important, you can leave it as pending.
> the product thumbnail database is still not active or not populating ... and is not unanimous, universal or similar as visual images. it has to be reconciled and ready for use ... inspect and add to the todo and the changelog. After the build, mark the backlog which issues have been resolved

- Deferred the rename. Verified the seeded symbol database, the absent public manifest, the live image coverage and the mix of bundled styles. Added the reconciliation work to the TODO and future changelog. The backlog will close each item after verification on the relevant build. [Inspection](ACTIVITY_LOG.md#23-november-2026--thumbnail-database-and-visual-reconciliation)


## 23 November 2026 — approved thumbnail fix and price-source review

- The owner asked for the thumbnail fix itself. Implemented a common WebP pack, versioned API delivery and bundled fallback. The owner approved the visual samples and requested the update in the upcoming changelog. [Approved preview](references/preview016-thumbnail-reconciliation.jpg) · [Changelog](../CHANGELOG.md#unreleased--build-016--app-059)
- The owner asked whether two or more price collectors could be combined with a verification check before populating prices. Reviewed the publisher, its cache schema and available feeds. Added the matching and verification work to the TODO. [Price verification](PREVIEW_006_BACKLOG.md#multi-source-price-verification)


## 23 November 2026 — nationwide price coverage and shutdown

- The owner asked whether the two-source approach repeats across most locations, requested nationwide verification and asked that differing collection methods and findings be recorded in the upcoming changelog.
- The owner asked to check regressions and missing dependencies after the audit, then stop the work environment to save electricity. They asked whether the chat window could be closed while the run continued. The audit, verification and handoff are filed in the repository. [Audit](ACTIVITY_LOG.md#23-november-2026--nationwide-price-source-audit-and-regression-check)


## 24 November 2026 — preview-10.8.1 build approval

- The owner approved packaging the combined fixes as bug-fix preview-10.8.1 and asked for a full code, currency and regression check before the build. The candidate uses Android version code 16 and app version 0.5.9. [Changelog](../CHANGELOG.md#preview-1081--build-016--app-059)
- Completed the pre-build audit, fixed receipt review and currency regressions, and delivered the checked internal APK. Device acceptance and backend rollout remain pending. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45352059558/artifacts/14901017390) · [Android checks](https://github.com/Per5on/spestoslav/actions/runs/45352059558) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45352011056)
