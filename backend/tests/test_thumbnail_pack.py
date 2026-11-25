import hashlib
import json
import os
import runpy
import uuid
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

from app import thumbnails
from app.db import normalize_database_url
from test_locality_search import client


def test_catalogue_pack_is_available_without_the_thumbnail_database(monkeypatch):
    monkeypatch.setattr(thumbnails, "engine", None)
    thumbnails.catalogue_bytes.cache_clear()
    response = client.get("/api/v1/thumbnails/catalogue")
    assert response.status_code == 200
    manifest = response.json()
    assert manifest["schema_version"] == 1
    assert {
        "groceries", "dairy-eggs", "bakery-breakfast", "produce", "meat-fish", "pantry",
        "spices-drinks", "technology", "mobile", "major-appliances", "small-appliances",
        "tv-computing", "smart-home-mobility",
    } <= manifest["images"].keys()
    expected = json.loads((thumbnails.CATALOGUE_ART / "sha256.json").read_text())
    assert set(manifest["images"]) == set(expected)
    for code, path in manifest["images"].items():
        image_response = client.get(path)
        assert image_response.status_code == 200
        assert image_response.headers["content-type"] == "image/webp"
        assert "immutable" in image_response.headers["cache-control"]
        digest = hashlib.sha256(image_response.content).hexdigest()
        assert path.endswith(f"?v={digest}")
        assert digest == expected[code]
        assert image_response.headers["etag"] == f'"{digest}"'
        with Image.open(BytesIO(image_response.content)) as image:
            image.load()
            assert image.format == "WEBP"
            assert image.size == (160, 140)
    assert client.get(f"/api/v1/thumbnails/catalogue/mobile?v={'0' * 64}").status_code == 404
    thumbnails.catalogue_bytes.cache_clear()


def test_catalogue_pack_survives_thumbnail_database_outage(monkeypatch):
    class UnavailableDatabase:
        def connect(self):
            raise OperationalError("test", {}, RuntimeError("unavailable"))

    monkeypatch.setattr(thumbnails, "engine", UnavailableDatabase())
    thumbnails.catalogue_bytes.cache_clear()
    path = client.get("/api/v1/thumbnails/catalogue").json()["images"]["small-appliances"]
    actual = client.get(path)
    assert actual.status_code == 200
    assert actual.content == (thumbnails.CATALOGUE_ART / "small-appliances.webp").read_bytes()
    thumbnails.catalogue_bytes.cache_clear()


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Disposable PostgreSQL required")
def test_catalogue_seed_replays_and_the_api_reads_the_same_database_bytes(monkeypatch, tmp_path):
    url = normalize_database_url(os.environ["TEST_DATABASE_URL"])
    root = create_engine(url)
    schema = "thumbnail_pack_" + uuid.uuid4().hex
    with root.begin() as db:
        db.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
    scoped = create_engine(make_url(url).update_query_dict({"options": f"-csearch_path={schema}"}))
    script = Path(__file__).resolve().parents[2] / "scripts/prepare_symbolic_thumbnails.py"
    statements = runpy.run_path(str(script))["catalogue_seed"]()
    try:
        for _ in range(2):
            with scoped.begin() as db:
                for statement in statements:
                    db.exec_driver_sql(statement)
                assert db.exec_driver_sql("SELECT COUNT(*) FROM catalogue_thumbnails").scalar_one() == len(statements) - 1
        monkeypatch.setattr(thumbnails, "engine", scoped)
        path = client.get("/api/v1/thumbnails/catalogue").json()["images"]["small-appliances"]
        expected = (thumbnails.CATALOGUE_ART / "small-appliances.webp").read_bytes()
        monkeypatch.setattr(thumbnails, "CATALOGUE_ART", tmp_path)
        thumbnails.catalogue_bytes.cache_clear()
        response = client.get(path)
        assert response.status_code == 200
        assert response.content == expected
    finally:
        thumbnails.catalogue_bytes.cache_clear()
        scoped.dispose()
        with root.begin() as db:
            db.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        root.dispose()
