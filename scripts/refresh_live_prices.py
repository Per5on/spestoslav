#!/usr/bin/env python3
"""Collect reviewed price feeds into a durable cache and optionally publish them."""

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
import json
import os
from pathlib import Path
import sqlite3

import httpx
import psycopg

from check_daily_prices import attempt, product_offers
import collect_karai_fuel_offers as karai
import collect_techmart_offers as techmart

CATEGORIES = ("groceries", "technology", "fuel")
DATA = Path(__file__).resolve().parents[1] / "data"
TABLE = """CREATE TABLE IF NOT EXISTS price_observations (
    category TEXT NOT NULL, source_url TEXT NOT NULL, retailer TEXT NOT NULL,
    locality TEXT NOT NULL, store_address TEXT NOT NULL, product_key TEXT NOT NULL,
    price_eur TEXT NOT NULL, observed_at TEXT NOT NULL, valid_until TEXT NOT NULL,
    price_scope TEXT NOT NULL,
    PRIMARY KEY (category, retailer, locality, store_address, product_key, observed_at, source_url, price_scope)
) WITHOUT ROWID"""
PRICE_INDEX = "CREATE INDEX IF NOT EXISTS price_validity ON price_observations(category, valid_until)"
UNEXPIRED_VIEW = """CREATE VIEW IF NOT EXISTS unexpired_observations AS
    SELECT * FROM price_observations
    WHERE julianday(observed_at) <= julianday('now')
      AND julianday(valid_until) > julianday('now')"""


@dataclass
class Batch:
    category: str
    rows: list
    statement: str
    checks: dict | None = None


def combine_fuel_sources(feed, secondary, now):
    """Use a licensed Fuelo chain export and use KARAI only for missing pairs."""
    observed = datetime.fromisoformat(feed["observed_at"])
    if feed["currency"] != "EUR" or feed["unit"] != "L" or observed.utcoffset() is None or not (
        now - timedelta(hours=24) < observed <= now
    ):
        raise ValueError("Invalid or expired Fuelo chain export")
    date = observed.astimezone(ZoneInfo("Europe/Sofia")).date()
    source = f"https://bg.fuelo.net/prices/date/{date}"
    backup = {(row["retailer"], row["fuel"]): row for row in secondary}
    primary = {}
    checks = {"matched": 0, "different": 0, "no_secondary": 0}
    allowed_fuels = {*karai.FUELS.values(), "petrol98", "dieselPlus"}
    if not feed["prices"]:
        raise ValueError("Fuelo chain export has no prices")
    for row in feed["prices"]:
        key = (row["retailer"], row["fuel"])
        if key in primary or key[0] not in karai.RETAILERS or key[1] not in allowed_fuels:
            raise ValueError("Invalid or duplicate Fuelo chain and fuel")
        try:
            amount = Decimal(str(row["price"]))
        except InvalidOperation as exc:
            raise ValueError("Invalid Fuelo price") from exc
        if not amount.is_finite() or not 0 < amount <= 10 or amount.as_tuple().exponent < -2:
            raise ValueError("Invalid Fuelo price")
        other = backup.pop(key, None)
        status = "no_secondary" if other is None else "matched" if amount == Decimal(other["price"]) else "different"
        checks[status] += 1
        primary[key] = {
            "retailer": key[0], "fuel": key[1], "price": str(amount), "source": source,
            "observed": observed.isoformat(), "expires": (observed + timedelta(hours=24)).isoformat(),
            "publisher": "fuelo-chain-reference",
        }
    return [*primary.values(), *backup.values()], checks


