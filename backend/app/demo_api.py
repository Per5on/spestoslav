"""Explicit demo fixtures, isolated from real products and price observations."""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/v1/demo")
ASSETS = Path(__file__).resolve().parent / "demo_assets"
PRODUCTS = [
    ("milk", "Демо: прясно мляко", "1 L"),
    ("oil", "Демо: слънчогледово олио", "1 L"),
    ("sugar", "Демо: захар", "1 kg"),
]


def enabled():
    if os.getenv("ENABLE_DEMO_CATALOG", "").lower() != "true":
        raise HTTPException(404, "Demo catalog is disabled")


@router.get("/catalog")
def demo_catalog(request: Request):
    enabled()
    return {
        "is_demo": True,
        "source": "USER_PROVIDED_REFERENCE",
        "products": [
            {
                "id": "demo-" + code,
                "name": name,
                "category_code": "groceries",
                "package": package,
                "image_url": str(request.url_for("demo_image", asset=code)),
                "price_eur": None,
                "verified": False,
                "is_demo": True,
            }
            for code, name, package in PRODUCTS
        ],
    }


@router.get("/images/{asset}", name="demo_image")
def demo_image(asset: str):
    enabled()
    if asset not in {code for code, _, _ in PRODUCTS}:
        raise HTTPException(404, "Demo asset not found")
    return FileResponse(
        ASSETS / (asset + ".jpg"),
        media_type="image/jpeg",
        headers={"Cache-Control": "public,max-age=86400"},
    )
