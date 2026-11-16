#!/usr/bin/env python3
"""Collect public catalogue metadata into a new review file, never publish prices.

Uses the same public table request as burlex.bg/kolkostruva/. No API contract or
reuse licence is implied. Stops on errors; missing records never mean closure.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
import httpx

SOURCE = "https://burlex.bg/kolkostruva/"
ENDPOINT = "https://burlex.bg/wp-admin/admin-ajax.php"


def collect(stores, max_pages, client, pause=time.sleep):
    response = client.get(SOURCE)
    response.raise_for_status()
    found = re.search(r'<[^>]+class="burlex-wrap"[^>]*>', response.text)
    if not found:
        raise ValueError("Public catalogue markup changed; review parser")
    nonce = re.search(r'data-nonce="([^"]+)"', found[0])
    if not nonce:
        raise ValueError("Public table token missing; stop without bypass")
    rows = {}
    conflicts = []
    truncated = []
    for store in stores:
        for page in range(1, max_pages + 1):
            pause(1)
            result = client.get(
                ENDPOINT,
                params={
                    "action": "burlex_prices_fetch",
                    "_nonce": nonce[1],
                    "page": page,
                    "per_page": 500,
                    "store": store,
                    "include_meta": 0,
                },
            )
            result.raise_for_status()
            data = result.json()
            if (
                not isinstance(data, dict)
                or data.get("ok") is not True
                or not isinstance(data.get("rows"), list)
            ):
                raise ValueError("Unexpected public table response")
            if data.get("page") != page or not 1 <= data.get("per_page", 0) <= 500:
                raise ValueError("Unexpected pagination")
            for row in data["rows"]:
                code = str(row.get("product_code", "")).strip()
                name = row.get("product_name", "").strip()
                category = row.get("category", "").strip()
                if not code or not name or not category:
                    raise ValueError("Missing identity fields")
                # Deliberately omit amounts, branch mapping and retailer-specific currency assumptions.
                clean = {
                    "source_product_code": code,
                    "name": name,
                    "source_category": category,
                }
                if code in rows and rows[code] != clean:
                    conflicts.append(code)
                else:
                    rows[code] = clean
            if page * data["per_page"] >= data.get("total", 0):
                break
        else:
            truncated.append(store)
    if not rows:
        raise ValueError("Empty import quarantined; preserve previous catalogue")
    if conflicts:
        raise ValueError("Conflicting retailer identities require review")
    return {
        "source_url": SOURCE,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "requires_review": True,
        "prices_imported": False,
        "barcodes_verified": 0,
        "stores_requested": stores,
        "truncated_stores": truncated,
        "products": sorted(rows.values(), key=lambda r: r["source_product_code"]),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store",
        action="append",
        required=True,
        help="Exact store name from the public source",
    )
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.max_pages <= 10:
        parser.error("--max-pages must be 1–10")
    if args.output.exists():
        parser.error("Output already exists; preserve previous batches")
    with httpx.Client(
        timeout=45,
        headers={"User-Agent": "Spestovnik-Catalog-Review/0.3"},
        follow_redirects=False,
    ) as client:
        result = collect(args.store, args.max_pages, client)
    with args.output.open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(
        "Staged",
        len(result["products"]),
        "identities for review; no database/price changes",
    )
