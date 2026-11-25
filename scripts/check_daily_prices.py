#!/usr/bin/env python3
"""Check approved public price sources and emit a count and freshness report."""

import argparse
from datetime import date, datetime, timedelta, timezone
import json
import re
from zoneinfo import ZoneInfo

import httpx

import collect_burlex_branch_prices as burlex
import collect_karai_fuel_offers as karai
import collect_techmart_offers as techmart

TECHMART_SKUS = ("46637", "43832", "43957", "46638", "45769")
SOURCE_ERRORS = (httpx.HTTPError, ValueError, TypeError, KeyError, AttributeError)


def check(category, client):
    if category == "groceries":
        burlex.check_robots(client)
        results = []
        for store in burlex.STORES:
            rows, observed = burlex.collect(store, client)
            if not rows:
                raise ValueError("Burlex returned no usable prices")
            results.append({"store": store, "count": len(rows), "observed_at": observed.isoformat()})
        return {"source": burlex.SOURCE, "checks": results}
    if category == "technology":
        failed = []
        rows = list(techmart.collect(TECHMART_SKUS, client, on_failed_sku=failed.append))
        if not rows:
            raise ValueError("Techmart returned no usable offers")
        return {
            "source": techmart.BASE, "count": len(rows), "requested": len(TECHMART_SKUS),
            "failed_skus": failed,
        }
    response = client.get(karai.API)
    response.raise_for_status()
    rows, observed = karai.offers(response.json(), datetime.now(timezone.utc))
    return {
        "source": karai.ATTRIBUTION, "count": len(rows), "observed_at": observed.isoformat(),
        "chains": len({row["retailer"] for row in rows}),
        "fuel_types": sorted({row["fuel"] for row in rows}),
    }


OPEN_DATA = "https://kolkostruva.bg/opendata"


def grocery_archive(client, today):
    page = client.get(OPEN_DATA)
    page.raise_for_status()
    dates = {
        date.fromisoformat(value) for value in re.findall(
            r'href="/opendata_files/(\d{4}-\d{2}-\d{2})\.zip"', page.text,
        )
    }
    recent = [day for day in dates if today - timedelta(days=2) <= day <= today]
    if not recent:
        raise ValueError("No recent grocery archive")
    latest = max(recent)
    url = f"https://kolkostruva.bg/opendata_files/{latest}.zip"
    archive = client.head(url)
    archive.raise_for_status()
    if "zip" not in archive.headers.get("content-type", "").lower():
        raise ValueError("Unexpected archive format")
    return {"source": OPEN_DATA, "archive_date": latest.isoformat(), "status": "available"}


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
    with httpx.Client(timeout=25, follow_redirects=False, headers={"User-Agent": burlex.AGENT}) as client:
        result = attempt(lambda: check(args.category, client))
        if args.category == "groceries":
            result["alternate_archive"] = attempt(
                lambda: grocery_archive(client, datetime.now(ZoneInfo("Europe/Sofia")).date())
            )
    print(json.dumps({
        "category": args.category, "checked_at": datetime.now(timezone.utc).isoformat(), **result,
    }, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)
