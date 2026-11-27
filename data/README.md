# Bulgarian locality reference

The active `bulgaria_localities.csv` retains the 5,291 stable GeoNames locality identities already used by the database, with Bulgarian/Latin names, municipality/region codes and provenance. Postal values were removed at the owner's request; no locality was deleted. The source GeoNames BG archive is retained as a geographic reference source, not as a postal-search dataset. GeoNames is a reference dataset, not an authoritative Bulgarian master register.

Refresh with `python scripts/import_geonames_localities.py`; import using `scripts/import_localities_to_db.py`. Identity remains Bulgarian name + Latin name + municipality code + region code; never derive identity from a postal code or admin grouping alone. The importer writes one row per identity and does not create postal links.

Source: https://download.geonames.org/export/zip/BG.zip ; attribution GeoNames (CC BY 3.0), https://www.geonames.org/export/zip/ . Names/administrative fields come from the source; missing fields are not guessed. Optional source coordinates remain descriptive reference data and do not add GPS/OSM UI.

Branch and retailer source validation: `python scripts/validate_inventory.py`. Home is removed from the active registry; the 29 remaining retailers do not imply complete branch or price coverage. Existing source addresses/check dates are preserved. Official NSI EKATTE reference: https://www.nsi.bg/nrnm/ekatte/archive .

## Retail price sources

The [price-source registry](price_source_registry.csv) records direct retailers, third-party mirrors, open data and fuel sources. Each row tracks a source and category. The `collection_status` field records the latest review and has no effect on the publisher's runtime configuration. The [retailer registry](retailer_source_registry.csv) tracks physical store locators and the [store seed](store_branches_seed.csv) records reviewed branches.

- T MARKET, BulMag, Techmart and Ardes supplied the live product-price pilot. Store locations determine retailer eligibility for comparison.
- Broshura.bg and Pazaruvaj are candidates that require a suitable, authorized feed. Brochure validity and store scope can vary. A Pazaruvaj listing showed an older price for the same Ardes model during the review. [Broshura terms](https://s3-eu-west-1.amazonaws.com/public-legal-docs.offerista/offerista-bg/en/tou.html) · [Pazaruvaj merchant terms](https://www.pazaruvaj.com/static/general_terms_and_conditions.html)
- Burlex and Колкострува supply store-level price observations. The archive preserves their original store scope. [Колкострува open data](https://kolkostruva.bg/opendata)
- Fuelo is the preferred fuel source when licensed feed access is available. KARAI is the secondary source and its timestamps must agree with the published observation date. [Fuelo developer docs](https://developers.fuelo.net/docs) · [KARAI Fuel Index](https://karai.bg/fuel-prices/indeks)

[Review evidence](../docs/HYBRID_PREVIEW.md#27-november--production-pilot-restored-and-third-party-review) · [Enable recurring publication](../docs/PRICE_FEED_SETUP.md)
