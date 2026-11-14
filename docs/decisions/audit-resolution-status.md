# Audit resolution status

| Finding | Current response |
|---|---|
| Duplicate locality route | Single canonical FastAPI locality search route in new project; legacy unchanged. |
| Missing Flyway V5/V6 source | Do not reconstruct unknown history; independent Alembic baseline created. |
| Missing product/price/submission APIs | Core SQLAlchemy models and locality/category endpoints started; domain endpoints remain outstanding. |
| Prototype basket/submission UI | Not treated as functional; persistent APIs and tests required before shipping. |
| GPS/radius selection | Excluded entirely; shared searchable settlement dropdown only. |
| Postal code absent | Optional postal_code field in new locality model; populate only from verified source. |
| OSM incompleteness | Supplementary source only; canonical settlement registry required. |
| Price verification | Provenance retained; observations default unverified. |
