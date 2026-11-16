# Preview 004 — one-row catalog controls and automatic button text fitting

Follow-up owner instructions after 003 publication: put Products, Stores and Refresh on one row and automatically fit button fonts.

- Grocery catalog now uses **Продукти · Магазини (count) · Обнови** on one row, in that order. The duplicate plain Products heading and separate selector row are removed; search/results move up one full control row.
- Shared action buttons and upper-tab labels automatically fit one line. Android uses native text fitting; the browser renderer measures the actual font. User/system font preferences set the preferred maximum; fitting shrinks only as needed, with an 11-point lower bound. Touch areas remain at least 44 points high.
- No Home/postal/backend change beyond 003. All previous redesign behavior and saved data are retained. The published 003 APK/snapshot remain unchanged; 004 is version 0.2.1, versionCode 4.

Local TypeScript/model checks and live-API browser regression pass. Geometry checks verify exactly three ordered controls on the same row, no clipped labels, minimum font/touch sizes, all six languages at 320px/130%, and the earlier redesign behaviors. Native Android 10 verification also passed, including the actual toolbar geometry.

## Verified delivery

- PR #7 source `bbc7b9ae1fab1742475e9fc7e26677e281e93a1f`, merged as `332ae57346b9487dbd6e046fc55ea2ec6ee67881`.
- Backend matrix [43711564924](https://github.com/Per5on/spestoslav/actions/runs/43711564924): 61 tests passed in each SQLAlchemy job. Android [43711564982](https://github.com/Per5on/spestoslav/actions/runs/43711564982): compile, signing verification, Android 10 smoke and publication passed.
- [APK 004](https://github.com/Per5on/spestoslav/releases/download/android-preview-004/spestovnik-preview-004.apk), SHA-256 `20e0e265ce8ed0e421c3a4b5d72f8bdcabb1cfe6b132bcc7e7a041230fbfc5e9`. Downloaded artifact checksum verified; actual emulator screenshot inspected and preserved as `references/preview-004-android.png`. `references/preview-004-menu.png` is a browser settings snapshot.
- Backend/data/scripts trees are unchanged from deployed `538bd9a`; readiness rechecked. No further database retirement or API deployment was necessary for this UI refinement.
- Earlier numbered previews remain intact. Next changed app build is 005.
- Owner deferred button-layout changes on the other tabs until later instructions. Shared text auto-fitting applies now, but other tab layouts were not redesigned.
- Owner asked about price comparison and retailer APIs: existing `POST /api/v1/baskets/compare` provides a foundation. Reliable verified price ingestion/product identity remains the larger dependency; do not assume retailer APIs exist or fabricate coverage. No additional integration was authorized by this question.
