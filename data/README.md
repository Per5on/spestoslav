# Bulgarian locality reference

The active `bulgaria_localities.csv` retains the 5,291 stable GeoNames locality identities already used by the database, with Bulgarian/Latin names, municipality/region codes and provenance. Postal values were removed at the owner's request; no locality was deleted. The source GeoNames BG archive is retained as a geographic reference source, not as a postal-search dataset. GeoNames is a reference dataset, not an authoritative Bulgarian master register.

Refresh with `python scripts/import_geonames_localities.py`; import using `scripts/import_localities_to_db.py`. Identity remains Bulgarian name + Latin name + municipality code + region code; never derive identity from a postal code or admin grouping alone. The importer writes one row per identity and does not create postal links.

Source: https://download.geonames.org/export/zip/BG.zip ; attribution GeoNames (CC BY 3.0), https://www.geonames.org/export/zip/ . Names/administrative fields come from the source; missing fields are not guessed. Optional source coordinates remain descriptive reference data and do not add GPS/OSM UI.

Branch and retailer source validation: `python scripts/validate_inventory.py`. Home is removed from the active registry; the 29 remaining retailers do not imply complete branch or price coverage. Existing source addresses/check dates are preserved. Official NSI EKATTE reference: https://www.nsi.bg/nrnm/ekatte/archive .
