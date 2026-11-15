# Android preview 002 — cleanup build

Preserves the inline preview and APK 001. Version 0.1.2, Android versionCode 2, display label Спестовник 02. Same `bg.spestoslav.preview` package updates the preview app while retaining its saved basket/locality; the original `bg.spestoslav.app` app ID remains separate.

No new feature phase: retains the confirmed green/orange design, four tabs, sample artwork, shared location search and honest missing-price/camera states. Fixes transliterated locality matching, enforces the API's 100-item basket limit, avoids catalog requests for store-only screens and removes redundant state/reset work and a deprecated status-bar property.

Build dependency fixes keep Expo 54/native peers aligned; patched glob, minimatch, PostCSS and image-size are locked and tested. A guarded postinstall patch adapts Metro's file-path image reads to image-size's buffer API and backports the unavailable deepmerge prototype-key fix. Do not install with `--ignore-scripts` for real builds. Regression checks cover prototype poisoning and ordinary config merging.

The workflow names artifacts/APKs/screenshots with `PREVIEW_SEQUENCE=002`, uses current Node 24-compatible action versions and verifies the standalone test signature plus Android 10 smoke interactions. Source, run URL, artifact hash and final result are recorded in the audit report/activity log once checks complete. A successful build is not a claim that this PR's backend changes have been deployed.