def render_product_offers(category, rows):
    identity_table, catalogue_source = {
        "groceries": ("grocery_catalog_identities", "burlex-public-basket"),
        "technology": ("technology_catalog_identities", "TECHMART_PUBLIC_CATALOG"),
    }[category]
    payload = json.dumps(rows)
    if not rows or "$storefront$" in payload:
        raise ValueError("No usable online offers or invalid SQL delimiter")
    return f"""WITH offers AS (
  SELECT * FROM jsonb_to_recordset($storefront${payload}$storefront$::jsonb)
    AS o(code text, retailer text, url text, price numeric, observed timestamptz, expires timestamptz)
), matched AS (
  SELECT md5(concat_ws('|',r.code,'online',p.id,o.observed::text))::uuid AS id,
    p.id AS product_id,r.code,o.price,o.url,o.observed,o.expires
  FROM offers o JOIN {identity_table} i
    ON i.source='{catalogue_source}' AND i.source_product_code=o.code
    AND (o.retailer <> 'techmart' OR i.source_url=o.url)
  JOIN products p ON p.id=i.product_id AND p.active AND p.category_code='{category}'
  JOIN catalog_retailers r ON r.code=o.retailer AND r.active AND r.category_code=p.category_code
  WHERE o.observed <= now() AND now() < o.expires
), inserted AS (
  INSERT INTO national_offers
    (id,product_id,retailer_code,price_eur,source_reference,observed_at,verified_at,verified_by,valid_until)
  SELECT id,product_id,code,price,url,observed,now(),code || '-public-jsonld',expires
  FROM matched ON CONFLICT (id) DO NOTHING RETURNING 1
)
SELECT (SELECT count(*) FROM matched) AS matched, count(*) AS published FROM inserted;"""


def collect_batches(category, client, failed_sku, fuelo_feed=None):
    if category in ("groceries", "technology"):
        rows = list(product_offers(category, client, failed_sku))
        yield Batch(category, [
            (category, row["url"], row["retailer"], "", "", row["code"], row["price"],
             row["observed"], row["expires"], "NATIONAL_ONLINE")
            for row in rows
        ], render_product_offers(category, rows))
    else:
        secondary = attempt(lambda: read_karai(client))
        now = datetime.now(timezone.utc)
        if not secondary["ok"] and fuelo_feed is None:
            raise ValueError("No usable fuel source")
        rows = secondary.get("rows", [])
        observed = secondary.get("observed", now)
        checks = None
        if fuelo_feed is not None:
            rows, checks = combine_fuel_sources(fuelo_feed, rows, now)
        expiry = observed + timedelta(hours=24)
        yield Batch(category, [
            (category, row.get("source", karai.ATTRIBUTION), row["retailer"], "", "", row["fuel"], row["price"],
             row.get("observed", observed.isoformat()), row.get("expires", expiry.isoformat()), "NATIONAL_ONLINE")
            for row in rows
        ], karai.render(rows, observed, summary=True), checks=checks)


def read_karai(client):
    response = client.get(karai.API)
    response.raise_for_status()
    rows, observed = karai.offers(response.json(), datetime.now(timezone.utc))
    return {"rows": rows, "observed": observed}


def cache_batches(path, batches):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as cache:
        cache.execute("BEGIN IMMEDIATE")
        columns = cache.execute("PRAGMA table_info(price_observations)").fetchall()
        old_key = columns and not any(row[1] == "source_url" and row[5] for row in columns)
        if old_key:
            cache.execute("DROP VIEW IF EXISTS unexpired_observations")
            cache.execute("ALTER TABLE price_observations RENAME TO previous_price_observations")
        cache.execute(TABLE)
        if old_key:
            cache.execute("INSERT INTO price_observations SELECT * FROM previous_price_observations")
            cache.execute("DROP TABLE previous_price_observations")
        cache.execute(PRICE_INDEX)
        cache.execute(UNEXPIRED_VIEW)
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
                matched, written = cursor.fetchone()
                current = matched - written
                if not matched or current + written == 0:
                    raise ValueError("No fresh catalogue matches or active published prices")
                counts.append({"matched": matched, "already_current": current, "published": written})
    return counts


