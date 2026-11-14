import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import Locality, LocalityPostalCode

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
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
                latitude=42.6977,
                longitude=23.3219,
                on_map=True,
            )
        )
        db.add(
            LocalityPostalCode(
                locality_id=locality_id,
                postal_code="1000",
                source="TEST",
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
    assert result["postal_codes"] == ["1000"]


def test_search_by_common_english_spelling():
    response = client.get("/api/v1/localities", params={"q": "Sofia"})
    assert response.status_code == 200
    assert response.json()[0]["name_latin"] == "Sofija"


def test_search_by_postal_code():
    response = client.get("/api/v1/localities", params={"q": "1000"})
    assert response.status_code == 200
    assert response.json()[0]["postal_codes"] == ["1000"]
