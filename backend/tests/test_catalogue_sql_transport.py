"""Raw SQL transport must preserve literal content and existing verified metadata."""

import os
import sys
import uuid
from pathlib import Path

import pytest
from app.db import Base, normalize_database_url
from app.main import app  # noqa: F401 — register runtime models
from app.marketplace import CurrentPrice
from app.models import Category, Product, Retailer
from app.technology import TechnologyGroup, TechnologyIdentity
from sqlalchemy import create_engine, func, literal, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from import_fuel_types import product_id
from import_technology_catalog import NAMESPACE, load_catalog
from prepare_preview_catalogue import batches, render

pytestmark = pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"), reason="Disposable PostgreSQL required"
)


def test_raw_literals_round_trip_without_dbapi_percent_or_backslash_escaping():
    engine = create_engine(normalize_database_url(os.environ["TEST_DATABASE_URL"]))
    try:
        with engine.begin() as db:
            db.exec_driver_sql("SET LOCAL standard_conforming_strings=on")
            for value in [
                "95% DCI-P3",
                "99% sRGB",
                "O'Brien \\ source; $quote$",
                "Български текст",
            ]:
                assert (
                    db.exec_driver_sql(
                        render(select(literal(value))),
                        execution_options={"no_parameters": True},
                    ).scalar_one()
                    == value
                )
    finally:
        engine.dispose()


def test_complete_transport_exact_source_content_and_repeat_preserves_history():
    url = normalize_database_url(os.environ["TEST_DATABASE_URL"])
    root = create_engine(url)
    schema = "catalogue_transport_" + uuid.uuid4().hex
    with root.begin() as db:
        db.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
    scoped = create_engine(
        make_url(url).update_query_dict({"options": f"-csearch_path={schema}"})
    )
    data = load_catalog()
    target = data["products"][0]
    target["brand"] = None  # Simulate an absent upstream field, not a brand change.
    identity = uuid.uuid5(
        NAMESPACE, data["source"] + ":" + target["source_product_code"]
    )
    try:
        Base.metadata.create_all(scoped)
        with Session(scoped) as db, db.begin():
            db.add_all(
                [
                    Category(code=c, name_bg=c, name_en=c)
                    for c in ("technology", "fuel", "groceries")
                ]
            )
            db.flush()
            db.add(
                Retailer(
                    code="techmart",
                    name="Retained retailer",
                    category_code="technology",
                    active=False,
                )
            )
            db.add(
                Product(
                    id=identity,
                    category_code="technology",
                    name="Retained identity",
                    normalized_name="retained",
                    brand="Known brand",
                    barcode="4006381333931",
                    active=False,
                )
            )
            db.add(
                Product(
                    id=product_id("petrol"),
                    category_code="fuel",
                    name="Retained grade",
                    normalized_name="retained",
                    variant="petrol",
                    barcode="96385074",
                    active=False,
                )
            )
            db.add(
                TechnologyGroup(
                    **dict(data["groups"][0], aliases="Custom verified search alias")
                )
            )
        statements = [s for chunk in batches(data) for s in chunk]
        fingerprints = []
        for _ in range(2):
            with scoped.begin() as db:
                for statement in statements:
                    db.exec_driver_sql(
                        statement, execution_options={"no_parameters": True}
                    )
            with Session(scoped) as db:
                rows = db.execute(
                    select(Product, TechnologyIdentity).join(
                        TechnologyIdentity, TechnologyIdentity.product_id == Product.id
                    )
                ).all()
                expected = {p["source_product_code"]: p for p in data["products"]}
                assert len(rows) == 1000
                for product, evidence in rows:
                    source = expected[evidence.source_product_code]
                    assert product.name == source["name"]
                    assert product.normalized_name == source["name"].casefold()
                    assert evidence.source_url == source["source_url"]
                    assert evidence.source_category == source["source_category"]
                    assert evidence.group_code == source["group_code"]
                assert db.get(Product, identity).brand == "Known brand"
                assert db.get(Product, identity).barcode == "4006381333931"
                assert db.get(Product, identity).active is False
                assert db.get(Product, product_id("petrol")).barcode == "96385074"
                assert db.get(Product, product_id("petrol")).active is False
                assert db.get(Retailer, "techmart").active is False
                assert (
                    db.get(TechnologyGroup, data["groups"][0]["code"]).aliases
                    == "Custom verified search alias"
                )
                assert db.scalar(select(func.count()).select_from(CurrentPrice)) == 0
                assert (
                    db.scalar(
                        select(func.count())
                        .select_from(Product)
                        .where(Product.category_code == "fuel")
                    )
                    == 5
                )
                fingerprints.append(
                    db.execute(
                        text(
                            "SELECT md5(string_agg(to_jsonb(p)::text,'' ORDER BY id)) FROM products p"
                        )
                    ).scalar_one()
                )
        assert fingerprints[0] == fingerprints[1]
    finally:
        scoped.dispose()
        with root.begin() as db:
            db.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        root.dispose()
