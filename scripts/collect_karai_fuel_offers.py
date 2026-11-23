#!/usr/bin/env python3
"""Render indicative chain offers from the public KARAI Fuel Index (CC BY 4.0)."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
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
        data["source"] != "live"
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
            price = Decimal(str(amount))
            if not price.is_finite() or not 0 < price <= 10 or price.as_tuple().exponent < -2:
                raise ValueError(f"Invalid source price for {retailer}/{fuel}")
            rows.append({"retailer": retailer, "fuel": fuel, "price": str(price)})
    if not rows:
        raise ValueError("No supported chain prices")
    return rows, observed


def render(rows, observed):
    payload = json.dumps(rows)
    expires = observed + timedelta(hours=24)
    return f"""WITH source_rows AS (
  SELECT * FROM jsonb_to_recordset($karai${payload}$karai$::jsonb)
    AS o(retailer text, fuel text, price numeric)
)
INSERT INTO national_offers
  (id,product_id,retailer_code,price_eur,source_reference,observed_at,verified_at,verified_by,valid_until)
SELECT md5(concat_ws('|','karai-chain-index',p.id,o.retailer,'{observed.isoformat()}'))::uuid,
  p.id,r.code,o.price,'{ATTRIBUTION}',
  '{observed.isoformat()}',now(),'karai-chain-index','{expires.isoformat()}'
FROM source_rows o JOIN products p ON p.category_code='fuel' AND p.active AND p.variant=o.fuel
JOIN catalog_retailers r ON r.code=o.retailer AND r.active AND r.category_code=p.category_code
WHERE current_timestamp >= '{observed.isoformat()}'::timestamptz
  AND current_timestamp < '{expires.isoformat()}'::timestamptz
ON CONFLICT (id) DO NOTHING RETURNING product_id, retailer_code, price_eur;"""


if __name__ == "__main__":
    response = httpx.get(API, timeout=15, follow_redirects=False)
    response.raise_for_status()
    print(render(*offers(response.json(), datetime.now(timezone.utc))))
