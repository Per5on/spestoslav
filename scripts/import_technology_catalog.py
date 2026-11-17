#!/usr/bin/env python3
"""Validate/import source-backed technology identities; never infer price or GTIN."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.db import SessionLocal
from app.models import Category, Product, Retailer
from app.technology import TechnologyGroup, TechnologyIdentity

CATALOG = Path(__file__).resolve().parents[1] / "data/technology/essential-1000.json"
NAMESPACE = uuid.UUID("b2da8396-149a-40ca-bcb9-d560723408e0")


def load_catalog(path=CATALOG):
    data = json.loads(Path(path).read_text())
    rows = data["products"]
    groups = {g["code"] for g in data["groups"]}
    if len(rows) != 1000 or len({p["source_product_code"] for p in rows}) != 1000:
        raise ValueError("Exactly 1,000 explicit retailer product codes required")
    if data["prices_imported"] or data["verified_gtins"]:
        raise ValueError("This source freeze does not verify prices or GTINs")
    for item in rows:
        source = urlsplit(item["source_url"])
        if (
            not item["name"].strip()
            or item["group_code"] not in groups
            or source.scheme != "https"
            or source.hostname != "techmart.bg"
            or source.username
            or item.get("barcode")
            or item.get("price_eur")
        ):
            raise ValueError("Invalid/unverified source identity")
    return data


def import_catalog(db, data):
    if not db.get(Category, "technology"):
        db.add(
            Category(
                code="technology",
                name_bg="Техника",
                name_en="Technology",
                sort_order=20,
            )
        )
        db.flush()
    retailer = db.get(Retailer, "techmart")
    if retailer is None:
        db.add(
            Retailer(
                code="techmart",
                name="Techmart",
                category_code="technology",
                website_url="https://techmart.bg/",
            )
        )
    elif retailer.category_code != "technology":
        raise ValueError("Existing Techmart identity has a conflicting category")
    # Existing retailer active state is retained; no branch or price is inferred.
    for group in data["groups"]:
        row = db.get(TechnologyGroup, group["code"])
        if row is None:
            db.add(TechnologyGroup(**group))
        else:
            for key, value in group.items():
                setattr(row, key, value)
    db.flush()
    for item in data["products"]:
        identity = uuid.uuid5(
            NAMESPACE, data["source"] + ":" + item["source_product_code"]
        )
        product = db.get(Product, identity)
        if product is None:
            product = Product(
                id=identity,
                category_code="technology",
                name=item["name"],
                normalized_name=item["name"].casefold(),
            )
            db.add(product)
        if product.category_code != "technology":
            raise ValueError("Existing product has a conflicting category")
        product.name = item["name"]
        product.normalized_name = item["name"].casefold()
        if item.get("brand") is not None:
            product.brand = item["brand"]
        # Preserve existing barcode and active state on repeated imports.
        db.flush()
        row = db.get(TechnologyIdentity, identity)
        values = dict(
            group_code=item["group_code"],
            source=data["source"],
            source_product_code=item["source_product_code"],
            source_category=item["source_category"],
            source_url=item["source_url"],
            observed_at=datetime.fromisoformat(data["observed_at"]),
        )
        if row is None:
            db.add(TechnologyIdentity(product_id=identity, **values))
        else:
            for key, value in values.items():
                setattr(row, key, value)
    db.flush()
    return len(data["products"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    data = load_catalog()
    if args.apply:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is required")
        with SessionLocal.begin() as db:
            print(import_catalog(db, data))
    else:
        print(
            "Validated", len(data["products"]), "source identities; no database changes"
        )
