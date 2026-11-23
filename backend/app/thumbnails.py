"""Versioned catalogue artwork and legacy product-group symbols."""

import hashlib
import os
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request, Response
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from .db import normalize_database_url

router = APIRouter(prefix="/api/v1/thumbnails")
url = os.getenv("THUMBNAILS_DATABASE_URL")
engine = (
    create_engine(normalize_database_url(url), pool_pre_ping=True, connect_args={"connect_timeout": 5})
    if url else None
)


@router.get("")
def thumbnail_manifest(request: Request, response: Response):
    response.headers["Cache-Control"] = "public, max-age=300"
    if engine is None:
        return {"images": {}}
    try:
        with engine.connect() as db:
            rows = db.execute(text("SELECT code, sha256 FROM symbolic_thumbnails ORDER BY code")).all()
    except SQLAlchemyError:
        raise HTTPException(503, "Symbolic thumbnails unavailable") from None
    return {"images": {
        code: request.url_for("symbolic_thumbnail", code=code).path + f"?v={digest}"
        for code, digest in rows
    }}


CATALOGUE_ART = Path(__file__).resolve().parents[2] / "data/catalogue-thumbnails"


@lru_cache(maxsize=1)
def catalogue_assets():
    return {path.stem: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(CATALOGUE_ART.glob("*.webp"))}


@router.get("/catalogue")
def catalogue_manifest(request: Request, response: Response):
    response.headers["Cache-Control"] = "public, max-age=300"
    return {"schema_version": 1, "images": {
        code: request.url_for("catalogue_thumbnail", code=code).path + f"?v={digest}"
        for code, digest in catalogue_assets().items()
    }}


@lru_cache(maxsize=64)
def catalogue_bytes(code: str, digest: str):
    if engine is not None:
        try:
            with engine.connect() as db:
                data = db.scalar(text(
                    "SELECT data FROM catalogue_thumbnails WHERE code = :code AND sha256 = :digest"
                ), {"code": code, "digest": digest})
            if data is not None and hashlib.sha256(data).hexdigest() == digest:
                return bytes(data)
        except SQLAlchemyError:
            pass  # The checked-in pack can serve the identical bytes during outages.
    return (CATALOGUE_ART / f"{code}.webp").read_bytes()


def image_response(data: bytes, digest: str):
    return Response(data, media_type="image/webp", headers={
        "Cache-Control": "public, max-age=31536000, immutable",
        "ETag": f'"{digest}"',
    })


@router.get("/catalogue/{code}", name="catalogue_thumbnail")
def catalogue_thumbnail(code: str, v: str = Query(pattern=r"^[a-f0-9]{64}$")):
    if catalogue_assets().get(code) != v:
        raise HTTPException(404, "Catalogue thumbnail not found")
    return image_response(catalogue_bytes(code, v), v)


@router.get("/{code}", name="symbolic_thumbnail")
def thumbnail(code: str, v: str = Query(pattern=r"^[a-f0-9]{64}$")):
    if engine is None:
        raise HTTPException(404, "Symbolic thumbnail not found")
    try:
        with engine.connect() as db:
            data = db.scalar(
                text("SELECT data FROM symbolic_thumbnails WHERE code = :code AND sha256 = :digest"),
                {"code": code, "digest": v},
            )
    except SQLAlchemyError:
        raise HTTPException(503, "Symbolic thumbnails unavailable") from None
    if data is None:
        raise HTTPException(404, "Symbolic thumbnail not found")
    return image_response(data, v)
