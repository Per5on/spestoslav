Legacy Flyway source files stop at V4. The live preview has a V5 Flyway baseline and V6 `add price note`; the baseline has no SQL file by design and V6 source is absent. Do not invent either script or migrate the legacy preview. The new app has an independent Alembic revision `0001_initial` for an isolated new development database.

The duplicate legacy `GET /api/v1/localities` mapping is avoided: the new FastAPI app has one `GET /api/v1/localities?q=...` route. The initial schema models categories, retailers, products, canonical localities, branches, price observations and submissions. Product/price/history/promotion/basket/submission APIs still require implementation and tests; schema presence is not a complete feature.

Price observations retain provenance and timestamps; verification defaults false; EUR only. Scraping is not implemented without permitted retailer access.
