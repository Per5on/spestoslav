#!/usr/bin/env python3
"""Render the reviewed Beta_10.8 public-data import against the existing catalogue."""

import argparse
import csv
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import hashlib
from io import TextIOWrapper
import json
from pathlib import Path
import unicodedata
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/public/beta-10.8.json"
HEADER = [
    "Населено място", "Търговски обект", "Наименование на продукта",
    "Код на продукта", "Категория", "Цена на дребно", "Цена в промоция",
]


def normal(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def bgn_to_eur(amount):
    return (amount / Decimal("1.95583")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate(manifest):
    checked = date.fromisoformat(manifest["price_date"])
    if (
        checked != date(2026, 11, 22)
        or manifest.get("price_input_currency") != "BGN"
        or manifest["price_currency"] != "EUR"
    ):
        raise ValueError("Archive date and currency are outside the reviewed scope")
    codes = [row["code"] for row in manifest["localities"]]
    if len(set(codes)) != len(codes) or any(len(c) != 5 or not c.isascii() or not c.isdecimal() for c in codes):
        raise ValueError("Invalid official locality codes")
    gtins = [row["gtin"] for row in manifest["barcodes"]]
    for code in gtins:
        if (
            len(code) != 13 or not code.isascii() or not code.isdecimal()
            or sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(code)) % 10
        ):
            raise ValueError("Invalid reviewed GTIN")
    if len(gtins) != len(set(gtins)):
        raise ValueError("Duplicate reviewed GTIN")


def load_prices(archive, manifest):
    validate(manifest)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest["price_archive_sha256"]:
        raise ValueError("Archive digest differs from the reviewed snapshot")
    catalogue = json.loads((ROOT / "data/groceries/essential-1000.json").read_text())
    names = {p["source_product_code"]: normal(p["name"]) for p in catalogue["products"]}
    reviewed = {row["label"]: row for row in manifest["branches"]}
    results = {label: {} for label in reviewed}
    with ZipFile(archive) as zipped:
        member, = (item for item in zipped.infolist() if item.filename.endswith("_202420609.csv"))
        if member.file_size > 10_000_000:
            raise ValueError("Unexpected retailer file size")
        with zipped.open(member) as file:
            reader = csv.reader(TextIOWrapper(file, encoding="utf-8-sig"))
            if next(reader) != HEADER:
                raise ValueError("Unexpected retailer columns")
            for city, label, name, code, _, regular, _promo in reader:
                if label not in reviewed or city != reviewed[label]["code"] or names.get(code) != normal(name):
                    continue
                price = Decimal(regular)
                if not price.is_finite() or not 0 < price <= 99999999 or price.as_tuple().exponent < -2:
                    raise ValueError("Invalid regular price")
                # The archive has no per-promotion validity. Keep the regular observation only.
                normalized = bgn_to_eur(price)
                if normalized <= 0:
                    raise ValueError("Archive price rounds to zero EUR")
                value = (format(price, ".2f"), format(normalized, ".2f"))
                if code in results[label] and results[label][code] != value:
                    raise ValueError("Conflicting price observations in one branch")
                results[label][code] = value
    return [
        {**row, "prices": [{"sku": sku, "raw_bgn": amounts[0], "amount": amounts[1]}
                            for sku, amounts in sorted(results[label].items())]}
        for label, row in reviewed.items()
    ]


def render(manifest, branches, *, repair=False):
    validate(manifest)
    payload = json.dumps({**manifest, "branches": branches}, ensure_ascii=False, separators=(",", ":"))
    if "$reviewed$" in payload or "$beta108$" in payload or any(not row["prices"] for row in branches):
        raise ValueError("Missing data or reserved SQL delimiter")
    if repair and sum(len(row["prices"]) for row in branches) != 1358:
        raise ValueError("Repair requires the complete sealed 1,358-row batch")
    return """DO $beta108$
DECLARE
    manifest_data jsonb := $reviewed$@PAYLOAD@$reviewed$::jsonb;
    row_data jsonb;
    matched integer;
    target uuid;
    repair_mode constant boolean := @REPAIR@;
    day_start timestamptz := (manifest_data->>'price_date')::date::timestamp AT TIME ZONE 'Europe/Sofia';
    day_end timestamptz := ((manifest_data->>'price_date')::date + 1)::timestamp AT TIME ZONE 'Europe/Sofia';
BEGIN
    SET LOCAL lock_timeout = '5s';
    LOCK TABLE locality_ekatte, product_barcodes, price_observations IN SHARE ROW EXCLUSIVE MODE;
    IF day_end > now() THEN RAISE EXCEPTION 'The sealed archive must be historical'; END IF;
    IF NOT repair_mode THEN
        FOR row_data IN SELECT value FROM jsonb_array_elements(manifest_data->'localities') LOOP
            SELECT count(*), min(id::text)::uuid INTO matched,target FROM inhabited_localities
            WHERE on_map AND name_bg=row_data->>'name' AND municipality=row_data->>'municipality' AND region=row_data->>'region';
            IF matched <> 1 OR EXISTS (
                SELECT 1 FROM locality_ekatte WHERE (locality_id=target OR ekatte_code=row_data->>'code')
                AND (locality_id,ekatte_code) IS DISTINCT FROM (target,row_data->>'code')
            ) THEN RAISE EXCEPTION 'Locality mapping missing or conflicting'; END IF;
            INSERT INTO locality_ekatte VALUES (target,row_data->>'code',manifest_data->>'locality_source',(manifest_data->>'locality_as_of')::date)
            ON CONFLICT DO NOTHING;
        END LOOP;
        FOR row_data IN SELECT value FROM jsonb_array_elements(manifest_data->'barcodes') LOOP
            SELECT count(*), min(p.id::text)::uuid INTO matched,target FROM products p
            JOIN technology_catalog_identities t ON t.product_id=p.id
            WHERE p.active AND p.category_code='technology' AND t.source='TECHMART_PUBLIC_CATALOG'
              AND t.source_product_code=row_data->>'sku' AND t.source_url=row_data->>'source';
            IF matched <> 1 OR EXISTS (
                SELECT 1 FROM products WHERE barcode ~ '^[0-9]{8,14}$'
                  AND lpad(barcode,14,'0')=lpad(row_data->>'gtin',14,'0') AND id<>target
            ) OR EXISTS (
                SELECT 1 FROM product_barcodes WHERE barcode ~ '^[0-9]{8,14}$'
                  AND lpad(barcode,14,'0')=lpad(row_data->>'gtin',14,'0')
                  AND (product_id<>target OR NOT verified)
            ) THEN RAISE EXCEPTION 'Product mapping missing or conflicting'; END IF;
            INSERT INTO product_barcodes (id,product_id,barcode,source,verified)
            VALUES (md5('beta108-gtin:' || (row_data->>'gtin'))::uuid,target,row_data->>'gtin','TECHMART_CORROBORATED',true)
            ON CONFLICT (barcode) DO NOTHING;
        END LOOP;
    END IF;
    FOR row_data IN SELECT value FROM jsonb_array_elements(manifest_data->'branches') LOOP
        SELECT count(*), min(b.id::text)::uuid INTO matched,target FROM store_branches b
        JOIN locality_ekatte e ON e.locality_id=b.locality_id
        WHERE b.active AND b.retailer_code='burlex' AND e.ekatte_code=row_data->>'code'
          AND b.branch_name=row_data->>'name' AND b.address=row_data->>'address';
        IF matched <> 1 THEN RAISE EXCEPTION 'Archive branch missing or ambiguous'; END IF;
        IF repair_mode THEN
            UPDATE price_observations h SET price_eur=o.amount, regular_price_eur=o.amount
            FROM jsonb_to_recordset(row_data->'prices') o(sku text, amount numeric, raw_bgn numeric)
            JOIN grocery_catalog_identities i ON i.source='burlex-public-basket' AND i.source_product_code=o.sku
            WHERE h.id=md5('kzp:' || (manifest_data->>'price_date') || ':' || target::text || ':' || i.product_id::text)::uuid
              AND h.product_id=i.product_id AND h.branch_id=target
              AND h.source='KZP_OPEN_ARCHIVE' AND h.source_reference=manifest_data->>'price_archive'
              AND h.verified AND h.valid_from=day_start AND h.valid_until=day_end
              AND h.collected_at=day_start AND h.price_eur=o.raw_bgn AND h.regular_price_eur=o.raw_bgn;
        ELSE
            WITH quotes AS (
                SELECT p.id, o.amount FROM jsonb_to_recordset(row_data->'prices') o(sku text, amount numeric)
                JOIN grocery_catalog_identities i ON i.source='burlex-public-basket' AND i.source_product_code=o.sku
                JOIN products p ON p.id=i.product_id AND p.active AND p.category_code='groceries'
            )
            INSERT INTO price_observations (id,product_id,branch_id,price_eur,regular_price_eur,source,source_reference,verified,valid_from,valid_until,collected_at)
            SELECT md5('kzp:' || (manifest_data->>'price_date') || ':' || target::text || ':' || q.id::text)::uuid,
              q.id,target,q.amount,q.amount,'KZP_OPEN_ARCHIVE',manifest_data->>'price_archive',true,day_start,day_end,day_start
            FROM quotes q ON CONFLICT (id) DO NOTHING;
        END IF;
        SELECT count(*) INTO matched FROM jsonb_to_recordset(row_data->'prices') o(sku text, amount numeric)
        JOIN grocery_catalog_identities i ON i.source='burlex-public-basket' AND i.source_product_code=o.sku
        JOIN price_observations h ON h.id=md5('kzp:' || (manifest_data->>'price_date') || ':' || target::text || ':' || i.product_id::text)::uuid
        WHERE h.product_id=i.product_id AND h.branch_id=target AND h.price_eur=o.amount AND h.verified
          AND h.source='KZP_OPEN_ARCHIVE' AND h.source_reference=manifest_data->>'price_archive'
          AND h.regular_price_eur=o.amount AND h.valid_from=day_start
          AND h.valid_until=day_end AND h.collected_at=day_start;
        IF matched <> jsonb_array_length(row_data->'prices') THEN RAISE EXCEPTION 'Archive quote mismatch'; END IF;
    END LOOP;
END $beta108$;""".replace("@PAYLOAD@", payload).replace("@REPAIR@", "true" if repair else "false")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--repair-currency", action="store_true", help="Render a repair for the existing historical batch")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    print(render(manifest, load_prices(args.archive, manifest), repair=args.repair_currency))
