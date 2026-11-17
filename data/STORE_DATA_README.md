# Store branch seed data

- `store_branches_seed.csv`: branch records, address, locality, optional coordinates and source.
- `retailer_source_registry.csv`: retailer coverage across all four app categories and store-locator research status.

Only branches explicitly listed by official retailer sources are included. Blank coordinates/postal codes mean they were not provided by the source; never invent them. Locality matching uses the existing `inhabited_localities` catalogue. Keep source URL and checked date for each branch. Deactivate closed branches rather than silently deleting them.

The current branch seed contains 116 source-backed starter records across multiple localities and 12 retailers; it is not a complete national inventory. The retailer registry covers the current catalogue; empty locator URLs are research tasks.

Sources checked 2026-11-14:
- Kaufland: https://www.kaufland.bg/moyat-kaufland/uslugi/filiali/veliko-trnovo-8600.html
- Lidl: https://www.lidl.bg/s/bg-BG/magazini/veliko-tarnovo/ul-narodni-buditeli-25/ and https://www.lidl.bg/s/bg-BG/magazini/veliko-tarnovo/ul-seres-3/
- Technopolis: https://www.technopolis.bg/stores
- Technomarket: https://www.technomarket.bg/magazini/veliko-tyrnovo/tehnomarket-veliko-tyrnovo
- Zora directory: https://zora.bg/stores

Structural validation: `python scripts/validate_inventory.py` checks provenance fields, duplicate branch keys and exact canonical name/municipality/region matches. The 15 November cleanup normalized two Fantastico region aliases to София; it did not change source addresses or advance source verification dates.
