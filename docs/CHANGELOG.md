# Спестовник changelog

Current work starts at [PROJECT_STATUS.md](PROJECT_STATUS.md). Original detailed notes are archived; [preview-sequence.json](references/preview-sequence.json) retains artifact URLs and digests. Historical APKs, screenshots and supplied references are unchanged.

## Preview 005 — candidate, not built yet

Version0.3.0/code5 is derived from `mobile/preview.json`. The owner authorized a build once final cleanup/checks pass.

- Initial 1,000 source-backed grocery identities in six approved groups, metadata-only catalogue cache, complete pagination and improved word/unit search. Retailer codes are not verified GTINs; no retailer price was invented or imported.
- Camera/image/manual GTIN lookup, unknown-code review requests, managed account sessions and owner-scoped private receipt upload, OCR, confirmation and moderation. Current prices change only after approval.
- Issue #8: exact six-item overflow order, nested Settings, Feedback entry and direct About with installed Android version metadata and `© 2026 Vimp. All rights reserved.` No Profile screen.
- Task3: header padding15→10, “Техника”, shared Магазини/Продукти/Обнови row with equal left buttons and text+0.5pt Refresh; stations/fuel/refresh and five fuel choices.
- Preview004 cleanup review covers CI, migrations, worker controls, metadata derivation, unused code and preserved compatibility. Real route directions and live Fuelo integration are not enabled.

See [mock scenarios](MOCK_SCENARIOS_005.md) and [review](CODE_REVIEW_004_2026-11-16.md). This candidate entry is not a release/CI/deployment success claim.

## Preview 004

Version0.2.1/code4. Products/Stores/Refresh moved onto one row; action/tab labels fit their available width. PR[#7](https://github.com/Per5on/spestoslav/pull/7), source`bbc7b9a`, merged`332ae57`. Android build/signature/emulator/publish [43711564982](https://github.com/Per5on/spestoslav/actions/runs/43711564982) and backend matrix43711564924 passed.

[Release](https://github.com/Per5on/spestoslav/releases/tag/android-preview-004) · [original notes](archive/previews/PREVIEW_004.md). APK SHA256`20e0e265ce8ed0e421c3a4b5d72f8bdcabb1cfe6b132bcc7e7a041230fbfc5e9`.

## Preview 003

Version0.2.0/code3. Four ordered upper tabs, money-bag logo, compact name-only locality, six languages/font preferences, larger photos and green add feedback. Home and postal storage retired after API0.5.0 rollout; 5,291 localities and139 branches retained.

PR[#6](https://github.com/Per5on/spestoslav/pull/6), merged`538bd9a`; backend43709020828 and Android43709020956 passed. [Release](https://github.com/Per5on/spestoslav/releases/tag/android-preview-003) · [original notes](archive/previews/PREVIEW_003.md). APK SHA256`bf02e1ec78f6d1b140fa6b92ff702a30c3aa2fa2279f2cabf465d688a7837f58`.

## Preview 002

Version0.1.2/code2. Locality transliteration, basket bounds and cleanup; preserved001 and its saved list/locality. [Release](https://github.com/Per5on/spestoslav/releases/tag/android-preview-002) · [original notes](archive/previews/ANDROID_PREVIEW_002.md). APK SHA256`693c45f72c197cc4cf205a3f61daeba8fb8901a15ff2fbc8222a5adcc4218e3e`.

## Preview 001

Preserved interactive snapshot01 plus Android0.1.1/code1 with live read-only catalogue/branch access, demo separation and local saved list/locality. Native run43600409741 passed. APK was retained locally/workflow, not publicly released. [Original notes](archive/previews/ANDROID_PREVIEW_001.md). APK SHA256`b834eae05f5db399a335f140e9e90d0d8fb7cff927dea8d8f46acd745cd654a2`.
