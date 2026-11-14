# Legacy repository audit

Audit target: `Per5on/testing`, branch `main`. This document records source and live-schema observations made on 2026-11-14. The legacy repository and its deployed preview have not been modified.

## 1. Existing application

- Android client is Kotlin with Jetpack Compose, Material 3 and Retrofit.
- Backend is Kotlin/Spring Boot 3.4.1, Kotlin 2.0.21, JPA, JdbcTemplate, Caffeine cache and Flyway; Java toolchain 17.
- Android uses compile/target SDK 35 and minimum SDK 26.
- The main Android UI is concentrated in a single `MainActivity.kt` file (about 42 KB), with translations embedded in Kotlin maps for Bulgarian and English.
- Language and location settings are persisted in Android SharedPreferences.
- The UI has a category ribbon for groceries, technology, home and fuel, plus a separate five-item bottom navigation (Categories, Pricing, Add, Basket, Profile). The new app's agreed primary navigation is instead exactly four category tabs: Храни, Горива, Дом, Техника.
- Existing location selection is shared across views, but includes manual coordinates, GPS permission and radius options. The new app should prioritize settlement/postal-code search and keep GPS optional.
- The existing screen uses placeholder/demo price and basket views and explicitly says there are no verified live prices. The Add dialog currently closes and clears its text locally; it does not submit to an API.

## 2. Backend endpoints found in source

- `GET /api/v1/catalog`: active category catalogue and retailers with active mapped branches in the supplied locality or coordinate radius. Without a selected locality or coordinates it returns no locally available retailers.
- `GET /api/v1/branches?locality=...`: active branches matching city or settlement.
- `GET /api/v1/branches/localities?query=...`: branch-derived locality suggestions.
- `GET /api/v1/branches/nearby?latitude=...&longitude=...&radiusKm=...`: distance-sorted active branches.
- `GET /api/v1/localities?query=...`: locality search is declared in two different controller classes in different packages (`catalog.LocalityController` and `locality.LocalityController`). Both declare the same GET route. This is a Spring request-mapping collision risk and should be resolved before relying on the legacy backend.
- No product, price-history, promotion, basket or submission API controller was found in the tracked source files reviewed. Corresponding UI areas are currently placeholders.

## 3. OpenStreetMap import

- `OpenStreetMapImportJob` queries the Bulgaria Overpass area for mapped settlements, relevant shop types and fuel stations.
- It attempts retailer matching against a hard-coded list of 37 retailer aliases and requires address locality tags before importing a branch.
- It upserts OSM records using source identifiers and runs on a 12-hour fixed delay after an initial delay.
- Mapped settlement records and branch records are separate. OSM coverage and address completeness therefore affect what can appear in a locality.
- The app includes OSM attribution text. Any reuse must preserve appropriate attribution and source provenance.
- OSM branch discovery is a store-location catalogue, not a verified price feed.

## 4. Repository migrations versus live Neon schema

The legacy repository contains only four tracked Flyway migration files: V1 through V4. The live Neon branch's `flyway_schema_history` contains a successful baseline at version 5 and a successful V6 migration named `V6__add_price_note.sql`; that V6 script is not present in the repository tree. The baseline means the live database cannot be reconstructed solely from the four checked-in migration files.

Live Neon schema inspection found these public tables:

- `product_categories`
- `catalog_retailers`
- `products`
- `store_branches`
- `inhabited_localities`
- `price_observations`
- `user_submissions`
- `flyway_schema_history`

The inspected branch currently contains 4 categories and 38 retailers. It contains zero rows in products, store branches, inhabited localities, price observations and user submissions.

Important existing data-model concepts worth carrying forward:
- Product barcode, brand, variant, package quantity/unit and normalized name.
- Physical store branches with settlement, municipality, region, address and coordinates.
- Separate inhabited-locality records with OSM source identifiers.
- Price observations tied to a product and physical branch, with EUR-only price fields, source, source reference, verification flag, validity timestamps and collection timestamp.
- User submissions with pending/approved/rejected status and optional location.
- Retailer/category catalogue seeded for grocery, technology, home and fuel.

The live `price_observations` table enforces EUR currency and positive prices. The source migration V4 adds branch source provenance and OSM source IDs. V6 adds `price_note`, but its migration file needs recovery or reconstruction from the live history/source before any migration chain is adopted.

## 5. Issues and migration implications

1. Resolve the duplicate `/api/v1/localities` controller mapping.
2. Recover the missing V5 baseline definition and V6 migration script, or create a clean, complete Alembic migration history for the new backend. Do not point Alembic at the legacy Flyway history as if it were an Alembic version table.
3. Add and test API contracts for products, prices, price history/promotions and submissions; the corresponding live tables alone do not provide these application behaviours.
4. Implement real submission persistence and moderation instead of the current local-only Add dialog.
5. Implement real basket/list persistence and comparison logic instead of the current demo cards.
6. Redesign navigation to the agreed four category tabs, and implement one shared settlement/postcode selector. GPS and distance radius are optional rather than mandatory.
7. The current locality schema has no dedicated postal-code field. Decide how postal-code search is sourced and represented before implementing that requirement.
8. Keep price-source verification explicit. Never expose demo or unreviewed submissions as verified live prices.
9. Expand and validate retailer/branch coverage beyond OSM matches; OSM is incomplete and does not establish retailer price availability.

## 6. Reuse strategy

Reuse the domain concepts and verified seed catalogue where appropriate, not the legacy UI or backend implementation line-for-line. The new project remains React Native + TypeScript, FastAPI and Alembic, with Neon PostgreSQL and Render hosting. The legacy repository and existing Render preview remain reference-only until a separately approved migration plan is ready.

## 7. Safety status

- Audit operations against GitHub and Neon were read-only.
- No production schema, rows, credentials, Neon branches, Render services or deployments were changed.
- The legacy repository `Per5on/testing` remains untouched.
