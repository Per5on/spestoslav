# Preview 005 — local mock verification and free-routing plan

Status: source work under verification. **The owner authorized building005 after all fixes/checks pass.** Preview 004 remains the last published APK. Synthetic data never enters the shared preview.

## Isolated systems

- Local PostgreSQL 16 disposable container: actual migration round-trip/model checks and repeated catalogue imports.
- Neon validation branch `br-ancient-shadow-balr2n5l`: additive migration 0007 and 1,000 deterministic source-backed grocery identities. Existing 5,291 localities / 139 branches retained; no price or barcode imported.
- Managed Auth on that isolated branch: sign-up, signed JWT issuer/signature verification, session restoration, sign-out and rejected refresh tested separately from mocked UI auth. Synthetic accounts use `example.invalid`; no real customer account is used.
- Browser scenario server `backend/tests/scenario_api.py` requires `SPESTOVNIK_SIMULATION=local-only`. It contains synthetic users/shops/prices and is never imported by the deployed application. Bind only to localhost. Its test-control routes are not production API routes.

## Reproduce without an APK build

1. Generate fixtures: `python scripts/generate_mock_images.py --output /tmp/spestovnik-simulation --video` (Pillow and DejaVu Sans required). Images explicitly say SIMULATION / СИМУЛАЦИЯ. They are not evidence of retailer prices or barcode ownership.
2. Configure a private temporary `RECEIPT_STORAGE_DIR`, Tesseract `bul+eng`, and start the local scenario server:
   `SPESTOVNIK_SIMULATION=local-only PYTHONPATH=backend:backend/tests python -m uvicorn scenario_api:app --host 127.0.0.1 --port 8774`.
3. Run the existing app in development web mode with `EXPO_PUBLIC_API_URL=http://127.0.0.1:8774`. This is a browser test, not an Android APK build or a release.
4. For automated camera input, Chromium can use `--use-fake-device-for-media-stream --use-fake-ui-for-media-stream --use-file-for-fake-video-capture=/tmp/spestovnik-simulation/simulation-camera.y4m`.
5. Mock sign-in is `alice@example.invalid` / `simulation-password`, or `bob@example.invalid` with the same synthetic password. These work only in the explicit local scenario server; they are not production credentials.

## Shopping journey and expected results

| Scenario | Action | Expected result |
|---|---|---|
| Fast catalogue | Load, search a late catalogue record, reload, then disconnect | All 1,000 source records are searchable; recent public metadata restores locally. Prices and credentials are excluded from the catalogue cache. Corrupt/duplicate/expired cache data is rejected. |
| Camera | Show the generated EAN image to the simulated video camera | Actual browser EAN decoder reads `4006381333931`, passes GTIN validation and finds the synthetic milk product. Repeated frames do not repeatedly add it. Camera stops on result/screen exit. |
| Image / manual fallback | Select the same barcode image; try a bad check digit | The image decoder finds the same code. Invalid GTIN/PLU/QR text is rejected; manual entry remains usable without camera permission. |
| Unknown barcode | Enter a valid unknown GTIN while signed in | An owner-scoped identification request is created once. No unverified product/barcode is silently published. |
| Complete basket | Add milk ×2 and oil ×1 in София | Complete shop A costs EUR5.50. The cheaper-looking partial shop C is incomplete and cannot win with a partial total. Travel/shipping remain excluded. |
| Receipt capture/upload | Select/photograph the synthetic receipt; explicitly upload | File is privately stored with EXIF removed. Owner can list/view it. Replaying the same upload key does not duplicate it; changed content with the same key is rejected. Another user cannot read/delete it. |
| Real OCR | Process uploaded fixture with Tesseract bul+eng | Only milk EUR2.20 and oil EUR3.00 become unmatched review lines. Totals, change, cash and quantity × unit-price lines are excluded, including Latin-lookalike РЕСТО. Unknown/BGN amounts are not assigned EUR values. |
| Unit-price confirmation | Match milk to its exact product and shop; type EUR1.10 | The line total is never prefilled as a unit price. Explicit confirmation queues a submission, leaving current comparison unchanged. |
| Moderation | Approve only inside the mock test controls / admin API | Comparison changes to EUR5.20 only after approval. Receipt item status follows the review. Rejected/unreviewed/expired observations remain outside published current prices. |
| Deletion/recovery | Delete; simulate storage failure, then retry | Owner's private data is removed. Interrupted deletion retains a tombstone, blocks OCR/image access and can be retried. Processing receipts cannot be deleted mid-claim. |
| Free route plan | Request the mock route over Home/A/B | Synthetic matrix produces a 4 km loop. It is explicitly a mock, has no real directions, and makes no claim about real shop distances or travel cost. |

## What still requires a permitted Android build/device test

Native camera permission prompts/denial, Expo Camera EAN decoding on Android, OS SecureStore session persistence, the Android photo picker and installed version metadata must be tested during the now-authorized APK build. Browser verification does not prove those native behaviours. Physical-device focus, glare and damaged labels also need a real-device check.

## Free shop routing — planned next capability

Keep route planning free. First use a manually chosen origin and at most two or three confirmed shops; optional GPS requires its own explicit permission. Verify branch coordinates, opening hours and shopping availability first. Existing canonical addresses alone are not a road-distance matrix.

Compare a complete one-shop basket with a multi-shop plan; show item coverage, stop order, distance/time source and any entered travel-cost assumptions separately. Do not infer stock from a price or include invented fuel costs. A simpler initial delivery can hand confirmed stops to an external navigation app. An in-app optimizer needs a routing provider or self-hosted engine with suitable terms; a public demo endpoint/free quota is not a production availability guarantee.

Current route simulation uses an explicitly synthetic matrix only. No real GPS, paid maps subscription or fabricated distance has been enabled.

Browser commands: install `mobile/scripts/requirements-browser-tests.txt` and Chromium, then run `mobile/scripts/test-browser-workflows.py --fixtures /tmp/spestovnik-simulation`, `test-browser-menu.py` and `test-browser-toolbars.py`. Each writes a new result directory and refuses to overwrite it.
