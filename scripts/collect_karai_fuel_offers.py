#!/usr/bin/env python3
"""Render indicative chain offers from the public KARAI Fuel Index (CC BY 4.0)."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
from zoneinfo import ZoneInfo

import httpx

API = "https://karai.bg/api/fuel-prices"
ATTRIBUTION = "https://karai.bg/fuel-prices/indeks"
RETAILERS = frozenset(("eko", "lukoil", "omv", "petrol", "rompetrol", "shell"))
FUELS = {"a95": "petrol", "diesel": "diesel", "lpg": "lpg"}


def offers(data, now):
    sofia = ZoneInfo("Europe/Sofia")
    source_date = date.fromisoformat(data["date"])
    observed = datetime.fromisoformat(data["fetchedAt"])
    if (
        observed.utcoffset() is None
        or data["source"] != "live"
        or data.get("currency", "EUR") != "EUR"
        or not now - timedelta(hours=24) <= observed <= now
        or source_date != observed.astimezone(sofia).date()
    ):
        raise ValueError("KARAI fuel source is stale, future-dated or a fallback")
    rows = []
    seen = set()
    for provider in data["providers"]:
        retailer = provider["logoKey"]
        if retailer not in RETAILERS:
            continue
        if retailer in seen:
            raise ValueError(f"Duplicate provider {retailer}")
        seen.add(retailer)
        for field, fuel in FUELS.items():
            amount = provider[field]
            if amount is None:
                continue
            try:
                price = Decimal(str(amount))
            except InvalidOperation as exc:
                raise ValueError(f"Invalid source price for {retailer}/{fuel}") from exc
            if not price.is_finite() or not 0 < price <= 10 or price.as_tuple().exponent < -2:
                raise ValueError(f"Invalid source price for {retailer}/{fuel}")
            rows.append({"retailer": retailer, "fuel": fuel, "price": str(price)})
    if not rows:
        raise ValueError("No supported chain prices")
    return rows, observed


def render(rows, observed, *, summary=False):
    if not rows:
        raise ValueError("No supported chain prices")
    payload = json.dumps([
        {**row, "source": row.get("source", ATTRIBUTION), "publisher": row.get("publisher", "karai-chain-index"),
         "observed": row.get("observed", observed.isoformat()), "expires": row.get("expires", (observed + timedelta(hours=24)).isoformat())}
        for row in rows
    ])
    if "$karai$" in payload:
        raise ValueError("Invalid source identifier delimiter")
    statement = f"""WITH source_rows AS (
  SELECT * FROM jsonb_to_recordset($karai${payload}$karai$::jsonb)
    AS o(retailer text, fuel text, price numeric, source text, publisher text, observed timestamptz, expires timestamptz)
), matched AS (
SELECT md5(concat_ws('|',o.publisher,p.id,o.retailer,o.observed::text))::uuid AS id,
  p.id AS product_id,r.code,o.price,o.source,o.publisher,o.observed,o.expires
FROM source_rows o JOIN products p ON p.category_code='fuel' AND p.active AND p.variant=o.fuel
JOIN catalog_retailers r ON r.code=o.retailer AND r.active AND r.category_code=p.category_code
WHERE o.observed <= current_timestamp AND current_timestamp < o.expires
), inserted AS (
  INSERT INTO national_offers
    (id,product_id,retailer_code,price_eur,source_reference,observed_at,verified_at,verified_by,valid_until)
  SELECT id,product_id,code,price,source,observed,now(),publisher,expires
  FROM matched ON CONFLICT (id) DO NOTHING RETURNING product_id, retailer_code, price_eur
) """
    return statement + (
        "SELECT (SELECT count(*) FROM matched) AS matched, count(*) AS published FROM inserted;"
        if summary else "SELECT product_id, retailer_code, price_eur FROM inserted;"
    )


if __name__ == "__main__":
    response = httpx.get(API, timeout=15, follow_redirects=False)
    response.raise_for_status()
    print(render(*offers(response.json(), datetime.now(timezone.utc))))
