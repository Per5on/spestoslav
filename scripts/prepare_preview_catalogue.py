#!/usr/bin/env python3
"""Render checked additive catalogue statements for a raw PostgreSQL transaction.

No database connections or writes. Output chunks must execute in ONE transaction after
applying migration0008 and checking the preview baseline/recovery copy.
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.models import Product, Retailer
from app.technology import TechnologyGroup, TechnologyIdentity
from import_fuel_types import load_types, product_id
from import_technology_catalog import NAMESPACE, load_catalog
from sqlalchemy import func, or_, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert


def render(statement):
    # Raw SQL transport performs no DBAPI %-substitution. Match the explicitly
    # required standard_conforming_strings=on instead of an uninitialized dialect.
    dialect = postgresql.dialect(paramstyle="named")
    dialect._backslash_escapes = False
    return str(
        statement.compile(dialect=dialect, compile_kwargs={"literal_binds": True})
    )


def guard(query):
    return (
        "DO $catalogue_guard$ BEGIN IF EXISTS ("
        + render(query)
        + ") THEN RAISE EXCEPTION 'Existing catalogue identity conflict requires review'; END IF; END $catalogue_guard$"
    )


def batches(data=None, fuels=None):
    data = data if data is not None else load_catalog()
    fuels = fuels if fuels is not None else load_types()
    groups = ["SET LOCAL standard_conforming_strings=on"]
    for group in data["groups"]:
        statement = insert(TechnologyGroup).values(
            dict(group, aliases=group.get("aliases", ""))
        )
        groups.append(
            render(
                statement.on_conflict_do_update(
                    index_elements=["code"],
                    set_={
                        key: getattr(statement.excluded, key)
                        for key in group
                        if key != "code"
                    },
                )
            )
        )
    result = [groups]
    for offset in range(0, len(data["products"]), 100):
        products, identities = [], []
        for row in data["products"][offset : offset + 100]:
            identity = uuid.uuid5(
                NAMESPACE, data["source"] + ":" + row["source_product_code"]
            )
            products.append(
                {
                    "id": identity,
                    "category_code": "technology",
                    "name": row["name"],
                    "normalized_name": row["name"].casefold(),
                    "brand": row.get("brand"),
                    "active": True,
                }
            )
            identities.append(
                {
                    "product_id": identity,
                    "group_code": row["group_code"],
                    "source": data["source"],
                    "source_product_code": row["source_product_code"],
                    "source_category": row["source_category"],
                    "source_url": row["source_url"],
                    "observed_at": datetime.fromisoformat(data["observed_at"]),
                }
            )
        check = guard(
            select(Product.id).where(
                Product.id.in_([p["id"] for p in products]),
                Product.category_code != "technology",
            )
        )
        p = insert(Product).values(products)
        p = p.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": p.excluded.name,
                "normalized_name": p.excluded.normalized_name,
                "brand": func.coalesce(p.excluded.brand, Product.brand),
            },
        )
        i = insert(TechnologyIdentity).values(identities)
        i = i.on_conflict_do_update(
            index_elements=["product_id"],
            set_={
                key: getattr(i.excluded, key)
                for key in (
                    "group_code",
                    "source",
                    "source_product_code",
                    "source_category",
                    "source_url",
                    "observed_at",
                )
            },
        )
        result.append([check, render(p), render(i)])
    directory = [
        guard(
            select(Retailer.code).where(
                Retailer.code == "techmart", Retailer.category_code != "technology"
            )
        )
    ]
    directory.append(
        render(
            insert(Retailer)
            .values(
                code="techmart",
                name="Techmart",
                category_code="technology",
                website_url="https://techmart.bg/",
                active=True,
            )
            .on_conflict_do_nothing(index_elements=["code"])
        )
    )
    for row in fuels:
        identity = product_id(row["code"])
        directory.append(
            guard(
                select(Product.id).where(
                    Product.id == identity,
                    or_(
                        Product.category_code != "fuel",
                        Product.variant.is_distinct_from(row["code"]),
                    ),
                )
            )
        )
        directory.append(
            render(
                insert(Product)
                .values(
                    id=identity,
                    category_code="fuel",
                    name=row["name_bg"],
                    normalized_name=row["name_bg"].casefold(),
                    variant=row["code"],
                    package_unit="l",
                    active=True,
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )
        )
    result.append(directory)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    chunks = batches()
    for index, chunk in enumerate(chunks):
        (args.output_dir / f"{index:02}.json").write_text(
            json.dumps(chunk, ensure_ascii=False)
        )
    print(
        json.dumps(
            {
                "chunks": len(chunks),
                "statements": sum(map(len, chunks)),
                "database_writes": False,
            }
        )
    )
