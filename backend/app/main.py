from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .db import get_db
from .models import Category, Locality, LocalityPostalCode, Product, Retailer, StoreBranch
from .marketplace import CurrentPrice, ProductBarcode, Promotion

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


from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException


class ProductLookupResponse(BaseModel):
    id: str
    category_code: str
    name: str
    brand: str | None = None
    variant: str | None = None
    package_quantity: float | None = None
    package_unit: str | None = None
    barcodes: list[str] = Field(default_factory=list)


class StoreBranchResponse(BaseModel):
    id: str
    retailer_code: str
    retailer_name: str
    locality_id: str
    locality_name: str
    branch_name: str | None = None
    address: str
    postal_code: str | None = None


class CurrentPriceResponse(BaseModel):
    id: str
    product_id: str
    branch_id: str
    price_eur: float
    source: str
    verified_at: datetime
    expires_at: datetime | None = None


class PromotionResponse(BaseModel):
    id: str
    product_id: str
    branch_id: str
    promotional_price_eur: float
    regular_price_eur: float | None = None
    starts_at: datetime
    ends_at: datetime | None = None


@app.get("/api/v1/products/barcode/{barcode}", response_model=ProductLookupResponse)
def product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    product = db.scalar(
        select(Product).join(ProductBarcode, ProductBarcode.product_id == Product.id)
        .where(ProductBarcode.barcode == barcode, ProductBarcode.verified.is_(True), Product.active.is_(True))
    )
    if product is None:
        product = db.scalar(select(Product).where(Product.barcode == barcode, Product.active.is_(True)))
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found for this barcode")
    codes = db.scalars(select(ProductBarcode.barcode).where(
        ProductBarcode.product_id == product.id, ProductBarcode.verified.is_(True)
    ).order_by(ProductBarcode.barcode)).all()
    if product.barcode and product.barcode not in codes:
        codes.append(product.barcode)
    return ProductLookupResponse(
        id=str(product.id), category_code=product.category_code, name=product.name,
        brand=product.brand, variant=product.variant,
        package_quantity=float(product.package_quantity) if product.package_quantity is not None else None,
        package_unit=product.package_unit, barcodes=codes,
    )


@app.get("/api/v1/stores", response_model=list[StoreBranchResponse])
def stores_for_locality(locality_id: UUID, db: Session = Depends(get_db)):
    rows = db.execute(
        select(StoreBranch, Retailer.name, Locality.name_bg, Locality.name)
        .join(Retailer, Retailer.code == StoreBranch.retailer_code)
        .join(Locality, Locality.id == StoreBranch.locality_id)
        .where(StoreBranch.locality_id == locality_id, StoreBranch.active.is_(True), Retailer.active.is_(True))
        .order_by(Retailer.name, StoreBranch.address)
    ).all()
    return [
        StoreBranchResponse(
            id=str(branch.id), retailer_code=branch.retailer_code, retailer_name=retailer_name,
            locality_id=str(branch.locality_id), locality_name=name_bg or locality_name,
            branch_name=branch.branch_name, address=branch.address,
            postal_code=getattr(branch, "postal_code", None),
        )
        for branch, retailer_name, name_bg, locality_name in rows
    ]


@app.get("/api/v1/prices/current", response_model=list[CurrentPriceResponse])
def current_prices(
    product_id: UUID | None = None, branch_id: UUID | None = None,
    locality_id: UUID | None = None, db: Session = Depends(get_db),
):
    stmt = select(CurrentPrice).join(StoreBranch, StoreBranch.id == CurrentPrice.branch_id).where(StoreBranch.active.is_(True))
    if product_id:
        stmt = stmt.where(CurrentPrice.product_id == product_id)
    if branch_id:
        stmt = stmt.where(CurrentPrice.branch_id == branch_id)
    if locality_id:
        stmt = stmt.where(StoreBranch.locality_id == locality_id)
    now = datetime.now(timezone.utc)
    rows = db.scalars(stmt.where(or_(CurrentPrice.expires_at.is_(None), CurrentPrice.expires_at > now))
        .order_by(CurrentPrice.verified_at.desc()).limit(500)).all()
    return [CurrentPriceResponse(
        id=str(row.id), product_id=str(row.product_id), branch_id=str(row.branch_id),
        price_eur=float(row.price_eur), source=row.source,
        verified_at=row.verified_at, expires_at=row.expires_at,
    ) for row in rows]


@app.get("/api/v1/promotions", response_model=list[PromotionResponse])
def active_promotions(
    locality_id: UUID | None = None, branch_id: UUID | None = None,
    product_id: UUID | None = None, db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    stmt = select(Promotion).join(StoreBranch, StoreBranch.id == Promotion.branch_id).where(
        Promotion.verified.is_(True), Promotion.starts_at <= now,
        or_(Promotion.ends_at.is_(None), Promotion.ends_at >= now), StoreBranch.active.is_(True),
    )
    if locality_id:
        stmt = stmt.where(StoreBranch.locality_id == locality_id)
    if branch_id:
        stmt = stmt.where(Promotion.branch_id == branch_id)
    if product_id:
        stmt = stmt.where(Promotion.product_id == product_id)
    rows = db.scalars(stmt.order_by(Promotion.ends_at.asc().nullslast()).limit(500)).all()
    return [PromotionResponse(
        id=str(row.id), product_id=str(row.product_id), branch_id=str(row.branch_id),
        promotional_price_eur=float(row.promotional_price_eur),
        regular_price_eur=float(row.regular_price_eur) if row.regular_price_eur is not None else None,
        starts_at=row.starts_at, ends_at=row.ends_at,
    ) for row in rows]
