from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .db import get_db
from .models import Category, Locality, LocalityPostalCode

app = FastAPI(title="Спестослав API", version="0.3.0")


class CategoryResponse(BaseModel):
    code: str
    name_bg: str
    name_en: str


class LocalityResponse(BaseModel):
    id: str
    name: str
    name_bg: str | None = None
    name_latin: str | None = None
    postal_codes: list[str] = Field(default_factory=list)
    type: str
    municipality: str | None = None
    region: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "spestoslav-api"}


@app.get("/api/v1/categories", response_model=list[CategoryResponse])
def categories(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Category)
        .where(Category.active.is_(True))
        .order_by(Category.sort_order)
    ).all()
    return [
        CategoryResponse(code=row.code, name_bg=row.name_bg, name_en=row.name_en)
        for row in rows
    ]


@app.get("/api/v1/localities", response_model=list[LocalityResponse])
def search_localities(
    q: str = Query(min_length=2, max_length=80),
    db: Session = Depends(get_db),
):
    term = q.strip()
    if len(term) < 2:
        return []

    normalized = term.casefold()
    # Bulgarian transliterations vary (e.g. София is commonly written Sofia,
    # while GeoNames stores Sofija). Search common "ia" -> "ija" variants too.
    latin_terms = {normalized, normalized.replace("ia", "ija")}
    contains_patterns = [f"%{value}%" for value in latin_terms]
    starts_with_patterns = [f"{value}%" for value in latin_terms]
    postal_matches = select(LocalityPostalCode.locality_id).where(
        LocalityPostalCode.postal_code.like(f"{term}%")
    )

    text_matches = [
        func.lower(Locality.name).like(pattern)
        for pattern in contains_patterns
    ] + [
        func.lower(func.coalesce(Locality.name_latin, "")).like(pattern)
        for pattern in contains_patterns
    ] + [
        func.lower(func.coalesce(Locality.name_bg, "")).like(f"%{normalized}%")
    ]

    localities = db.scalars(
        select(Locality)
        .where(Locality.on_map.is_(True))
        .where(or_(*text_matches, Locality.id.in_(postal_matches)))
        .order_by(
            (func.lower(func.coalesce(Locality.name_bg, "")) == normalized).desc(),
            or_(*[
                func.lower(func.coalesce(Locality.name_latin, "")).like(pattern)
                for pattern in starts_with_patterns
            ]).desc(),
            Locality.name_bg,
            Locality.name,
        )
        .limit(20)
    ).all()

    locality_ids = [locality.id for locality in localities]
    postal_rows = db.execute(
        select(LocalityPostalCode.locality_id, LocalityPostalCode.postal_code)
        .where(LocalityPostalCode.locality_id.in_(locality_ids))
        .order_by(LocalityPostalCode.postal_code)
    ).all() if locality_ids else []

    postal_codes_by_locality: dict[str, list[str]] = {}
    for locality_id, postal_code in postal_rows:
        postal_codes_by_locality.setdefault(str(locality_id), []).append(postal_code)

    return [
        LocalityResponse(
            id=str(locality.id),
            name=locality.name,
            name_bg=locality.name_bg,
            name_latin=locality.name_latin,
            postal_codes=postal_codes_by_locality.get(str(locality.id), []),
            type=locality.type,
            municipality=locality.municipality,
            region=locality.region,
        )
        for locality in localities
    ]
