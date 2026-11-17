"""Local-only UI fixtures: never imported by deployed application modules."""

import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import smtplib
import uuid

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from app import feedback
from app.models import Category, Locality, Product, Retailer, StoreBranch
from app.marketplace import CurrentPrice
from app.workflows import ProductImage


def seed(app, sessions, root):
    spec = importlib.util.spec_from_file_location(
        "simulation_technology_import", root / "scripts/import_technology_catalog.py"
    )
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)
    priorities = json.loads((root / "data/retailer_priorities_007.json").read_text())[
        "retailers"
    ]
    with sessions.begin() as db:
        importer.import_catalog(db, importer.load_catalog())
        if not db.get(Category, "fuel"):
            db.add(Category(code="fuel", name_bg="Горива", name_en="Fuel"))
            db.flush()
        sofia = db.scalar(select(Locality).where(Locality.name_bg == "София"))
        keys = {
            (x.name_bg, x.municipality, x.region) for x in db.scalars(select(Locality))
        }
        with (root / "data/bulgaria_localities.csv").open(
            encoding="utf-8-sig"
        ) as handle:
            for row in csv.DictReader(handle):
                name = row["settlement_name_bg"]
                municipality = row["municipality_name_source"].split(" / ")[0]
                region = row["oblast_name_source"].split(" / ")[0]
                identity = (name, municipality, region)
                if identity in keys:
                    continue
                keys.add(identity)
                db.add(
                    Locality(
                        id=uuid.uuid5(uuid.NAMESPACE_URL, "|".join(identity)),
                        source="SIMULATION_REFERENCE",
                        source_id=hashlib.sha256(
                            "|".join(identity).encode()
                        ).hexdigest(),
                        name=name,
                        name_bg=name,
                        name_latin=row["settlement_name_latin"],
                        municipality=municipality,
                        region=region,
                        on_map=True,
                    )
                )
        for row in priorities:
            code = row["retailer_code"]
            if not db.get(Retailer, code):
                db.add(
                    Retailer(
                        code=code,
                        name=row["retailer_name"],
                        category_code=row["category_code"],
                        website_url=row["official_website"],
                    )
                )
                db.flush()
            db.add(
                StoreBranch(
                    id=uuid.uuid5(uuid.NAMESPACE_URL, "simulation-branch-" + code),
                    retailer_code=code,
                    locality_id=sofia.id,
                    branch_name="Симулация · " + row["retailer_name"],
                    address="Примерен обект · демонстрационен адрес",
                    source="SIMULATION",
                )
            )
        db.flush()
        for name, asset in [("SIM Мляко 1 L", "milk"), ("SIM Олио 1 L", "oil")]:
            product = db.scalar(select(Product).where(Product.name == name))
            db.add(
                ProductImage(
                    product_id=product.id,
                    image_url="http://127.0.0.1:8774/api/v1/demo/images/" + asset,
                    source_url="https://example.invalid/simulation",
                )
            )
        for index, (code, name) in enumerate(
            [
                ("petrol", "Бензин 95"),
                ("petrol98", "Бензин 98+"),
                ("diesel", "Дизел"),
                ("dieselPlus", "Дизел +"),
                ("lpg", "Автогаз"),
            ]
        ):
            product = Product(
                id=uuid.uuid5(uuid.NAMESPACE_URL, "simulation-fuel-" + code),
                category_code="fuel",
                name=name,
                normalized_name=name.casefold(),
                variant=code,
                package_unit="L",
            )
            db.add(product)
            db.flush()
            for number, row in enumerate(
                x for x in priorities if x["category_code"] == "fuel"
            ):
                db.add(
                    CurrentPrice(
                        product_id=product.id,
                        branch_id=uuid.uuid5(
                            uuid.NAMESPACE_URL,
                            "simulation-branch-" + row["retailer_code"],
                        ),
                        price_eur=Decimal("1.45")
                        + Decimal(index) / 10
                        + Decimal(number) / 100,
                        source="SIMULATION",
                        verified_at=datetime.now(timezone.utc),
                    )
                )
    # No actual SMTP connection; records are ephemeral synthetic evidence only.
    state = {"mode": "available", "messages": []}
    feedback.configured = lambda: state["mode"] != "unavailable"

    def deliver(payload):
        if state["mode"] == "failure":
            raise smtplib.SMTPException("Simulated provider failure")
        state["messages"].append(
            {"recipient": feedback.RECIPIENT, **payload.model_dump()}
        )

    feedback.deliver = deliver

    class Mode(BaseModel):
        mode: str

    @app.post("/__simulation/feedback-mode")
    def change_mode(payload: Mode):
        if payload.mode not in ("available", "failure", "unavailable"):
            raise HTTPException(422, "Invalid simulation mode")
        state["mode"] = payload.mode
        feedback._attempts.clear()
        return {"is_simulation": True, "mode": state["mode"]}

    @app.get("/__simulation/feedback")
    def evidence():
        return {"is_simulation": True, "messages": state["messages"]}
