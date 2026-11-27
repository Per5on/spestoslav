#!/usr/bin/env python3
"""Collect bounded, indicative Techmart online offers and render an additive import."""

import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import json
from pathlib import Path
import time
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import httpx

BASE = "https://techmart.bg"
AGENT = "Spestovnik-Catalog-Review/0.3"
CATALOGUE = Path(__file__).resolve().parents[1] / "data/technology/essential-1000.json"


class StructuredData(HTMLParser):
    def __init__(self):
        super().__init__()
        self.product_nodes = []
        self.parts = None

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self.parts = []

    def handle_data(self, data):
        if self.parts is not None:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag != "script" or self.parts is None:
            return
        raw = "".join(self.parts)
        self.parts = None
        try:
            root = json.loads(raw)
        except ValueError:
            return
        nodes = root.get("@graph", [root]) if isinstance(root, dict) else root
        if isinstance(nodes, list):
            self.product_nodes.extend(
                node for node in nodes if isinstance(node, dict) and node.get("@type") == "Product"
            )


def offer_price(html, code, *, source_url=None, product_name=None, gtin=None):
    structured = StructuredData()
    structured.feed(html)
    matching = [node for node in structured.product_nodes if str(node.get("sku")) == code]
    if len(matching) != 1:
        raise ValueError(f"Expected one exact online SKU {code}")
    product = matching[0]
    if product_name is not None and product.get("name") != product_name:
        raise ValueError(f"Product name changed for SKU {code}")
    if gtin is not None and str(product.get("gtin13")) != gtin:
        raise ValueError(f"GTIN changed for SKU {code}")
    offer = product.get("offers")
    if isinstance(offer, list):
        offer = offer[0] if len(offer) == 1 else None
    if (
        not isinstance(offer, dict)
        or offer.get("@type") != "Offer"
        or offer.get("priceCurrency") != "EUR"
        or offer.get("availability") not in ("https://schema.org/InStock", "http://schema.org/InStock")
        or (source_url is not None and offer.get("url", source_url) != source_url)
    ):
        return None
    try:
        price = Decimal(str(offer.get("price")))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid EUR amount for SKU {code}") from exc
    if not price.is_finite() or not 0 < price <= 9999999 or price.as_tuple().exponent < -2:
        raise ValueError(f"Invalid EUR amount for SKU {code}")
    return str(price)


def collect(codes, client, *, on_failed_sku=None):
    source = json.loads(CATALOGUE.read_text())
    by_code = {row["source_product_code"]: row["source_url"] for row in source["products"]}
    robots_response = client.get(BASE + "/robots.txt")
    robots_response.raise_for_status()
    robots = RobotFileParser()
    robots.parse(robots_response.text.replace("\\r\\n", "\n").splitlines())
    for code in codes:
        url = by_code.get(code)
        if url is None and on_failed_sku is not None:
            on_failed_sku(code)
            continue
        if url is None:
            raise ValueError(f"SKU {code} is absent from the imported catalogue")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "techmart.bg" or not robots.can_fetch(AGENT, url):
            raise ValueError(f"Catalogue URL is outside the allowed source for SKU {code}")
        time.sleep(1)
        try:
            response = client.get(url)
            response.raise_for_status()
            price = offer_price(response.text, code)
        except (httpx.HTTPError, ValueError):
            if on_failed_sku is None:
                raise
            on_failed_sku(code)
            continue
        if price:
            observed = datetime.now(timezone.utc)
            yield {
                "code": code, "url": url, "price": price, "observed": observed.isoformat(),
                "expires": (observed + timedelta(hours=12)).isoformat(),
            }


def render(rows, *, summary=False):
    payload = json.dumps(rows)
    if not rows or "$observations$" in payload:
        raise ValueError("No valid offers or invalid SQL delimiter")
    statement = """WITH observations AS (
  SELECT * FROM jsonb_to_recordset($observations$@PAYLOAD@$observations$::jsonb)
    AS o(code text, url text, price numeric, observed timestamptz, expires timestamptz)
), matched AS (
SELECT md5(concat_ws('|','techmart-online',i.product_id,o.observed::text))::uuid AS id,
  i.product_id,r.code,o.price,o.url,o.observed,o.expires
FROM observations o JOIN technology_catalog_identities i
  ON i.source='TECHMART_PUBLIC_CATALOG' AND i.source_product_code=o.code AND i.source_url=o.url
JOIN products p ON p.id=i.product_id AND p.active AND p.category_code='technology'
JOIN catalog_retailers r ON r.code='techmart' AND r.active AND r.category_code=p.category_code
WHERE o.observed <= now() AND now() < o.expires
), inserted AS (
  INSERT INTO national_offers
    (id,product_id,retailer_code,price_eur,source_reference,observed_at,verified_at,verified_by,valid_until)
  SELECT id,product_id,code,price,url,observed,now(),'techmart-public-jsonld',expires
  FROM matched ON CONFLICT (id) DO NOTHING RETURNING product_id, price_eur
) """.replace("@PAYLOAD@", payload)
    return statement + (
        "SELECT (SELECT count(*) FROM matched) AS matched, count(*) AS published FROM inserted;"
        if summary else "SELECT product_id, price_eur FROM inserted;"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sku", required=True, action="append")
    args = parser.parse_args()
    codes = list(dict.fromkeys(args.sku))
    if len(codes) > 20 or any(not code.isascii() or not code.isdecimal() for code in codes):
        parser.error("Choose 1–20 numeric Techmart SKUs")
    with httpx.Client(timeout=20, follow_redirects=False, headers={"User-Agent": AGENT}) as client:
        print(render(list(collect(codes, client))))
