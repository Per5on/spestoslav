# Android preview 001

This implements the preserved interactive preview 01 in the existing Expo/React Native app. The inline preview and reference images remain unchanged. Future releases use a new numbered tag and APK filename; do not replace this release's assets.

- Display name: Спестовник 01. Version 0.1.1, Android versionCode 1.
- Preview package: `bg.spestoslav.preview`, separate from the existing `bg.spestoslav.app` package.
- Android 10+ (API 29). Standalone release-mode APK using Expo's test signing key; no Expo Go or Metro connection required. This is a test build, not a Play Store production signing setup.
- API: `https://spestoslav-api.onrender.com`; no credentials embedded. The app reads real backend data rather than the inline preview's snapshot.
- Four green/orange category tabs, shared searchable name/postal dropdown, supplied piggy-bank artwork, explicit opt-in demo photos (enabled for this preview), multi-product selection, persistent on-device locality and shopping list, branch inventory and manual barcode lookup.
- Real product lists and branch price reads are separate from the demo catalog. Demo products cannot be priced or sent to basket comparison. Branch quotes exclude online offers and shipping/travel.
- No camera, receipt upload or login UI in 001. The screen states this explicitly. Fuelo remains unavailable without API access. Empty inventory/price states do not imply complete nationwide coverage.
- The product browse screen currently loads the first 100 products, locality results the API's top 20 matches, branches/current prices the first 500. Pagination needs expanding before large catalog rollout.

## Build and verify

The `Android preview APK` GitHub Actions workflow installs locked dependencies, checks TypeScript, runs model regression checks, validates Expo dependencies, generates native Android files and builds/signature-verifies the standalone APK. Generated native trees are ignored; all native settings are in `mobile/app.json`.

Locally: `cd mobile && npm ci && npm run typecheck && npm test`. Then `npx expo prebuild --platform android --no-install` and `cd android && ./gradlew assembleRelease` with Android SDK/NDK and Java 17 installed.

The APK and its SHA-256 are retained in the numbered workflow artifact and published with a numbered GitHub prerelease after successful verification. The workflow does not modify Render or Neon. End-to-end camera/receipt claims must wait for an implemented authenticated flow.
