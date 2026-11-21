import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import Locality, Category, Product, Retailer, StoreBranch
from app.marketplace import CurrentPrice, ProductBarcode, Promotion
from datetime import datetime, timedelta, timezone

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def register_unicode_lower(dbapi_connection, _connection_record):
    dbapi_connection.create_function(
        "lower",
        1,
        lambda value: value.casefold() if value is not None else None,
        deterministic=True,
    )


TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def setup_function():
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        locality_id = uuid.uuid4()
        db.add(
            Locality(
                id=locality_id,
                source="TEST",
                source_id="sofia-test",
                name="Sofija",
                name_bg="София",
                name_latin="Sofija",
                type="CITY",
                municipality="Столична",
                region="София (столица)",
                on_map=True,
            )
        )

        db.add(Category(code="FOOD", name_bg="Храни", name_en="Food"))
        db.flush()
        db.add(Retailer(code="TEST", name="Test Market", category_code="FOOD"))
        product_id, branch_id = uuid.uuid4(), uuid.uuid4()
        db.add(
            Product(
                id=product_id,
                category_code="FOOD",
                barcode="3800000000003",
                name="Test product",
                normalized_name="test product",
            )
        )
        db.flush()
        db.add(
            ProductBarcode(
                product_id=product_id,
                barcode="3800000000003",
                source="TEST",
                verified=True,
            )
        )
        db.add(
            StoreBranch(
                id=branch_id,
                retailer_code="TEST",
                locality_id=locality_id,
                address="Main street 1",
            )
        )
        db.flush()
        db.add(
            CurrentPrice(
                product_id=product_id,
                branch_id=branch_id,
                price_eur=1.25,
                source="TEST",
                verified_at=datetime.now(timezone.utc),
            )
        )
        db.add(
            Promotion(
                product_id=product_id,
                branch_id=branch_id,
                promotional_price_eur=0.99,
                regular_price_eur=1.25,
                starts_at=datetime.now(timezone.utc) - timedelta(days=1),
                ends_at=datetime.now(timezone.utc) + timedelta(days=1),
                source="TEST",
                verified=True,
            )
        )
        db.commit()


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_search_by_bulgarian_name():
    response = client.get("/api/v1/localities", params={"q": "София"})
    assert response.status_code == 200
    result = response.json()[0]
    assert result["name_bg"] == "София"
    assert result["municipality"] == "Столична"
    assert result["postal_codes"] == []


def test_search_by_common_english_spelling():
    response = client.get("/api/v1/localities", params={"q": "Sofia"})
    assert response.status_code == 200
    assert response.json()[0]["name_latin"] == "Sofija"


def test_two_character_prefix_ranks_before_contains_matches():
    with TestingSessionLocal() as db:
        for index in range(25):
            db.add(
                Locality(
                    source="TEST",
                    source_id=f"contains-{index}",
                    name=f"Asova {index}",
                    name_bg=f"Асова {index}",
                    type="VILLAGE",
                    on_map=True,
                )
            )
        db.commit()
    for query in ("Со", "So"):
        response = client.get("/api/v1/localities", params={"q": query})
        assert response.status_code == 200
        assert len(response.json()) == 20
        assert response.json()[0]["name_bg"] == "София"


def test_prefix_and_contains_groups_are_each_alphabetical():
    with TestingSessionLocal() as db:
        for latin, bulgarian, locality_type in (
            ("Visoko", "Високо", "CITY"),
            ("Sozopol", "Созопол", "CITY"),
            ("Asovo", "Асово", "VILLAGE"),
            ("Sovata", "Совата", "VILLAGE"),
        ):
            db.add(
                Locality(
                    source="TEST",
                    source_id=latin,
                    name=latin,
                    name_latin=latin,
                    name_bg=bulgarian,
                    type=locality_type,
                    on_map=True,
                )
            )
        db.commit()

    for query in ("Со", "SO"):
        response = client.get("/api/v1/localities", params={"q": query})
        assert response.status_code == 200
        assert [row["name_bg"] for row in response.json()] == [
            "Совата",
            "Созопол",
            "София",
            "Асово",
            "Високо",
        ]


def test_locality_search_treats_sql_wildcards_literally():
    for query in ("%%", "__"):
        assert client.get("/api/v1/localities", params={"q": query}).json() == []


def test_postal_search_is_removed():
    response = client.get("/api/v1/localities", params={"q": "1000"})
    assert response.status_code == 200
    assert response.json() == []


def test_barcode_lookup():
    response = client.get("/api/v1/products/barcode/3800000000003")
    assert response.status_code == 200
    assert response.json()["name"] == "Test product"


def test_store_list_is_limited_to_registered_active_branches():
    locality_id = client.get("/api/v1/localities", params={"q": "София"}).json()[0][
        "id"
    ]
    response = client.get("/api/v1/stores", params={"locality_id": locality_id})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["retailer_name"] == "Test Market"


def test_current_prices_and_promotions():
    assert len(client.get("/api/v1/prices/current").json()) == 1
    offers = client.get("/api/v1/promotions").json()
    assert len(offers) == 1
    assert offers[0]["promotional_price_eur"] == 0.99


def test_merchant_directory_lists_active_addresses_with_bounded_paging():
    with TestingSessionLocal.begin() as db:
        locality_id = db.scalar(select(Locality.id))
        db.add_all([
            StoreBranch(retailer_code="TEST", locality_id=locality_id, address="Main street 2"),
            StoreBranch(retailer_code="TEST", locality_id=locality_id, address="Inactive", active=False),
        ])

    first = client.get("/api/v1/merchant-directory", params={"limit": 1})
    assert first.status_code == 200
    page = first.json()
    branch = page["branches"][0]
    assert branch["retailer_name"] == "Test Market"
    assert branch["category_code"] == "FOOD"
    assert branch["locality_name"] == "София"
    assert branch["address"] == "Main street 1"
    assert page["next_offset"] == 1

    last = client.get("/api/v1/merchant-directory", params={"limit": 1, "offset": 1}).json()
    assert [branch["address"] for branch in last["branches"]] == ["Main street 2"]
    assert last["next_offset"] is None
    assert client.get("/api/v1/merchant-directory", params={"offset": 2}).json() == {
        "branches": [], "next_offset": None,
    }
    assert client.get("/api/v1/merchant-directory", params={"limit": 201}).status_code == 422
