# Audit resolution status

| Finding | Current response |
|---|---|
| Duplicate legacy locality route | New FastAPI app defines one canonical `GET /api/v1/localities?q=...` route. Legacy repo left unchanged. |
| Missing Flyway V5/V6 source | Do not invent missing migration scripts or run Flyway against the legacy preview. New project has an independent Alembic baseline. |
| Missing product/price/submission APIs | Initial SQLAlchemy domain models and category/locality endpoints are in place; product, price, promotion and submission endpoints still need implementation and tests. |
| Prototype basket/submission UI | Not considered functional; persistent APIs and tests are required before release. |
| GPS/radius location flow | Explicitly excluded. App-level shared searchable settlement dropdown only. |
| Postal code absent | Optional `postal_code` field exists in the new locality model; populate only from a verified dataset. |
| OSM incompleteness | OSM is supplementary, not the sole authoritative locality/postal-code registry. |
| Price verification | Provenance and timestamps are retained; new observations default to unverified; EUR only. |
| Reference website | Correct reference is `https://avtogararuse.org/index.cgi`; the form contains “Тръгва от” and “Пристига в” select controls. Adapt its selection pattern to one shared locality selector. |


## Current backend verification

The table above records historical preparation status. Current implementation and exact verification/rollout scope are tracked in `../BACKEND_READINESS.md`; frontend requirements are in `../FRONTEND_BRIEF.md`. New product, review, collection, scanning, national-offer and basket APIs have tests, but implementation/test success is not itself deployment evidence.
