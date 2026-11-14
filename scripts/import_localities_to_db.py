#!/usr/bin/env python3
"""Import the reviewed GeoNames locality CSV into the Spestoslav database."""
import csv
import hashlib
import os
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db import SessionLocal
from app.models import Locality, LocalityPostalCode

CSV_PATH = ROOT / "data" / "bulgaria_postal_codes.csv"

def identity_id(row):
    identity = "|".join((
        row["settlement_name_bg"].strip().casefold(),
        row["settlement_name_latin"].strip().casefold(),
        row["municipality_code"].strip(),
        row["oblast_code"].strip(),
    ))
    return hashlib.md5(identity.encode("utf-8")).hexdigest()

def main():
    if SessionLocal is None:
        raise SystemExit("DATABASE_URL is not configured")
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    localities = {}
    postal_links = set()
    for row in rows:
        source_id = identity_id(row)
        localities[source_id] = {
            "source": "GEONAMES",
            "source_id": source_id,
            "name": row["settlement_name_latin"].strip(),
            "name_bg": row["settlement_name_bg"].strip(),
            "name_latin": row["settlement_name_latin"].strip(),
            "type": "OTHER",
            "municipality": row["municipality_name_source"].split(" / ", 1)[0].strip(),
            "municipality_code": row["municipality_code"].strip(),
            "region": row["oblast_name_source"].split(" / ", 1)[0].strip(),
            "region_code": row["oblast_code"].strip(),
            "on_map": True,
        }
        postal_links.add((source_id, row["postal_code"].strip()))

    with SessionLocal() as db:
        with db.begin():
            for item in localities.values():
                stmt = insert(Locality).values(**item).on_conflict_do_update(
                    constraint="uq_inhabited_locality_source",
                    set_={k:v for k,v in item.items() if k not in ("source","source_id")}
                )
                db.execute(stmt)
            ids = {
                x.source_id: x.id for x in db.scalars(
                    select(Locality).where(Locality.source == "GEONAMES")
                ).all()
            }
            link_rows = [
                {"locality_id": ids[source_id], "postal_code": code, "source": "GEONAMES"}
                for source_id, code in postal_links if source_id in ids
            ]
            if link_rows:
                db.execute(insert(LocalityPostalCode).values(link_rows).on_conflict_do_nothing(
                    constraint="uq_locality_postal_code"
                ))
    print(f"Imported/updated {len(localities)} localities and {len(postal_links)} postal-code links.")

if __name__ == "__main__":
    main()
