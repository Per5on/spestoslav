#!/usr/bin/env python3
"""Idempotent official-name import. Does not create barcodes, branches or prices."""

import argparse
import json
from pathlib import Path
import sys
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.db import SessionLocal
from app.models import Category, Product
from app.grocery import GroceryGroup, GroceryIdentity

CATALOG = Path(__file__).resolve().parents[1] / "data/groceries/essential-1000.json"
NAMESPACE = uuid.UUID("7ed3f621-dc85-4a36-b944-a36119f373c9")


def load_catalog(path=CATALOG):
    data = json.loads(Path(path).read_text())
    codes = {g["code"] for g in data["groups"]}
    rows = data["products"]
    if len(rows) != 1000 or len({p["source_product_code"] for p in rows}) != 1000:
        raise ValueError("Expected exactly 1,000 unique source product identities")
    if data["price_imported"] or data["barcodes_verified"]:
        raise ValueError(
            "This source provides names and retailer codes, not verified GTINs or price validity"
        )
    for row in rows:
        if not row["name"].strip() or row["group_code"] not in codes:
            raise ValueError("Invalid classification")
        if row.get("barcode") or row.get("price_eur"):
            raise ValueError("Unverified identifier or price")
    return data


def import_catalog(db, data):
    if not db.get(Category, "groceries"):
        db.add(
            Category(
                code="groceries", name_bg="Храни", name_en="Groceries", sort_order=10
            )
        )
        db.flush()
    for group in data["groups"]:
        row = db.get(GroceryGroup, group["code"])
        if row is None:
            row = GroceryGroup(**group)
            db.add(row)
        else:
            for key, value in group.items():
                setattr(row, key, value)
    db.flush()
    ids = [
        uuid.uuid5(NAMESPACE, data["source"] + ":" + p["source_product_code"])
        for p in data["products"]
    ]
    existing = {p.id: p for p in db.scalars(select(Product).where(Product.id.in_(ids)))}
    evidence_rows = {
        p.product_id: p
        for p in db.scalars(
            select(GroceryIdentity).where(GroceryIdentity.product_id.in_(ids))
        )
    }
    pending = []
    for item in data["products"]:
        identity = uuid.uuid5(
            NAMESPACE, data["source"] + ":" + item["source_product_code"]
        )
        product = existing.get(identity)
        if product is None:
            product = Product(
                id=identity,
                category_code="groceries",
                normalized_name="",
                name=item["name"],
            )
            db.add(product)
        product.name = item["name"]
        product.normalized_name = item["name"].casefold()
        product.package_quantity = (
            Decimal(item["package_quantity"]) if item["package_quantity"] else None
        )
        product.package_unit = item["package_unit"]
        pending.append((identity, item))
    db.flush()
    for identity, item in pending:
        values = dict(
            group_code=item["group_code"],
            source=data["source"],
            source_product_code=item["source_product_code"],
            source_category=item["source_category"],
            source_url=data["source_url"],
            observed_at=datetime.fromisoformat(data["observed_at"]),
        )
        evidence = evidence_rows.get(identity)
        if evidence is None:
            db.add(GroceryIdentity(product_id=identity, **values))
        else:
            for key, value in values.items():
                setattr(evidence, key, value)
    db.flush()
    return len(data["products"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    data = load_catalog()
    if args.apply:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL required")
        with SessionLocal.begin() as db:
            print(
                "Imported",
                import_catalog(db, data),
                "source-backed names; no prices or barcodes",
            )
    else:
        print(
            "Validated",
            len(data["products"]),
            "products in",
            len(data["groups"]),
            "groups; use --apply after testing the migration",
        )


def catalog_sql(data):
    """Same deterministic import through the connected SQL service when TCP is unavailable."""
    from sqlalchemy.dialects import postgresql
    from sqlalchemy.dialects.postgresql import insert

    dialect = postgresql.dialect()

    def compiled(statement):
        return str(
            statement.compile(dialect=dialect, compile_kwargs={"literal_binds": True})
        )

    statements = [
        compiled(
            insert(Category)
            .values(
                code="groceries",
                name_bg="Храни",
                name_en="Groceries",
                description_bg="",
                description_en="",
                sort_order=10,
                active=True,
            )
            .on_conflict_do_nothing(index_elements=["code"])
        )
    ]
    groups = insert(GroceryGroup).values(data["groups"])
    statements.append(
        compiled(
            groups.on_conflict_do_update(
                index_elements=["code"],
                set_={
                    key: getattr(groups.excluded, key)
                    for key in ["name_bg", "name_en", "aliases", "sort_order"]
                },
            )
        )
    )
    products = []
    identities = []
    for item in data["products"]:
        identity = uuid.uuid5(
            NAMESPACE, data["source"] + ":" + item["source_product_code"]
        )
        products.append(
            dict(
                id=identity,
                category_code="groceries",
                name=item["name"],
                normalized_name=item["name"].casefold(),
                package_quantity=Decimal(item["package_quantity"])
                if item["package_quantity"]
                else None,
                package_unit=item["package_unit"],
                active=True,
            )
        )
        identities.append(
            dict(
                product_id=identity,
                group_code=item["group_code"],
                source=data["source"],
                source_product_code=item["source_product_code"],
                source_category=item["source_category"],
                source_url=data["source_url"],
                observed_at=datetime.fromisoformat(data["observed_at"]),
            )
        )
    for offset in range(0, len(products), 100):
        product_sql = insert(Product).values(products[offset : offset + 100])
        statements.append(
            compiled(
                product_sql.on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        key: getattr(product_sql.excluded, key)
                        for key in [
                            "name",
                            "normalized_name",
                            "package_quantity",
                            "package_unit",
                        ]
                    },
                )
            )
        )
    for offset in range(0, len(identities), 100):
        evidence_sql = insert(GroceryIdentity).values(identities[offset : offset + 100])
        statements.append(
            compiled(
                evidence_sql.on_conflict_do_update(
                    index_elements=["product_id"],
                    set_={
                        key: getattr(evidence_sql.excluded, key)
                        for key in [
                            "group_code",
                            "source",
                            "source_product_code",
                            "source_category",
                            "source_url",
                            "observed_at",
                        ]
                    },
                )
            )
        )
    return statements
