#!/usr/bin/env python3
"""Check published prices and actual multi-retailer comparison from the public API."""

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
import json

import httpx

PRODUCT_CATEGORIES = ("groceries", "technology")


def read(client, path, **params):
    try:
        response = client.get(path, params=params)
    except httpx.TransportError:
        response = client.get(path, params=params)
    response.raise_for_status()
    return response.json()


def directory(client):
    offset = 0
    for _ in range(100):
        page = read(client, "/api/v1/merchant-directory", limit=200, offset=offset)
        yield from page["branches"]
        next_offset = page["next_offset"]
        if next_offset is None:
            return
        if next_offset <= offset:
            raise ValueError("Merchant directory pagination stalled")
        offset = next_offset
    raise ValueError("Merchant directory capacity exceeded")


def offers(client, category):
    for offset in range(0, 10000, 100):
        page = read(client, "/api/v1/national-offers", category_code=category, limit=100, offset=offset)
        yield from page
        if len(page) < 100:
            return
    raise ValueError("Online offer capacity exceeded")


def verify_category(client, category, branches, now):
    towns_by_retailer = defaultdict(set)
    towns = {}
    for branch in branches:
        if branch["category_code"] != category:
            continue
        town_id = branch["locality_id"]
        towns[town_id] = branch["locality_name"]
        towns_by_retailer[branch["retailer_code"]].add(town_id)

    active_by_product = defaultdict(dict)
    for offer in offers(client, category):
        if offer["price_scope"] != "NATIONAL_ONLINE":
            continue
        amount = Decimal(offer["price_eur"])
        if amount.is_finite() and amount > 0 and datetime.fromisoformat(offer["valid_until"]) > now:
            active_by_product[offer["product_id"]][offer["retailer_code"]] = amount

    comparable_products = 0
    comparable_towns = set()
    sample = None
    for product, prices in sorted(active_by_product.items()):
        eligible = defaultdict(dict)
        for retailer, amount in prices.items():
            for town in towns_by_retailer[retailer]:
                eligible[town][retailer] = amount
        comparison_towns = {town for town, quotes in eligible.items() if len(quotes) >= 2}
        if not comparison_towns:
            continue
        comparable_products += 1
        comparable_towns.update(comparison_towns)
        if sample is None:
            town = min(comparison_towns, key=lambda town: (towns[town], town))
            actual = {
                row["retailer_code"]: Decimal(row["price_eur"])
                for row in read(client, "/api/v1/national-offers", category_code=category,
                                product_id=product, locality_id=town, limit=100)
                if row["price_scope"] == "NATIONAL_ONLINE"
            }
            sample = {
                "locality": towns[town], "product_id": product,
                "retailer_prices": {code: str(amount) for code, amount in sorted(actual.items())},
                "matches_national_amounts": actual == eligible[town],
            }

    return {
        "ok": bool(sample and sample["matches_national_amounts"]),
        "active_offers": sum(map(len, active_by_product.values())),
        "comparable_products": comparable_products,
        "comparable_localities": len(comparable_towns),
        "sample": sample,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("api_base")
    args = parser.parse_args()
    with httpx.Client(base_url=args.api_base, timeout=30, follow_redirects=False) as client:
        errors = (httpx.HTTPError, KeyError, TypeError, ValueError, ArithmeticError)
        try:
            branches = list(directory(client))
        except errors as exc:
            result = {"directory": {"ok": False, "error": type(exc).__name__}}
        else:
            now = datetime.now(timezone.utc)
            result = {}
            for category in PRODUCT_CATEGORIES:
                try:
                    result[category] = verify_category(client, category, branches, now)
                except errors as exc:
                    result[category] = {"ok": False, "error": type(exc).__name__}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if all(item["ok"] for item in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
