#!/usr/bin/env python3
"""Stage Burlex Sofia regular prices from the official public store table."""

import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
import re
from urllib.robotparser import RobotFileParser

import httpx

from collect_burlex_catalog import ENDPOINT, SOURCE

AGENT = "Spestovnik-Catalog-Review/0.3"
STORES = {
    "БУРЛЕКС БАНИШОРА": "ул. Иван Тургенев 2",
    "БУРЛЕКС ЛОЗЕНЕЦ": "ж.к. Лозенец, бул. Арсеналски 105",
}


def check_robots(client):
    response = client.get("https://burlex.bg/robots.txt")
    response.raise_for_status()
    robots = RobotFileParser()
    robots.parse(response.text.splitlines())
    if not all(robots.can_fetch(AGENT, url) for url in (SOURCE, ENDPOINT)):
        raise ValueError("Source disallows automated reads")


def collect(store, client):
    page = client.get(SOURCE)
    page.raise_for_status()
    wrap = re.search(r'<[^>]+class="burlex-wrap"[^>]*>', page.text)
    nonce = re.search(r'data-nonce="([^"]+)"', wrap[0]) if wrap else None
    if not nonce or not re.search(r"BGN_EUR_RATE\s*=\s*1\.95583", page.text):
        raise ValueError("Official price table markup or currency changed")
    response = client.get(
        ENDPOINT, params={
            "action": "burlex_prices_fetch", "_nonce": nonce[1], "settlement": "София",
            "store": store, "per_page": 500, "page": 1, "include_meta": 0,
        },
    )
    response.raise_for_status()
    data = response.json()
    if data.get("ok") is not True or data.get("page") != 1 or not data.get("rows"):
        raise ValueError("Official price table is empty or changed")
    observed = datetime.now(timezone.utc)
    rows = {}
    for row in data["rows"]:
        code = str(row["product_code"]).strip()
        if row["store"] != store or row["settlement"] != "София" or not code:
            raise ValueError("Store or product identity mismatch")
        try:
            bgn = Decimal(str(row["price"]).replace(",", "."))
        except InvalidOperation as exc:
            raise ValueError(f"Invalid Burlex price for {code}") from exc
        if not bgn.is_finite() or not 0 <= bgn <= 99999:
            raise ValueError(f"Invalid Burlex price for {code}")
        price = (bgn / Decimal("1.95583")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if price <= 0:
            continue
        if code in rows and rows[code]["price"] != str(price):
            raise ValueError(f"Conflicting Burlex prices for {code}")
        rows[code] = {"code": code, "price": str(price)}
    return rows.values(), observed


def render(store, rows, observed, *, summary=False):
    payload = json.dumps(list(rows), ensure_ascii=True)
    if "$burlex$" in payload:
        raise ValueError("Invalid source identifier delimiter")
    expires = observed + timedelta(hours=12)
    count = f"""(SELECT count(*) FROM verified) AS matched,
    (SELECT count(*) FROM verified v JOIN current_prices c
       ON c.product_id=v.product_id AND c.branch_id=v.branch_id
       WHERE c.verified_at <= now() AND (c.expires_at IS NULL OR c.expires_at > now())
         AND (c.observed_at >= '{observed.isoformat()}'::timestamptz OR c.source <> 'BURLEX_PUBLIC_TABLE')
    ) AS already_current, """ if summary else ""
    return f"""WITH source_rows AS (
  SELECT * FROM jsonb_to_recordset($burlex${payload}$burlex$::jsonb)
    AS o(code text, price numeric)
), verified AS (
  SELECT i.product_id, b.id AS branch_id, o.price
  FROM source_rows o JOIN grocery_catalog_identities i
    ON i.source='burlex-public-basket' AND i.source_product_code=o.code
  JOIN products p ON p.id=i.product_id AND p.active AND p.category_code='groceries'
  JOIN store_branches b ON b.active AND b.retailer_code='burlex'
    AND b.address='{STORES[store]}'
  JOIN inhabited_localities l ON l.id=b.locality_id AND l.name_bg='София'
    AND l.municipality='Столична' AND l.region='София (столица)'
  JOIN catalog_retailers r ON r.code=b.retailer_code AND r.active AND r.category_code=p.category_code
  WHERE now() >= '{observed.isoformat()}'::timestamptz AND now() < '{expires.isoformat()}'::timestamptz
), history AS (
  INSERT INTO price_observations
    (id,product_id,branch_id,price_eur,source,source_reference,verified,collected_at,valid_until)
  SELECT md5(concat_ws('|','burlex-public-table',product_id,branch_id,'{observed.isoformat()}'))::uuid,
    product_id,branch_id,price,'BURLEX_PUBLIC_TABLE','{SOURCE}',true,
    '{observed.isoformat()}','{expires.isoformat()}'
  FROM verified ON CONFLICT (id) DO NOTHING
), updated AS (
  INSERT INTO current_prices
    (id,product_id,branch_id,price_eur,source,observed_at,verified_at,expires_at)
  SELECT gen_random_uuid(), product_id,branch_id,price,'BURLEX_PUBLIC_TABLE',
    '{observed.isoformat()}',now(),'{expires.isoformat()}'
  FROM verified
  ON CONFLICT (product_id,branch_id) DO UPDATE SET
    price_eur=excluded.price_eur, observed_at=excluded.observed_at,
    verified_at=excluded.verified_at, expires_at=excluded.expires_at
  WHERE current_prices.observed_at < excluded.observed_at
    AND (current_prices.source=excluded.source OR current_prices.expires_at <= now())
  RETURNING 1
)
SELECT {count}count(*) AS published FROM updated;"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", choices=STORES, required=True)
    args = parser.parse_args()
    with httpx.Client(timeout=25, follow_redirects=False, headers={"User-Agent": AGENT}) as client:
        check_robots(client)
        rows, observed = collect(args.store, client)
        print(render(args.store, rows, observed))
