#!/usr/bin/env python3
"""Render an additive store import for the shared legacy preview schema."""

import argparse
import hashlib
import json

from validate_inventory import identity, read, validate


def render(city, municipality, region, categories):
    validate()
    locality = identity(city, municipality, region)
    rows = [
        row for row in read("store_branches_seed.csv")
        if identity(row["city"], row["municipality"], row["region"]) == locality
        and row["category_code"] in categories
    ]
    if not rows:
        raise ValueError("No source-backed branches for this locality and category")
    for row in rows:
        key = "|".join((row["retailer_code"], *locality, row["address"].casefold()))
        row["inventory_id"] = "inventory:" + hashlib.sha256(key.encode()).hexdigest()
    payload = json.dumps(rows, ensure_ascii=False)
    if "$source_rows$" in payload or "$import_branches$" in payload:
        raise ValueError("Reserved SQL delimiter in source data")
    return """DO $import_branches$
DECLARE r jsonb; locality uuid; matches integer;
BEGIN
  SET LOCAL lock_timeout = '5s';
  LOCK TABLE store_branches IN SHARE ROW EXCLUSIVE MODE;
  FOR r IN SELECT value FROM jsonb_array_elements($source_rows$@PAYLOAD@$source_rows$::jsonb) LOOP
    SELECT count(*), min(id::text)::uuid INTO matches, locality
    FROM inhabited_localities
    WHERE name_bg = r->>'city' AND municipality = r->>'municipality' AND region = r->>'region';
    IF matches <> 1 THEN RAISE EXCEPTION 'Expected one canonical locality'; END IF;
    IF NOT EXISTS (
      SELECT 1 FROM catalog_retailers
      WHERE code = r->>'retailer_code' AND category_code = r->>'category_code' AND active
    ) THEN RAISE EXCEPTION 'Missing active retailer: %', r->>'retailer_code'; END IF;
    IF EXISTS (
      SELECT 1 FROM store_branches
      WHERE source = r->>'source' AND source_id = r->>'inventory_id'
        AND (retailer_code, locality_id, address) IS DISTINCT FROM
            (r->>'retailer_code', locality, r->>'address')
    ) THEN RAISE EXCEPTION 'Conflicting branch source identity'; END IF;

    INSERT INTO store_branches
      (retailer_code, retailer_name, branch_name, city, settlement, municipality, region,
       address, latitude, longitude, source, source_id, locality_id, active, last_seen_at)
    SELECT r->>'retailer_code', r->>'retailer_name', nullif(r->>'branch_name',''),
      r->>'city', r->>'city', r->>'municipality', r->>'region', r->>'address',
      nullif(r->>'latitude','')::numeric, nullif(r->>'longitude','')::numeric,
      r->>'source', r->>'inventory_id', locality, true,
      (r->>'source_checked_at')::date::timestamp AT TIME ZONE 'Europe/Sofia'
    WHERE NOT EXISTS (
      SELECT 1 FROM store_branches WHERE retailer_code = r->>'retailer_code'
        AND locality_id = locality
        AND regexp_replace(lower(normalize(address, NFKC)), '[^[:alnum:]]+', '', 'g') =
            regexp_replace(lower(normalize(r->>'address', NFKC)), '[^[:alnum:]]+', '', 'g')
    )
    ON CONFLICT (source, source_id) DO NOTHING;
  END LOOP;
END $import_branches$;""".replace("@PAYLOAD@", payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city", required=True)
    parser.add_argument("--municipality", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--category", action="append", required=True, choices=("technology", "fuel"))
    args = parser.parse_args()
    print(render(args.city, args.municipality, args.region, set(args.category)))
