#!/usr/bin/env python3
"""Import owner-approved grade labels only; never infer Fuelo prices or stations."""

import argparse
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.db import SessionLocal
from app.models import Category, Product

PATH = Path(__file__).resolve().parents[1] / "data/fuel/types.json"
CODES = {"petrol", "petrol98", "diesel", "dieselPlus", "lpg"}


def product_id(code):
    return uuid.uuid5(uuid.NAMESPACE_URL, "spestovnik:fuel:" + code)


def load_types(path=PATH):
    data = json.loads(Path(path).read_text())
    rows = data["products"]
    if (
        data["source"] != "OWNER_APPROVED_FUEL_TAXONOMY"
        or len(rows) != 5
        or {p["code"] for p in rows} != CODES
    ):
        raise ValueError("Expected the five approved fuel grades")
    if any(
        not p["name_bg"].strip()
        or any(k in p for k in ("price_eur", "barcode", "branch_id"))
        for p in rows
    ):
        raise ValueError("No inferred price, barcode or station allowed")
    return rows


def import_types(db, rows):
    if not db.get(Category, "fuel"):
        db.add(Category(code="fuel", name_bg="Горива", name_en="Fuel", sort_order=30))
        db.flush()
    for row in rows:
        identity = product_id(row["code"])
        product = db.get(Product, identity)
        if product is None:
            db.add(
                Product(
                    id=identity,
                    category_code="fuel",
                    name=row["name_bg"],
                    normalized_name=row["name_bg"].casefold(),
                    variant=row["code"],
                    package_unit="l",
                )
            )
        elif product.category_code != "fuel" or product.variant != row["code"]:
            raise ValueError("Existing fuel identity conflict requires review")
    db.flush()
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    rows = load_types()
    if args.apply:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL required")
        with SessionLocal.begin() as db:
            print(import_types(db, rows))
    else:
        print(
            "Validated five grade labels; no prices, barcodes, stations or database writes"
        )