def check_published_feed(client, api_base, category, batches):
    expected = {
        (row[2], row[1], Decimal(row[6]), datetime.fromisoformat(row[7]))
        for batch in batches for row in batch.rows if row[9] == "NATIONAL_ONLINE"
    }
    total = len(expected)
    if not total:
        raise ValueError("No online offers to verify")
    for offset in range(0, 10000, 100):
        response = client.get(
            api_base.rstrip("/") + "/api/v1/national-offers",
            params={"category_code": category, "limit": 100, "offset": offset},
        )
        response.raise_for_status()
        rows = response.json()
        expected.difference_update(
            (row["retailer_code"], row["source_reference"], Decimal(row["price_eur"]),
             datetime.fromisoformat(row["observed_at"]))
            for row in rows if row["price_scope"] == "NATIONAL_ONLINE"
        )
        if not expected:
            return {"expected": total, "served": total}
        if len(rows) < 100:
            break
    return {"ok": False, "expected": total, "served": total - len(expected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", choices=CATEGORIES, action="append")
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--catalogue-base", action="store_true")
    parser.add_argument("--sql-dir", type=Path)
    parser.add_argument("--verify-api", metavar="BASE_URL", help="Check published grocery and technology offers through the API")
    parser.add_argument("--fuelo-feed", type=Path, help="Licensed Fuelo chain averages JSON export")
    args = parser.parse_args()
    categories = tuple(dict.fromkeys(args.category or CATEGORIES))
    approved = set(os.getenv("PRICE_REUSE_APPROVED_CATEGORIES", "").split())
    database_url = os.getenv("PRICE_PUBLISH_DATABASE_URL")
    if args.apply and (not set(categories) <= approved or not database_url):
        parser.error("Provide a dedicated publisher database URL and approve reuse for every selected category")

    if args.verify_api:
        api_url = urlsplit(args.verify_api)
        if not args.apply or api_url.scheme not in ("http", "https") or not api_url.hostname or (
            api_url.scheme != "https" and api_url.hostname not in ("localhost", "127.0.0.1", "::1")
        ) or api_url.username or api_url.password or api_url.query or api_url.fragment:
            parser.error("API verification needs --apply and an HTTPS or loopback API base URL")

    if args.fuelo_feed and ("fuel" not in categories or (
        args.apply and os.getenv("PRICE_REUSE_FUELO_APPROVED") != "1"
    )):
        parser.error("Fuelo publication requires the fuel category and separate Fuelo reuse approval")
    feed = json.loads(args.fuelo_feed.read_text()) if args.fuelo_feed else None

    report = {}
    with httpx.Client(timeout=25, follow_redirects=False, headers={"User-Agent": techmart.AGENT}) as client:
        for category in categories:
            def refresh(category=category):
                failed = []
                batches = list(collect_batches(category, client, failed.append, feed))
                cache_batches(args.cache, batches)
                if args.sql_dir:
                    args.sql_dir.mkdir(parents=True, exist_ok=True)
                    for i, batch in enumerate(batches, 1):
                        (args.sql_dir / f"{category}-{i}.sql").write_text(batch.statement + "\n")
                written = publish_batches(database_url, batches) if args.apply else None
                api_check = None
                if args.verify_api and category != "fuel":
                    api_check = attempt(lambda: check_published_feed(client, args.verify_api, category, batches))
                return {
                    "collected": [len(batch.rows) for batch in batches],
                    "publication": written, "failed_skus": failed,
                    **({"api_verification": api_check} if api_check is not None else {}),
                    **({"fuel_cross_check": batches[0].checks} if batches[0].checks is not None else {}),
                }

            try:
                report[category] = attempt(refresh)
            except (sqlite3.Error, psycopg.Error) as exc:
                report[category] = {"ok": False, "error": type(exc).__name__}
    if args.catalogue_base and args.cache.is_file():
        add_reference_data(args.cache)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(item["ok"] and item.get("api_verification", {}).get("ok", True) for item in report.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
