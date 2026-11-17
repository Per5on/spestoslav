"""Explicit demo fixtures, isolated from real products and price observations."""

import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/v1/demo")
ASSETS = Path(__file__).resolve().parent / "demo_assets"
PRODUCTS = json.loads(
    (
        Path(__file__).resolve().parents[2] / "data/demo-thumbnails/catalog.json"
    ).read_text()
)["products"]


def enabled():
    if os.getenv("ENABLE_DEMO_CATALOG", "").lower() != "true":
        raise HTTPException(404, "Demo catalog is disabled")


@router.get("/catalog")
def demo_catalog(
    request: Request,
    category_code: str = Query(default="groceries", pattern="^(groceries|technology)$"),
):
    enabled()
    return {
        "is_demo": True,
        "source": "SAMPLE_THUMBNAIL_CATALOGUE",
        "products": [
            {
                "id": "demo-" + row["code"],
                "name": row["name"],
                "category_code": row["category_code"],
                "package": row["package"],
                "image_url": str(request.url_for("demo_image", asset=row["code"]))
                + "?v="
                + row["asset_sha256"][:12],
                "price_eur": None,
                "verified": False,
                "is_demo": True,
                "source_url": row["source_url"],
            }
            for row in PRODUCTS
            if row["category_code"] == category_code
        ],
    }


@router.get("/credits")
def credits():
    enabled()
    return [
        {
            key: row.get(key, "")
            for key in (
                "code",
                "name",
                "source_url",
                "license",
                "license_url",
                "author",
            )
        }
        for row in PRODUCTS
    ]


@router.get("/images/{asset}", name="demo_image")
def demo_image(asset: str):
    enabled()
    row = next((row for row in PRODUCTS if row["code"] == asset), None)
    if row is None:
        raise HTTPException(404, "Demo asset not found")
    return FileResponse(
        ASSETS / row["asset"],
        media_type=row["content_type"],
        headers={"Cache-Control": "public,max-age=86400"},
    )
