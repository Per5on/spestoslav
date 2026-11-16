"""Local mock-simulation server. NEVER imported by the deployed application.

Run: SP...=local-only PYTHONPATH=backend:backend/tests python -m uvicorn scenario_api:app --host 127.0.0.1 --port 8774
"""

import os

if os.getenv("SPESTOVNIK_SIMULATION") != "local-only":
    raise RuntimeError("Explicit local simulation opt-in required")
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import importlib.util
from fastapi import Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, update
import test_locality_search as fixtures
from app.main import app
from app.db import get_db
from app.auth import current_user, Principal
from app.models import Category, Product, Retailer, StoreBranch
from app.marketplace import CurrentPrice, ProductBarcode, Promotion
from app import mobile_auth
from app.receipt_worker import process_one

fixtures.setup_function()
app.dependency_overrides[get_db] = fixtures.override_get_db
root = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "grocery_import", root / "scripts/import_grocery_catalog.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with fixtures.TestingSessionLocal.begin() as db:
    module.import_catalog(db, module.load_catalog())
    db.execute(update(Category).where(Category.code == "FOOD").values(active=False))
    db.execute(
        update(Product)
        .where(Product.category_code == "FOOD")
        .values(
            category_code="groceries",
            name="SIM Мляко 1 L",
            normalized_name="sim мляко 1 l",
            barcode="4006381333931",
        )
    )
    db.execute(
        update(Retailer)
        .where(Retailer.code == "TEST")
        .values(category_code="groceries", name="Симулация A")
    )
    db.execute(update(ProductBarcode).values(barcode="4006381333931"))
    db.execute(
        update(Promotion).values(ends_at=datetime.now(timezone.utc) - timedelta(days=1))
    )
    branch = db.scalar(select(StoreBranch))
    branch.address = "Тестова улица A"
    oil = Product(
        category_code="groceries",
        name="SIM Олио 1 L",
        normalized_name="sim олио 1 l",
        barcode="96385074",
    )
    db.add(oil)
    db.flush()
    db.add(
        CurrentPrice(
            product_id=oil.id,
            branch_id=branch.id,
            price_eur=Decimal("3"),
            source="SIMULATION",
            verified_at=datetime.now(timezone.utc),
        )
    )
    product = db.scalar(select(Product).where(Product.barcode == "4006381333931"))
    for code, name, milk_price, oil_price in [
        ("SIM_B", "Симулация B", "1.10", "4"),
        ("SIM_C", "Симулация C", ".50", None),
    ]:
        retailer = Retailer(code=code, name=name, category_code="groceries")
        db.add(retailer)
        db.flush()
        other = StoreBranch(
            retailer_code=code,
            locality_id=branch.locality_id,
            address="Тестова улица " + code,
        )
        db.add(other)
        db.flush()
        for p, v in [(product, milk_price), (oil, oil_price)]:
            if v:
                db.add(
                    CurrentPrice(
                        product_id=p.id,
                        branch_id=other.id,
                        price_eur=Decimal(v),
                        source="SIMULATION",
                        verified_at=datetime.now(timezone.utc),
                    )
                )

users = {
    "alice": {"id": "alice", "email": "alice@example.invalid", "name": "Alice"},
    "bob": {"id": "bob", "email": "bob@example.invalid", "name": "Bob"},
}
revoked = set()


def fake_provider(path, method="GET", session=None, payload=None):
    if path in ("/sign-in/email", "/sign-up/email"):
        name = payload["email"].split("@")[0]
        if name not in users or payload["password"] != "simulation-password":
            raise HTTPException(401, "Simulation credentials rejected")
        revoked.discard(name)
        return {"user": users[name]}, "simulation." + name
    name = (session or "").removeprefix("simulation.")
    if name not in users or name in revoked:
        raise HTTPException(401, "Simulation session expired")
    if path == "/token":
        return {"token": "simulation-jwt-" + name}, None
    if path == "/get-session":
        return {"user": users[name]}, None
    if path == "/sign-out":
        revoked.add(name)
        return {"success": True}, None
    raise HTTPException(404, "Simulation provider route missing")


mobile_auth.upstream = fake_provider


def simulation_user(authorization: str | None = Header(default=None)):
    name = (authorization or "").removeprefix("Bearer simulation-jwt-")
    if name not in users or name in revoked:
        raise HTTPException(401, "Simulation sign-in required")
    return Principal(name)


app.dependency_overrides[current_user] = simulation_user
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8775", "http://127.0.0.1:8775"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/__simulation/ocr")
def run_ocr():
    return {
        "is_simulation": True,
        "processed": process_one(fixtures.TestingSessionLocal),
    }


@app.get("/__simulation/route")
def route_example():
    from itertools import permutations

    matrix = {
        ("Home", "A"): 1,
        ("A", "Home"): 1,
        ("Home", "B"): 2,
        ("B", "Home"): 2,
        ("A", "B"): 1,
        ("B", "A"): 1,
    }
    routes = [
        (
            ["Home", *order, "Home"],
            sum(matrix[a, b] for a, b in zip(["Home", *order], [*order, "Home"])),
        )
        for order in permutations(["A", "B"])
    ]
    order, distance = min(routes, key=lambda p: p[1])
    return {
        "is_simulation": True,
        "proposed_order": order,
        "distance_km": distance,
        "distance_source": "synthetic test matrix",
        "real_directions_available": False,
        "travel_cost_included": False,
    }


@app.post("/__simulation/approve")
def approve_example():
    from app.workflows import ReviewSubmission
    from app.marketplace import PriceCache
    from app.write_api import review, ReviewInput

    with fixtures.TestingSessionLocal() as db:
        submission = db.scalar(
            select(ReviewSubmission)
            .join(PriceCache, PriceCache.id == ReviewSubmission.cache_id)
            .where(
                PriceCache.status == "PENDING",
                ReviewSubmission.owner_subject == "alice",
            )
        )
        if not submission:
            raise HTTPException(404, "No simulation submission")
        result = review(
            submission.id,
            ReviewInput(
                decision="APPROVED", note="Reviewed synthetic local receipt fixture"
            ),
            principal=Principal("simulation-admin", "admin"),
            db=db,
        )
        return {"is_simulation": True, "result": result}
