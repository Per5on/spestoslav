from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .db import get_db
from .models import Category, Locality, LocalityPostalCode

app = FastAPI(title="Спестослав API", version="0.2.0")

class CategoryResponse(BaseModel):
    code: str
    name_bg: str
    name_en: str

class LocalityResponse(BaseModel):
    id: str
    name: str
    name_bg: str | None = None
    postal_codes: list[str] = []
    type: str
    municipality: str | None = None
    region: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "service": "spestoslav-api"}

@app.get("/api/v1/categories", response_model=list[CategoryResponse])
def categories(db: Session = Depends(get_db)):
    rows = db.scalars(select(Category).where(Category.active.is_(True)).order_by(Category.sort_order)).all()
    return [CategoryResponse(code=r.code, name_bg=r.name_bg, name_en=r.name_en) for r in rows]

@app.get("/api/v1/localities", response_model=list[LocalityResponse])
def search_localities(q: str = Query(min_length=2, max_length=80), db: Session = Depends(get_db)):
    term = q.strip()
    if len(term) < 2:
        return []
    pattern = f"%{term}%"
    postal_match = select(LocalityPostalCode.locality_id).where(LocalityPostalCode.postal_code == term)
    rows = db.scalars(
        select(Locality)
        .where(Locality.on_map.is_(True))
        .where(or_(
            func.lower(Locality.name).like(pattern.lower()),
            func.lower(func.coalesce(Locality.name_bg, "")).like(pattern.lower()),
            func.lower(func.coalesce(Locality.name_latin, "")).like(pattern.lower()),
            Locality.id.in_(postal_match),
        ))
        .order_by((func.lower(Locality.name_bg) == term.lower()).desc(), Locality.name_bg, Locality.name)
        .limit(20)
    ).all()
    return [
        LocalityResponse(
            id=str(r.id), name=r.name, name_bg=r.name_bg,
            postal_codes=db.scalars(
                select(LocalityPostalCode.postal_code)
                .where(LocalityPostalCode.locality_id == r.id)
                .order_by(LocalityPostalCode.postal_code)
            ).all(),
            type=r.type, municipality=r.municipality, region=r.region
        )
        for r in rows
    ]
