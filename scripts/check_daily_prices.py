#!/usr/bin/env python3
"""Check approved public price sources and emit a count and freshness report."""

import argparse
from datetime import datetime, timezone
import json

import httpx

import collect_karai_fuel_offers as karai
import collect_techmart_offers as techmart
import collect_storefront_offers as storefront

TECHMART_SKUS = ("46637", "43832", "43957", "46638", "45769")
SOURCE_ERRORS = (httpx.HTTPError, ValueError, TypeError, KeyError, AttributeError)


def product_offers(category, client, failed_sku):
    if category == "groceries":
        yield from storefront.collect("t_market", client, failed_sku)
        yield from storefront.collect("bulmag", client, failed_sku)
    else:
        try:
            for row in techmart.collect(TECHMART_SKUS, client, on_failed_sku=failed_sku):
                yield {**row, "retailer": "techmart"}
        except httpx.HTTPError:
            for sku in TECHMART_SKUS:
                failed_sku(sku)
        yield from storefront.collect("ardes", client, failed_sku)


def check(category, client):
    if category in ("groceries", "technology"):
        failed = []
        rows = list(product_offers(category, client, failed.append))
        if not rows:
            raise ValueError("No usable online offers")
        return {
            "retailers": sorted({row["retailer"] for row in rows}),
            "count": len(rows), "failed_skus": failed,
        }
    response = client.get(karai.API)
    response.raise_for_status()
    rows, observed = karai.offers(response.json(), datetime.now(timezone.utc))
    return {
        "source": karai.ATTRIBUTION, "count": len(rows), "observed_at": observed.isoformat(),
        "chains": len({row["retailer"] for row in rows}),
        "fuel_types": sorted({row["fuel"] for row in rows}),
    }


def attempt(operation):
    try:
        return {"ok": True, **operation()}
    except SOURCE_ERRORS as exc:
        # HTTP errors contain request URLs that may include a public frontend nonce.
        return {"ok": False, "error": type(exc).__name__}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("category", choices=("groceries", "technology", "fuel"))
    args = parser.parse_args()
    with httpx.Client(timeout=25, follow_redirects=False, headers={"User-Agent": techmart.AGENT}) as client:
        result = attempt(lambda: check(args.category, client))
    print(json.dumps({
        "category": args.category, "checked_at": datetime.now(timezone.utc).isoformat(), **result,
    }, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)
