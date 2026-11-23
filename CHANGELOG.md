# Спестовник changelog

This lists the recorded Android previews and pre-alpha and beta candidates through build 016. [Project activity log](docs/ACTIVITY_LOG.md) · [Release handoff](docs/CODEX_HANDOFF.md)

## Unreleased · build 016 · app 0.5.9

- Published the nationwide directory with 1,585 active branches. In Пловдив, live checks found five indicative technology offers and 17 indicative fuel offers. Current grocery prices for the city are still pending.
- Added a notice in the grocery and technology tabs when the selected town has no current prices. Included four reviewed Велико Търново branches in the staged grocery refresh. [Live browser preview](docs/references/preview016-plovdiv-grocery.png)
- Fixed candidate receipt upload recovery after a lost database commit response. Retries with the same request key can recover the saved receipt and its photo. Backend rollout is pending.
- Mobile tests, Android configuration, live browser checks and both hosted PostgreSQL jobs passed for source `dcbdea2`. APK packaging and device checks remain pending. [Hosted checks](https://github.com/Per5on/spestoslav/actions/runs/45249343835) · [Release TODO](docs/PREVIEW_006_BACKLOG.md#build-016-release-plan)

## Bug fix · build 015 · app 0.5.8

- Added missing verified branches for Varna and Veliko Tarnovo and published a fresh KARAI fuel update. The catalogue now surfaces priced products first and refreshes price data on resume.
- Added price-cache generation, staged scheduled publication, source error handling and review-queue expiry checks.
- Added candidate API limits for sign-in, password recovery and locality search. Removed `docs/12.docx` from this revision. [Build and rollout notes](docs/BUG_FIX_015.md)
- Verified the signed ARM APK and both hosted PostgreSQL jobs. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45210084849/artifacts/14836831458) · [Android checks](https://github.com/Per5on/spestoslav/actions/runs/45210084849) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45210224790)

## Beta_10.8 · build 014 · app 0.5.7

- Grouped fuel prices by chain and local branch count. A confirmed price that differs appears with the station address.
- Added email-code password recovery to sign-in. Verified the full flow with a simulated inbox. Live recovery still needs the backend rollout and an authorized test inbox.
- Added daily grocery, technology and fuel source checks on the default branch. Scoped the current-price request by category in the beta backend, separated confirmed price loading from indicative prices, and indexed product search.
- Imported six NSI locality codes, four corroborated handset GTINs and 1,358 dated КЗП grocery observations into the shared database. The live barcode API resolved all four codes and their zero-padded aliases. The price archive is historical and has no effect on current quotes.
- Added „Трети страни“ under „За приложението“ with credits for data, merchant addresses, images, libraries and services. Catalogue and fuel views retain price scope and image notices. [Browser preview](docs/references/beta-10.8-third-parties.png)
- The browser decoded one new GTIN from an image and returned the matching product through the live API. The first ARM candidate passed packaging and is superseded by the credits update. [First candidate run](https://github.com/Per5on/spestoslav/actions/runs/45188561983)
- The signed ARM test APK for source `cb8d736` passed Android CI for `arm64-v8a` and `armeabi-v7a`. Both hosted PostgreSQL jobs passed. Physical installation and camera scanning are pending. [APK artifact](https://github.com/Per5on/spestoslav/actions/runs/45191123258/artifacts/14826956549) · [Android run](https://github.com/Per5on/spestoslav/actions/runs/45191123258) · [Backend checks](https://github.com/Per5on/spestoslav/actions/runs/45191136452)

## Preview 10.7 · build 013 · app 0.5.6

- Reduced tab padding to 8 pt, placed the refresh control at the right edge of the responsive fuel toolbar and highlighted the narrower location field.
- Applied the market-scale launcher and header artwork used in this preview.
- Android CI passed APK signing and both ARM ABIs, plus validation of the test-signed bundle. [Android run](https://github.com/Per5on/spestoslav/actions/runs/45062475962)

## Preview 10.6 · build 012 · app 0.5.5

- Added the two-column Settings layout, icon-and-label category tabs, two fuel rows and the larger saved national merchant directory.
- Switched APK packaging to ARM. The owner confirmed the existing 10.6 APK installed. [Android run](https://github.com/Per5on/spestoslav/actions/runs/45039195640)

## Preview 10.5 · build 011 · app 0.5.4

- Added itemized basket comparisons, pop-up category groups, palette removals and product-matched representative thumbnails.
- Added the dated directory fallback, zoomable photos and the illustrative-photo notice. The hosted Android job passed after earlier runner failures. [Android run](https://github.com/Per5on/spestoslav/actions/runs/44930361440)

## Pre-alpha 010 · app 0.5.3

- Renamed the list tab to „Сравни цените“, simplified catalogue controls and added the merchant directory.
- Renamed the appearance menu to „Тема“ and made thumbnails always visible. Android CI passed emulator smoke, ARM package verification and test-signed bundle validation. [Android run](https://github.com/Per5on/spestoslav/actions/runs/44923545071)

## Pre-alpha 009 · app 0.5.2

- Added theme choices, symbolic thumbnails and guest and authenticated data-deletion workflows. Native smoke and ARM packaging passed. [Android run](https://github.com/Per5on/spestoslav/actions/runs/44348096077)

## Preview 008 · app 0.5.1

- Improved catalogue loading, locality ordering, account error and session handling, receipts, and Android packaging checks. The corrected Android run produced a verified APK. [Android run](https://github.com/Per5on/spestoslav/actions/runs/44309388382)

## Preview 007 · app 0.5.0

- Added source-backed grocery and technology catalogues, sample photos, five fuel selections and private receipt workflows. Android smoke exercised camera and barcode decoding. [Android run](https://github.com/Per5on/spestoslav/actions/runs/44149787807)

## Preview 006 · app 0.4.0

- Development candidate for catalogue and Settings refinements, locality performance, and feed and feedback readiness. Backend CI passed the recorded candidate. The follow-up Android job passed and skipped publication. [Candidate Android run](https://github.com/Per5on/spestoslav/actions/runs/43871290741)

## Preview 005 · app 0.3.0

- Added grocery workflows, image barcode decoding, camera and permission handling, and private receipts with OCR. Feedback moved under About.
- Published as an Android prerelease after the corrected native build passed. [Release](https://github.com/Per5on/spestoslav/releases/tag/android-preview-005) · [Android run](https://github.com/Per5on/spestoslav/actions/runs/43859570901)

## Preview 004 · app 0.2.1

- Put catalogue controls and refresh on one row and added responsive button labels. Native verification passed and the APK was published. [Release](https://github.com/Per5on/spestoslav/releases/tag/android-preview-004)

## Preview 003 · app 0.2.0

- Retired Home and postal search, introduced the revised four tabs, six interface languages and saved text sizing, and updated the catalogue presentation. Native verification passed and the APK was published. [Release](https://github.com/Per5on/spestoslav/releases/tag/android-preview-003)

## Preview 002 · app 0.1.2

- Cleaned up dependencies and code, tightened basket and receipt behavior, and verified Android smoke. The APK was published. [Release](https://github.com/Per5on/spestoslav/releases/tag/android-preview-002)

## Preview 001 · app 0.1.1

- First preserved interactive snapshot and standalone Android APK. Added a searchable locality, saved basket and early barcode lookup. Native compilation and Android 10 smoke passed. [Snapshot](docs/references/preview-001.html) · [Android run](https://github.com/Per5on/spestoslav/actions/runs/43600409741)
