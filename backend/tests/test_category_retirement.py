"""Exercise the destructive retirement against realistic FKs in disposable Postgres."""

import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text, select, func, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from app.db import normalize_database_url
from app.models import (
    Category,
    Locality,
    Retailer,
    Product,
    StoreBranch,
    PriceObservation,
)
from app.marketplace import (
    ProductBarcode,
    CurrentPrice,
    PriceCache,
    Promotion,
    ReceiptScan,
    ReceiptItem,
)
from app.workflows import (
    ReviewSubmission,
    CollectionSource,
    ReceiptJob,
    ProductIdentificationRequest,
    ProductImage,
    NationalOffer,
)


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"), reason="Requires disposable PostgreSQL"
)
def test_retirement_removes_only_home_and_postal_data():
    root = Path(__file__).resolve().parents[1]
    engine = create_engine(normalize_database_url(os.environ["TEST_DATABASE_URL"]))
    schema = "retirement_" + uuid.uuid4().hex
    with engine.begin() as db:
        db.execute(text(f'CREATE SCHEMA "{schema}"'))
    scoped = make_url(engine.url).update_query_dict(
        {"options": f"-csearch_path={schema}"}
    )
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    scoped_engine = create_engine(scoped)
    sessions = sessionmaker(bind=scoped_engine, expire_on_commit=False)
    from unittest.mock import patch

    with patch.dict(
        os.environ, {"DATABASE_URL": scoped.render_as_string(hide_password=False)}
    ):
        try:
            command.upgrade(config, "0005_catalog_and_freshness")
            now = datetime.now(timezone.utc)
            with sessions.begin() as db:
                db.add_all(
                    [
                        Category(code="home", name_bg="Дом", name_en="Home"),
                        Category(code="groceries", name_bg="Храни", name_en="Food"),
                    ]
                )
                db.flush()
                locality = Locality(
                    source="TEST", source_id="retain-me", name="Sofija", name_bg="София"
                )
                db.add(locality)
                db.flush()
                locality_id = locality.id
                db.execute(
                    text(
                        "INSERT INTO locality_postal_codes (id,locality_id,postal_code,source) VALUES (:id,:locality,'1000','TEST')"
                    ),
                    {"id": uuid.uuid4(), "locality": locality_id},
                )
                db.add_all(
                    [
                        Retailer(
                            code="home-shop", name="Home shop", category_code="home"
                        ),
                        Retailer(
                            code="food-shop",
                            name="Food shop",
                            category_code="groceries",
                        ),
                    ]
                )
                db.flush()
                home = Product(
                    category_code="home",
                    name="Home product",
                    normalized_name="home product",
                )
                food = Product(
                    category_code="groceries",
                    name="Food product",
                    normalized_name="food product",
                )
                db.add_all([home, food])
                db.flush()
                food_id = food.id
                home_branch = StoreBranch(
                    retailer_code="home-shop",
                    locality_id=locality_id,
                    address="Home test address",
                )
                food_branch = StoreBranch(
                    retailer_code="food-shop",
                    locality_id=locality_id,
                    address="Food test address",
                )
                db.add_all([home_branch, food_branch])
                db.flush()
                food_branch_id = food_branch.id
                db.add_all(
                    [
                        CurrentPrice(
                            product_id=home.id,
                            branch_id=home_branch.id,
                            price_eur=2,
                            source="TEST",
                            verified_at=now,
                        ),
                        CurrentPrice(
                            product_id=food.id,
                            branch_id=food_branch.id,
                            price_eur=3,
                            source="TEST",
                            verified_at=now,
                        ),
                        PriceObservation(
                            product_id=home.id,
                            branch_id=home_branch.id,
                            price_eur=2,
                            source="TEST",
                        ),
                        Promotion(
                            product_id=home.id,
                            branch_id=home_branch.id,
                            promotional_price_eur=1,
                            starts_at=now,
                            source="TEST",
                        ),
                        ProductBarcode(product_id=home.id, barcode="12345678"),
                        ProductImage(
                            product_id=home.id,
                            image_url="https://example.test/home.png",
                            source_url="https://example.test",
                        ),
                        ProductIdentificationRequest(
                            owner_subject="test-user",
                            barcode="12345678",
                            product_id=home.id,
                        ),
                        CollectionSource(
                            code="home-source",
                            retailer_code="home-shop",
                            origin="https://example.test",
                        ),
                        NationalOffer(
                            product_id=home.id,
                            retailer_code="home-shop",
                            price_eur=2,
                            source_reference="https://example.test",
                            observed_at=now,
                            verified_at=now,
                            verified_by="test-admin",
                            valid_until=now + timedelta(days=1),
                        ),
                    ]
                )
                cache = PriceCache(
                    product_id=home.id,
                    branch_id=home_branch.id,
                    submitted_price_eur=2,
                    source="TEST",
                )
                db.add(cache)
                db.flush()
                db.add(
                    ReviewSubmission(
                        owner_subject="test-user",
                        request_key="home-request",
                        cache_id=cache.id,
                    )
                )
                scan = ReceiptScan(
                    image_storage_key="synthetic-only/home.png",
                    branch_id=home_branch.id,
                )
                other_scan = ReceiptScan(
                    image_storage_key="synthetic-only/food.png",
                    branch_id=food_branch.id,
                )
                db.add_all([scan, other_scan])
                db.flush()
                food_scan_id = other_scan.id
                db.add_all(
                    [
                        ReceiptJob(scan_id=scan.id, owner_subject="test-user"),
                        ReceiptItem(
                            receipt_scan_id=scan.id,
                            product_id=home.id,
                            raw_description="Home",
                            status="UNMATCHED",
                        ),
                        ReceiptItem(
                            receipt_scan_id=other_scan.id,
                            product_id=food.id,
                            raw_description="Food",
                            status="UNMATCHED",
                        ),
                    ]
                )
            command.upgrade(config, "head")
            command.check(config)
            with sessions() as db:
                assert db.get(Locality, locality_id) is not None
                assert (
                    db.get(Product, food_id) is not None
                    and db.get(StoreBranch, food_branch_id) is not None
                )
                assert db.get(ReceiptScan, food_scan_id) is not None
                assert db.scalar(select(func.count()).select_from(ReceiptItem)) == 1
                assert db.scalar(select(func.count()).select_from(CurrentPrice)) == 1
                assert (
                    db.scalar(
                        select(func.count())
                        .select_from(Category)
                        .where(Category.code == "home")
                    )
                    == 0
                )
                for model in [
                    ReviewSubmission,
                    PriceCache,
                    PriceObservation,
                    Promotion,
                    ProductBarcode,
                    ProductImage,
                    ProductIdentificationRequest,
                    CollectionSource,
                    NationalOffer,
                    ReceiptJob,
                ]:
                    assert db.scalar(select(func.count()).select_from(model)) == 0, (
                        model.__tablename__
                    )
            inspector = inspect(scoped_engine)
            assert "locality_postal_codes" not in inspector.get_table_names()
            for table in ["inhabited_localities", "store_branches"]:
                assert "postal_code" not in {
                    c["name"] for c in inspector.get_columns(table)
                }
            # The exact same SQL can safely be applied again after a deployment retry.
            with scoped_engine.begin() as db:
                for statement in (
                    (root / "migrations/sql/0006_remove_home_postal.sql")
                    .read_text()
                    .split(";")
                ):
                    if statement.strip():
                        db.execute(text(statement))
        finally:
            scoped_engine.dispose()
            with engine.begin() as db:
                db.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            engine.dispose()
