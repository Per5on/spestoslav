#!/usr/bin/env python3
"""Read-only validation of seed provenance, duplicates and canonical locality links."""

import csv
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

DATA = Path(__file__).resolve().parents[1] / "data"


def read(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def identity(city, municipality, region):
    return tuple(value.strip().casefold() for value in (city, municipality, region))


def validate():
    seed = read("store_branches_seed.csv")
    registry = read("retailer_source_registry.csv")
    locality_rows = read("bulgaria_localities.csv")
    retailers = {row["retailer_code"]: row for row in registry}
    if len(retailers) != len(registry):
        raise ValueError("Duplicate retailer code")
    localities = {
        identity(
            row["settlement_name_bg"],
            row["municipality_name_source"].split(" / ")[0],
            row["oblast_name_source"].split(" / ")[0],
        )
        for row in locality_rows
    }
    seen = set()
    for line, row in enumerate(seed, 2):
        locality = identity(row["city"], row["municipality"], row["region"])
        key = (row["retailer_code"], locality, row["address"].strip().casefold())
        retailer = retailers.get(row["retailer_code"])
        if key in seen or not row["address"].strip():
            raise ValueError(f"Seed line {line}: duplicate or missing address")
        seen.add(key)
        if locality not in localities:
            raise ValueError(
                f"Seed line {line}: unmatched canonical locality {locality}"
            )
        if not retailer or retailer["category_code"] != row["category_code"]:
            raise ValueError(f"Seed line {line}: missing retailer/category mismatch")
        source = urlsplit(row["source_url"])
        if source.scheme != "https" or not source.hostname or not row["source"]:
            raise ValueError(f"Seed line {line}: missing HTTPS source/provenance")
        if date.fromisoformat(row["source_checked_at"]) > date.today():
            raise ValueError(f"Seed line {line}: future verification date")
    return {
        "seed_branches": len(seed),
        "retailers_in_registry": len(retailers),
        "represented_retailers": len({row["retailer_code"] for row in seed}),
        "canonical_localities": len(localities),
        "duplicate_branches": 0,
        "unmatched_localities": 0,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False))
