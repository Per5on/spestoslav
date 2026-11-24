import csv
from decimal import Decimal
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import sys
from zipfile import ZipFile

import pytest
from sqlalchemy import create_engine
from app.db import normalize_database_url

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import prepare_beta108_public_data as archive


def test_sealed_archive_normalizes_bgn_once(tmp_path):
    manifest = json.loads(archive.MANIFEST.read_text())
    catalogue = json.loads((archive.ROOT / "data/groceries/essential-1000.json").read_text())["products"]
    product = next(p for p in catalogue if p["source_product_code"] == "100015")
    branch = manifest["branches"][0]
    text = StringIO()
    writer = csv.writer(text)
    writer.writerow(archive.HEADER)
    writer.writerow([branch["code"], branch["label"], product["name"], "100015", "1", "4.29", "0"])
    path = tmp_path / "archive.zip"
    with ZipFile(path, "w") as data:
        data.writestr("Burlex_202420609.csv", text.getvalue())
    manifest["price_archive_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert archive.load_prices(path, manifest)[0]["prices"] == [
        {"sku": "100015", "raw_bgn": "4.29", "amount": "2.19"},
    ]
    with pytest.raises(ValueError, match="complete sealed"):
        archive.render(manifest, [{**branch, "prices": [{"sku": "100015", "amount": "2.19"}]}], repair=True)
    manifest["price_input_currency"] = "EUR"
    with pytest.raises(ValueError, match="outside the reviewed scope"):
        archive.load_prices(path, manifest)


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Disposable PostgreSQL required")
def test_history_repair_is_scoped_and_idempotent():
    manifest = json.loads(archive.MANIFEST.read_text())
    branch = manifest["branches"][0]
    prices = [{"sku": str(i), "raw_bgn": "4.29", "amount": "2.19"} for i in range(1358)]
    sql = archive.render(manifest, [{**branch, "prices": prices}], repair=True)
    engine = create_engine(normalize_database_url(os.environ["TEST_DATABASE_URL"]))
    try:
        with engine.begin() as db:
            db.exec_driver_sql("CREATE TEMP TABLE locality_ekatte (locality_id uuid, ekatte_code text) ON COMMIT DROP")
            db.exec_driver_sql("CREATE TEMP TABLE product_barcodes (id uuid) ON COMMIT DROP")
            db.exec_driver_sql("CREATE TEMP TABLE store_branches (id uuid, locality_id uuid, active bool, retailer_code text, branch_name text, address text) ON COMMIT DROP")
            db.exec_driver_sql("CREATE TEMP TABLE grocery_catalog_identities (product_id uuid, source text, source_product_code text) ON COMMIT DROP")
            db.exec_driver_sql("""CREATE TEMP TABLE price_observations (id uuid PRIMARY KEY, product_id uuid, branch_id uuid,
                price_eur numeric, regular_price_eur numeric, source text, source_reference text,
                verified bool, valid_from timestamptz, valid_until timestamptz, collected_at timestamptz) ON COMMIT DROP""")
            db.exec_driver_sql("INSERT INTO locality_ekatte VALUES (md5('locality')::uuid,'68134')")
            db.exec_driver_sql("INSERT INTO store_branches VALUES (md5('branch')::uuid,md5('locality')::uuid,true,'burlex',%s,%s)", (branch["name"], branch["address"]))
            db.exec_driver_sql("""INSERT INTO grocery_catalog_identities
                SELECT md5(n::text)::uuid,'burlex-public-basket',n::text FROM generate_series(0,1357) n""")
            db.exec_driver_sql("""INSERT INTO price_observations
                SELECT md5('kzp:2026-11-22:' || md5('branch')::uuid::text || ':' || product_id::text)::uuid,
                    product_id,md5('branch')::uuid,4.29,4.29,'KZP_OPEN_ARCHIVE',%s,true,
                    '2026-11-22 00:00:00+02','2026-11-23 00:00:00+02','2026-11-22 00:00:00+02'
                FROM grocery_catalog_identities""", (manifest["price_archive"],))
            db.exec_driver_sql("INSERT INTO price_observations (id, price_eur, source) VALUES (md5('unrelated')::uuid,4.29,'DIRECT')")
            db.exec_driver_sql(sql)
            db.exec_driver_sql(sql)
            assert db.exec_driver_sql("SELECT count(*) FROM price_observations WHERE price_eur=2.19 AND regular_price_eur=2.19").scalar_one() == 1358
            assert db.exec_driver_sql("SELECT price_eur FROM price_observations WHERE source='DIRECT'").scalar_one() == Decimal("4.29")
    finally:
        engine.dispose()
