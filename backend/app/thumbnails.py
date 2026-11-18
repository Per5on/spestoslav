"""Public product-group symbols served from a dedicated image database."""

import os

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
    return Response(data, media_type="image/webp", headers={
        "Cache-Control": "public, max-age=31536000, immutable",
        "ETag": f'"{v}"',
    })
