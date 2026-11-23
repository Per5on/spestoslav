#!/usr/bin/env python3
"""Collect reviewed price feeds into a durable cache and optionally publish them."""

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sqlite3

import httpx
import psycopg

from check_daily_prices import TECHMART_SKUS, attempt
import collect_burlex_branch_prices as burlex
import collect_karai_fuel_offers as karai
import collect_techmart_offers as techmart

CATEGORIES = ("groceries", "technology", "fuel")
DATA = Path(__file__).resolve().parents[1] / "data"
SCHEMA = """
CREATE TABLE IF NOT EXISTS price_observations (
    category TEXT NOT NULL, source_url TEXT NOT NULL, retailer TEXT NOT NULL,
    locality TEXT NOT NULL, store_address TEXT NOT NULL, product_key TEXT NOT NULL,
    price_eur TEXT NOT NULL, observed_at TEXT NOT NULL, valid_until TEXT NOT NULL,
    price_scope TEXT NOT NULL,
    PRIMARY KEY (category, retailer, locality, store_address, product_key, observed_at)
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS price_validity ON price_observations(category, valid_until);
CREATE VIEW IF NOT EXISTS unexpired_observations AS
    SELECT * FROM price_observations
    WHERE julianday(observed_at) <= julianday('now')
      AND julianday(valid_until) > julianday('now');
"""


@dataclass
class Batch:
    category: str
    rows: list
    statement: str


def collect_batches(category, client, failed_sku):
    if category == "groceries":
        burlex.check_robots(client)
        for store, address in burlex.STORES.items():
            rows, observed = burlex.collect(store, client)
            rows = list(rows)
            if not rows:
                raise ValueError("Burlex returned no usable prices")
            expiry = observed + timedelta(hours=12)
            yield Batch(category, [
                (category, burlex.SOURCE, "burlex", "София", address, row["code"],
                 row["price"], observed.isoformat(), expiry.isoformat(), "BRANCH")
                for row in rows
            ], burlex.render(store, rows, observed, summary=True))
    elif category == "technology":
        rows = list(techmart.collect(TECHMART_SKUS, client, on_failed_sku=failed_sku))
        yield Batch(category, [
            (category, row["url"], "techmart", "", "", row["code"], row["price"],
             row["observed"], row["expires"], "NATIONAL_ONLINE")
            for row in rows
        ], techmart.render(rows, summary=True))
    else:
        response = client.get(karai.API)
        response.raise_for_status()
        rows, observed = karai.offers(response.json(), datetime.now(timezone.utc))
        expiry = observed + timedelta(hours=24)
        yield Batch(category, [
            (category, karai.ATTRIBUTION, row["retailer"], "", "", row["fuel"], row["price"],
             observed.isoformat(), expiry.isoformat(), "NATIONAL_ONLINE")
            for row in rows
        ], karai.render(rows, observed, summary=True))


def cache_batches(path, batches):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as cache:
        cache.executescript(SCHEMA)
        cache.executemany(
            """INSERT INTO price_observations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT DO NOTHING""",
            (row for batch in batches for row in batch.rows),
        )


def add_reference_data(path):
    products = []
    for category, file in (
        ("groceries", "groceries/essential-1000.json"),
        ("technology", "technology/essential-1000.json"),
        ("fuel", "fuel/types.json"),
    ):
        for row in json.loads((DATA / file).read_text())["products"]:
            products.append((
                category, row.get("source_product_code") or row["code"],
                row.get("name") or row["name_bg"],
            ))
    with (DATA / "store_branches_seed.csv").open(newline="") as stream:
        branches = [
            tuple(row[key] for key in (
                "category_code", "retailer_code", "branch_name", "city", "municipality",
                "region", "address", "source_url", "source_checked_at",
            ))
            for row in csv.DictReader(stream)
        ]
    with sqlite3.connect(path) as cache:
        cache.executescript("""
            CREATE TABLE IF NOT EXISTS catalogue (
                category TEXT, product_key TEXT, product_name TEXT,
                PRIMARY KEY (category, product_key)
            ) WITHOUT ROWID;
            CREATE TABLE IF NOT EXISTS directory (
                category TEXT, retailer TEXT, branch_name TEXT, locality TEXT,
                municipality TEXT, region TEXT, address TEXT, source_url TEXT, source_checked_at TEXT,
                PRIMARY KEY (category, retailer, locality, municipality, region, address, branch_name)
            ) WITHOUT ROWID;
        """)
        cache.executemany("INSERT OR IGNORE INTO catalogue VALUES (?, ?, ?)", products)
        cache.executemany("INSERT OR IGNORE INTO directory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", branches)


def publish_batches(database_url, batches):
    counts = []
    with psycopg.connect(database_url, connect_timeout=8) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout = '40s'")
            cursor.execute("SET LOCAL lock_timeout = '5s'")
            for batch in batches:
                cursor.execute(batch.statement)
                metrics = cursor.fetchone()
                if batch.category == "groceries":
                    matched, current, written = metrics
                else:
                    matched, written = metrics
                    # Matched rows use the same deterministic observation ID on replay.
                    current = matched - written
                if not matched or current + written == 0:
                    raise ValueError("No fresh catalogue matches or active published prices")
                counts.append({"matched": matched, "already_current": current, "published": written})
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", choices=CATEGORIES, action="append")
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--catalogue-base", action="store_true")
    parser.add_argument("--sql-dir", type=Path)
    args = parser.parse_args()
    categories = tuple(dict.fromkeys(args.category or CATEGORIES))
    approved = set(os.getenv("PRICE_REUSE_APPROVED_CATEGORIES", "").split())
    database_url = os.getenv("PRICE_PUBLISH_DATABASE_URL")
    if args.apply and (not set(categories) <= approved or not database_url):
        parser.error("Provide a dedicated publisher database URL and approve reuse for every selected category")

    report = {}
    with httpx.Client(timeout=25, follow_redirects=False, headers={"User-Agent": burlex.AGENT}) as client:
        for category in categories:
            def refresh(category=category):
                failed = []
                batches = list(collect_batches(category, client, failed.append))
                cache_batches(args.cache, batches)
                if args.sql_dir:
                    args.sql_dir.mkdir(parents=True, exist_ok=True)
                    for i, batch in enumerate(batches, 1):
                        (args.sql_dir / f"{category}-{i}.sql").write_text(batch.statement + "\n")
                written = publish_batches(database_url, batches) if args.apply else None
                return {
                    "collected": [len(batch.rows) for batch in batches],
                    "publication": written, "failed_skus": failed,
                }

            try:
                report[category] = attempt(refresh)
            except (sqlite3.Error, psycopg.Error) as exc:
                report[category] = {"ok": False, "error": type(exc).__name__}
    if args.catalogue_base and args.cache.is_file():
        add_reference_data(args.cache)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(item["ok"] for item in report.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
