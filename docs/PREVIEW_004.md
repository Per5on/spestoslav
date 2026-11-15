# Preview 004 — one-row catalog controls and automatic button text fitting

Follow-up owner instructions after 003 publication: put Products, Stores and Refresh on one row and automatically fit button fonts.

- Grocery catalog now uses **Продукти · Магазини (count) · Обнови** on one row, in that order. The duplicate plain Products heading and separate selector row are removed; search/results move up one full control row.
- Shared action buttons and upper-tab labels automatically fit one line. Android uses native text fitting; the browser renderer measures the actual font. User/system font preferences set the preferred maximum; fitting shrinks only as needed, with an 11-point lower bound. Touch areas remain at least 44 points high.
- No Home/postal/backend change beyond 003. All previous redesign behavior and saved data are retained. The published 003 APK/snapshot remain unchanged; 004 is version 0.2.1, versionCode 4.

Local TypeScript/model checks and live-API browser regression pass. Geometry checks verify exactly three ordered controls on the same row, no clipped labels, minimum font/touch sizes, all six languages at 320px/130%, and the earlier redesign behaviors. Native emulator CI remains a separate gate until its actual result is recorded.
