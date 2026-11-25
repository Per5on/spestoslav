# Спестовник subscription plan

Planning draft for a future release. Updated 23 November 2026.

## Offer to validate

| Tier | Proposed scope | Pricing hypothesis |
| --- | --- | --- |
| Free | Catalogue and local price comparison, basket, barcode scanning and existing receipt workflows. A small watchlist or digest can be trialed once alerts have reliable data. | Free |
| Plus | Up to 50 watched products, price thresholds and verified price-drop alerts in supported localities. Up to five tracked products for a free alert pilot is a separate hypothesis. | €2.99/month or €24.99/year |

Confirm tiers, the watchlist limits and final prices with the owner after an alert pilot. Offer recurring access to alerts only in markets and categories with verified source coverage. Explain price freshness, locality scope and delivery delays. Start with straightforward monthly and annual plans. Evaluate trials after the paid offer and renewal disclosures have been tested.

Use actual store payout reports to model net monthly revenue per paid account. Include fees, taxes as accounted for in those reports, refunds and annual-plan month allocation. Subtract variable feed, alert and support costs. Calculate break-even from fixed operating costs divided by positive net contribution per subscriber. Recheck the Play terms effective for the distribution market and release date before using a fee assumption. [Google Play EEA conditions](https://support.google.com/googleplay/android-developer/answer/14659200?hl=en)

## Purchase and entitlement design

1. **Android checkout.** Use Google Play Billing for paid digital alerts in the Play-distributed release. Plan one Plus product with monthly and annual base plans. Display the store’s localized price, billing interval, auto-renewal terms, included features, and a visible way to dismiss the offer. Put restore and the Play subscription-management link in account settings. Have separate review before any additional distribution or billing route. [Play payments policy](https://support.google.com/googleplay/android-developer/answer/9858738?hl=en) · [Play subscriptions policy](https://support.google.com/googleplay/android-developer/answer/9900533?hl=en)
2. **FastAPI verification.** Require sign-in before a purchase is attached to a Спестовник account. Pass an obfuscated account identifier into Play where supported. Verify the purchase on the server via the Google Play Developer API. Validate the package, product, purchase state and account binding, and acknowledge successful new purchases within Play’s window. Treat verified provider state as the entitlement authority. Keep API credentials and protected purchase tokens server-side with restricted access and redacted logs. [Subscription lifecycle](https://developer.android.com/google/play/billing/lifecycle/subscriptions)
3. **State transitions.** Record a unique provider purchase reference, associated account, plan, state, renewal flag, and paid-through time. Verify each real-time developer notification against the provider API. Handle duplicate and out-of-order events and reconcile missed notifications. Keep verified access during active and eligible grace periods, and through paid-through expiry on cancellation. Apply hold, expiry and revocation according to verified provider state. Billing outages should preserve the last verified entitlement within its known validity. [Notification reference](https://developer.android.com/google/play/billing/rtdn-reference)
4. **Customer and privacy operations.** Review checkout disclosures and withdrawal, refund, invoicing and tax responsibilities for the actual seller and markets. Update Bulgarian and English terms, privacy disclosures, support copy and deletion behavior. Explain that Play renewal management is separate when an account with an active subscription is deleted, and make the management link visible. Decide which billing records need retention and for how long before launch. [EU consumer rights directive](https://eur-lex.europa.eu/eli/dir/2011/83/oj/eng) · [Play subscriptions policy](https://support.google.com/googleplay/android-developer/answer/9900533?hl=en)

## Implementation and rollout order

- [ ] **Confirm scope and economics.** Agree on Plus benefits, limits, pricing, first market, operating costs, and who handles refunds and support.
- [ ] **Pilot free alerts.** Run monitored offers through freshness, locality and product checks. Test duplicate suppression, opt-in, delivery gaps, and what users see when prices expire. Use the pilot to decide which coverage can be advertised.
- [ ] **Integrate in a Play test track.** Use test products and accounts. Verify purchase, pending payment, acknowledgement, duplicate notification, restart and reinstall, device change, renewal, cancellation, grace, hold, refund, revocation, missed notification recovery and account deletion. Verify that an existing receipt, basket and free comparison still work throughout.
- [ ] **Review and release.** Review the Bulgarian and English screens and terms, Play requirements, alerts, support and reconciliation. Release to a small cohort and monitor activation, cancellations, refunds, delivery and discrepancies. Be able to disable new purchase entry while honoring existing subscriptions.

This plan is separate from build 016 remediation. Paid feature implementation and store setup are pending owner approval. [Build 016 TODO](PREVIEW_006_BACKLOG.md#build-016-release-plan)
