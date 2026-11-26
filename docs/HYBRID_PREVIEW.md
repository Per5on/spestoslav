# Preview 10.9.1-hybrid

26 November 2026 · build 018 · app 0.5.11 · branch `preview-10.9.1-hybrid`

The comparison build uses `bg.spestoslav.preview.hybrid` so it can coexist with 10.9.1. Android separates each app's local session, basket, theme and catalogue cache. Both clients use the same production API.

## Design and research

- Use a local Android-only Expo module, which Expo autolinks across generated projects. Load the module from the receipt screen. [Expo modules guidance](https://docs.expo.dev/modules/get-started/)
- Use ML Kit 16.0.0 with an Activity Result contract. Request one JPEG page to match the existing receipt API. Copy the result to private cache with a bounded stream and validate its JPEG bounds. Keep camera and gallery capture for failed scans and unavailable Play services. Scanner components can download on first use, and the SDK requires at least 1.7 GB RAM. [ML Kit document scanner](https://developers.google.com/ml-kit/vision/doc-scanner/android)
- Build separate signed ARM64 and ARMv7 APKs and verify the ABI of each. Use signed preview 10.9.1, build 017, at 43,965,037 bytes as the size baseline. [Android ABI packaging guidance](https://developer.android.com/build/configure-apk-splits)
- Defer the optional remote thumbnail manifest until saved state is restored and JavaScript reaches an idle period. Use the bundled artwork immediately. Measure first display, first usable screen, first cached price and first fresh price separately. Compare frame timing, memory, scanner launch time and receipt retakes on the same ARM phone. [Android startup measurements](https://developer.android.com/topic/performance/vitals/launch-time)

The staging backend fixture exercises the new fuel path. The production rollout remains separate. The pilot uses the current receipt API and OCR worker.

## Retailer price wording

All six languages use availability wording for products and fuel without a current price. Product cards show published online prices without a source-type label, regardless of the selected town. Basket comparison uses the same prices and includes only retailers with an active local branch. Each eligible retailer appears once. Fuel keeps branch counts and the existing station-price path. Sample products are identified as outside the comparison.
