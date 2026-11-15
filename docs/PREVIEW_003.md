# Preview 003 — compact navigation, settings and name-only locality

Owner's 15 November instructions supersede the earlier four-category/postal/piggy-bank brief.

## Interface

- Upper tabs, left to right: **Храни · ТЕХНИКА · Горива · Моят списък**. The first three are backend categories; My list is the existing saved-basket screen, not a new catalog category.
- No lower ribbon. Header cart replaced by vertical three-dot settings, containing Scan, Sign in, Receipts, Font size and Language. Scan retains manual barcode lookup; camera/sign-in/receipt UI remains explicitly unavailable rather than faked.
- Working interface-language choices: Bulgarian, English, German, Spanish, French, Russian. Working saved font choices 90/100/115/130%; system font scaling remains supported.
- Header default height reduced by 1 React Native logical point; product search reduced by 0.5 point overall. Location field drops its interior label and optional mode buttons, and is 44 points high with name-only suggestions and municipality/region details.
- Product images increase from 60×90 to 88×104 while default cards retain a 125-point minimum height using tighter padding. The per-product cart turns green for one second after a successful addition; repeated taps restart its timer, and rejected additions do not flash.
- Active piggy-bank asset removed. Money-bag/coin logo isolated from the supplied sample with image editing; original references and previous numbered previews stay archived.

## Backend and data retirement

API 0.5.0 removes postal lookup and all ORM/SQL dependency on postal storage. An empty deprecated `postal_codes` response array remains solely so published 001/002 clients can still render name results; it reads/stores no postal data. New 003 clients neither use nor show it.

`backend/migrations/sql/0006_remove_home_postal.sql` is the single versioned removal script used by fresh-install Alembic 0006 and the shared legacy preview. It removes Home-owned dependent records in FK order, then Home products/branches/retailers/category. Shared non-Home tables/localities remain. It drops postal association storage and the two postal columns without a CASCADE table drop. Structure-only downgrade cannot recreate deleted data; the pre-change branch is the recovery copy.

- Shared preview before removal: 5,291 localities, 139 branches, 38 retailers, 1 Home category, 9 Home retailers, 0 Home products/branches, 5,296 postal links, 0 receipts.
- Validation branch `br-crimson-feather-balgu231`: transaction succeeded; after removal 5,291 localities, 139 branches, 29 retailers, 0 Home categories and 0 postal storage columns. Shared preview was still unchanged at that validation point.
- Pre-change recovery snapshot: `br-frosty-star-badgjcyw`, created without compute from `br-snowy-morning-baym8iw6`.
- Retained existing GeoNames identities in a deduplicated locality-only CSV; all 5,291 identities match the previous import key. Active importer/retailer registry/seed files no longer store postal codes or Home retailers. Source addresses, coordinates and source-check dates are unchanged.

Rollout order: test fresh PostgreSQL migrations and FK cleanup; merge and deploy the name-only API; verify it works with the existing schema; then apply the already validated retirement transaction to shared preview. Verify counts/readiness/name search and absence of postal/Home storage afterward. Never run the separate Alembic baseline on the shared Flyway database.

## Verification and version preservation

Version 0.2.0, Android versionCode 3, package `bg.spestoslav.preview`. Earlier artifacts stay unchanged; the next changed preview after this is 004. Native APK and visual snapshot are named 003.

Local TypeScript/model/language-key checks pass. Browser checks against current public API data pass ordered tabs, absent Home/postal/lower ribbon, name-only search, 88-point thumbnails, one-second feedback, shared location, six languages, font scaling, state restoration, widths 320/390/736 and API retry recovery, without JavaScript errors. Screenshot capture waits for modal transitions to finish. PostgreSQL and native emulator CI plus shared rollout remain separate gates until their actual results are recorded in the activity log.

## Completed shared rollout

PR #6 source `293c4be` passed PostgreSQL CI 43709020828 (**61 tests per SQLAlchemy matrix job**) and Android/native/publish run 43709020956. Merged as `538bd9a`. API 0.5.0 deployed live as Render `dep-dbsppd8n74is73aimkc0`; version/readiness/name-only search were checked **before** retiring storage. Then the validated SQL transaction was applied to shared preview.

Shared result: 5,291 localities, 139 branches, 29 retailers, zero Home categories and zero postal storage columns. Locality UUID digest `f8d3d55571c20ea931cfd66c131d8f63` and branch UUID/locality/address digest `6694e399b5549bdb34ab49ba72a2300c` match pre-change values exactly. Locality CSV source-ID digest `d32d673ce9eccaee8bac205bb1b86e3a` matches the existing database. Post-removal readiness, ordered three-category read, name search, empty postal search and Sofia's 46 grocery branches passed. Recovery/validation branches remain isolated; no app credentials were switched.

Published [APK/snapshot 003](https://github.com/Per5on/spestoslav/releases/tag/android-preview-003); downloaded APK checksum matched `bf02e1ec78f6d1b140fa6b92ff702a30c3aa2fa2279f2cabf465d688a7837f58`. The actual Android screenshot was inspected. The owner then requested the extra single-row/autosizing refinement, which is preserved separately as 004.
