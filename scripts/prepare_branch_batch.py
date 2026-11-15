#!/usr/bin/env python3
"""Emit atomic, idempotent SQL for a reviewed batch on the legacy preview schema.

Usage: python scripts/prepare_branch_batch.py data/batches/2026-11-14-groceries.csv
Execute the printed statement on the explicitly selected preview branch.
No connections, schema changes, or implicit closure inference.
"""
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


def source_id(row):
    """Locally assigned identity, not a retailer-issued branch identifier."""
    identity = '|'.join(row[k].strip() for k in (
        'retailer_code', 'city', 'municipality', 'region', 'address'))
    return 'inventory:' + row['retailer_code'] + ':' + hashlib.sha256(identity.encode()).hexdigest()[:32]


def load_batch(path, seed_path=None):
    with Path(path).open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError('Empty batch')
    identities = set()
    for row in rows:
        for key in ('retailer_code', 'retailer_name', 'category_code', 'branch_name',
                    'city', 'municipality', 'region', 'address', 'source',
                    'source_url', 'source_checked_at'):
            if not row.get(key, '').strip():
                raise ValueError(f'Missing {key}')
        if row['source'] != 'OFFICIAL_STORE_LOCATOR':
            raise ValueError('Only reviewed official-source batches are supported')
        if urlparse(row['source_url']).scheme != 'https' or not urlparse(row['source_url']).netloc:
            raise ValueError('Expected HTTPS source URL')
        if date.fromisoformat(row['source_checked_at']) > date.today():
            raise ValueError('Future verification date')
        key = source_id(row)
        if key in identities:
            raise ValueError('Duplicate physical branch in batch')
        identities.add(key)
        if any(row.get(k) for k in ('latitude', 'longitude', 'postal_code')):
            raise ValueError('This importer supports batches without optional geographic fields only')
    if seed_path:
        with Path(seed_path).open(encoding='utf-8', newline='') as handle:
            seed = list(csv.DictReader(handle))
        for row in rows:
            if sum(row == item for item in seed) != 1:
                raise ValueError('Each batch row must occur exactly once in seed')
    return rows


def render_sql(rows):
    payload = json.dumps([dict(row, inventory_id=source_id(row)) for row in rows], ensure_ascii=False)
    literal = "E'" + payload.replace("\\", "\\\\").replace("'", "''") + "'"
    if "$inventory_batch$" in payload:
        raise ValueError("Reserved SQL delimiter in batch")
    return f"""DO $inventory_batch$
DECLARE r jsonb; locality uuid; matches integer;
BEGIN
  SET LOCAL standard_conforming_strings = on;
  LOCK TABLE store_branches IN SHARE ROW EXCLUSIVE MODE;
  FOR r IN SELECT value FROM jsonb_array_elements({literal}::jsonb) LOOP
    SELECT count(*), min(id::text)::uuid INTO matches, locality
    FROM inhabited_localities
    WHERE name_bg=r->>'city' AND municipality=r->>'municipality' AND region=r->>'region';
    IF matches <> 1 THEN
      RAISE EXCEPTION 'Expected one locality for %, %, %; found %',
        r->>'city', r->>'municipality', r->>'region', matches;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM catalog_retailers
        WHERE code=r->>'retailer_code' AND category_code=r->>'category_code' AND active) THEN
      RAISE EXCEPTION 'Missing active retailer/category: %', r->>'retailer_code';
    END IF;
    IF EXISTS (SELECT 1 FROM store_branches
        WHERE retailer_code=r->>'retailer_code' AND locality_id=locality
          AND address=r->>'address'
          AND (source,source_id) IS DISTINCT FROM (r->>'source',r->>'inventory_id')) THEN
      RAISE EXCEPTION 'Existing physical branch has another identity: %', r->>'address';
    END IF;
    IF EXISTS (SELECT 1 FROM store_branches
        WHERE source=r->>'source' AND source_id=r->>'inventory_id'
          AND (retailer_code,locality_id,address,active) IS DISTINCT FROM
              (r->>'retailer_code',locality,r->>'address',true)) THEN
      RAISE EXCEPTION 'Identity collision or inactive branch requires review: %', r->>'inventory_id';
    END IF;
    INSERT INTO store_branches
      (retailer_code,retailer_name,branch_name,city,settlement,municipality,region,
       address,source,source_id,locality_id,active,last_seen_at)
    VALUES (r->>'retailer_code',r->>'retailer_name',r->>'branch_name',r->>'city',
       r->>'city',r->>'municipality',r->>'region',r->>'address',r->>'source',
       r->>'inventory_id',locality,true,(r->>'source_checked_at')::date::timestamp AT TIME ZONE 'Europe/Sofia')
    ON CONFLICT (source,source_id) DO NOTHING;
  END LOOP;
END $inventory_batch$;"""


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    print(render_sql(load_batch(sys.argv[1], root / 'data/store_branches_seed.csv')))
