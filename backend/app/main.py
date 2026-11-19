from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, load_only

from .db import get_db
from .grocery import GroceryGroup, GroceryIdentity
from .technology import TechnologyGroup, TechnologyIdentity
from .barcodes import gtin_aliases
from .models import (
    Category,
    Locality,
    Product,
    Retailer,
    StoreBranch,
)
from .marketplace import CurrentPrice, ProductBarcode, Promotion
from .workflows import (
    ReviewSubmission,
    ReceiptJob,
    CollectionSource,
    ProductImage,
    NationalOffer,
    ProductIdentificationRequest,
)

app = FastAPI(title="Спестослав API", version="0.6.0")


class CategoryResponse(BaseModel):
    code: str
    name_bg: str
    name_en: str


class LocalityResponse(BaseModel):
    id: str
    name: str
    name_bg: str | None = None
    name_latin: str | None = None
    # Empty compatibility field for APK 001/002; there is no postal search/storage.
    postal_codes: list[str] = Field(default_factory=list, deprecated=True)
    type: str
    municipality: str | None = None
    region: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "spestoslav-api"}


@app.get("/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        # Verify the actual API projections, not just TCP connectivity.
        for statement in (
            select(Category).limit(1),
            select(Locality.id, Locality.name_bg, Locality.name_latin).limit(1),
            select(StoreBranch).limit(1),
            select(Product).limit(1),
            select(CurrentPrice).limit(1),
            select(Promotion).limit(1),
            select(ReviewSubmission.id).limit(1),
            select(
                ReceiptJob.id, ReceiptJob.request_key, ReceiptJob.upload_fingerprint
            ).limit(1),
            select(CollectionSource.code).limit(1),
            select(ProductImage.product_id).limit(1),
            select(NationalOffer.id).limit(1),
            select(ProductIdentificationRequest.id).limit(1),
            select(GroceryGroup.code).limit(1),
            select(GroceryIdentity.product_id).limit(1),
            select(TechnologyIdentity.product_id).limit(1),
        ):
            db.execute(statement)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=503, detail="Database is not ready") from None
    return {"status": "ready", "service": "spestoslav-api"}


@app.get("/api/v1/categories", response_model=list[CategoryResponse])
def categories(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Category).where(Category.active.is_(True)).order_by(Category.sort_order)
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
    names_and_terms = (
        (func.lower(Locality.name), latin_terms),
        (func.lower(func.coalesce(Locality.name_latin, "")), latin_terms),
        (func.lower(func.coalesce(Locality.name_bg, "")), {normalized}),
    )
    matches = [(name, value) for name, terms in names_and_terms for value in terms]
    contains = or_(*(name.contains(value, autoescape=True) for name, value in matches))
    prefix = or_(*(name.startswith(value, autoescape=True) for name, value in matches))
    display_name = func.lower(func.coalesce(func.nullif(Locality.name_bg, ""), Locality.name))

    localities = db.scalars(
        select(Locality)
        .options(
            load_only(
                Locality.id,
                Locality.name,
                Locality.name_bg,
                Locality.name_latin,
                Locality.type,
                Locality.municipality,
                Locality.region,
            )
        )
        .where(Locality.on_map.is_(True))
        .where(contains)
        .order_by(
            prefix.desc(),
            display_name,
            Locality.name,
            Locality.id,
        )
        .limit(20)
    ).all()

    return [
        LocalityResponse(
            id=str(locality.id),
            name=locality.name,
            name_bg=locality.name_bg,
            name_latin=locality.name_latin,
            type=locality.type,
            municipality=locality.municipality,
            region=locality.region,
        )
        for locality in localities
    ]


class ProductLookupResponse(BaseModel):
    id: str
    category_code: str
    name: str
    brand: str | None = None
    variant: str | None = None
    package_quantity: float | None = None
    package_unit: str | None = None
    image_url: str | None = None
    barcodes: list[str] = Field(default_factory=list)


class StoreBranchResponse(BaseModel):
    id: str
    retailer_code: str
    retailer_name: str
    locality_id: str
    locality_name: str
    branch_name: str | None = None
    address: str


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
    try:
        aliases = gtin_aliases(barcode)
    except ValueError:
        raise HTTPException(422, "Invalid GTIN length or check digit") from None
    products = db.scalars(
        select(Product)
        .join(Category, Category.code == Product.category_code)
        .outerjoin(ProductBarcode, ProductBarcode.product_id == Product.id)
        .where(
            Product.active.is_(True),
            Category.active.is_(True),
            or_(
                Product.barcode.in_(aliases),
                (ProductBarcode.barcode.in_(aliases))
                & ProductBarcode.verified.is_(True),
            ),
        )
        .distinct()
        .limit(2)
    ).all()
    if len(products) > 1:
        raise HTTPException(409, "Barcode identity conflict requires review")
    product = products[0] if products else None
    if product is None:
        raise HTTPException(
            status_code=404, detail="Product not found for this barcode"
        )
    codes = db.scalars(
        select(ProductBarcode.barcode)
        .where(
            ProductBarcode.product_id == product.id, ProductBarcode.verified.is_(True)
        )
        .order_by(ProductBarcode.barcode)
    ).all()
    if product.barcode and product.barcode not in codes:
        codes.append(product.barcode)
    return ProductLookupResponse(
        id=str(product.id),
        category_code=product.category_code,
        name=product.name,
        brand=product.brand,
        variant=product.variant,
        package_quantity=float(product.package_quantity)
        if product.package_quantity is not None
        else None,
        package_unit=product.package_unit,
        barcodes=codes,
        image_url=(
            image.image_url if (image := db.get(ProductImage, product.id)) else None
        ),
    )


class MerchantDirectoryEntry(BaseModel):
    """One sourced, active physical merchant branch for directory browsing."""

    id: str
    category_code: str
    retailer_code: str
    retailer_name: str
    locality_id: str
    locality_name: str
    municipality: str | None = None
    region: str | None = None
    branch_name: str | None = None
    address: str


@app.get("/api/v1/merchant-directory", response_model=list[MerchantDirectoryEntry])
def merchant_directory(
    locality_id: UUID | None = None,
    region: str | None = Query(default=None, max_length=160),
    category_code: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """National, bounded pages; optional locality/region/category filters.

    An unfiltered page is allowed for the all-merchants menu. Only real,
    active branches with active retailers and categories are included.
    """
    stmt = (
        select(
            StoreBranch, Retailer.name, Retailer.category_code,
            Locality.name_bg, Locality.name, Locality.municipality, Locality.region,
        )
        .join(Retailer, Retailer.code == StoreBranch.retailer_code)
        .join(Category, Category.code == Retailer.category_code)
        .join(Locality, Locality.id == StoreBranch.locality_id)
        .where(
            StoreBranch.active.is_(True),
            Retailer.active.is_(True),
            Category.active.is_(True),
        )
    )
    if locality_id is not None:
        stmt = stmt.where(StoreBranch.locality_id == locality_id)
    if region:
        stmt = stmt.where(Locality.region == region)
    if category_code:
        stmt = stmt.where(Retailer.category_code == category_code)
    rows = db.execute(
        stmt.order_by(
            Retailer.category_code,
            Locality.region,
            Locality.municipality,
            func.coalesce(Locality.name_bg, Locality.name),
            Retailer.name,
            StoreBranch.address,
            StoreBranch.id,
        )
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        MerchantDirectoryEntry(
            id=str(branch.id),
            category_code=category,
            retailer_code=branch.retailer_code,
            retailer_name=retailer_name,
            locality_id=str(branch.locality_id),
            locality_name=name_bg or locality_name,
            municipality=municipality,
            region=branch_region,
            branch_name=branch.branch_name,
            address=branch.address,
        )
        for branch, retailer_name, category, name_bg, locality_name,
            municipality, branch_region in rows
    ]


@app.get("/api/v1/stores", response_model=list[StoreBranchResponse])
def stores_for_locality(
    locality_id: UUID | None = None,
    region: str | None = Query(default=None, max_length=160),
    category_code: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    if locality_id is None and not region:
        raise HTTPException(422, "Provide a canonical locality_id or region")
    rows = db.execute(
        select(StoreBranch, Retailer.name, Locality.name_bg, Locality.name)
        .join(Retailer, Retailer.code == StoreBranch.retailer_code)
        .join(Locality, Locality.id == StoreBranch.locality_id)
        .where(StoreBranch.active.is_(True), Retailer.active.is_(True))
        .where(
            StoreBranch.locality_id == locality_id
            if locality_id
            else Locality.region == region
        )
        .where(Retailer.category_code == category_code if category_code else True)
        .order_by(Retailer.name, StoreBranch.address, StoreBranch.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        StoreBranchResponse(
            id=str(branch.id),
            retailer_code=branch.retailer_code,
            retailer_name=retailer_name,
            locality_id=str(branch.locality_id),
            locality_name=name_bg or locality_name,
            branch_name=branch.branch_name,
            address=branch.address,
        )
        for branch, retailer_name, name_bg, locality_name in rows
    ]


@app.get("/api/v1/prices/current", response_model=list[CurrentPriceResponse])
def current_prices(
    product_id: UUID | None = None,
    branch_id: UUID | None = None,
    locality_id: UUID | None = None,
    limit: int = Query(default=500, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = (
        select(CurrentPrice)
        .join(StoreBranch, StoreBranch.id == CurrentPrice.branch_id)
        .join(Retailer, Retailer.code == StoreBranch.retailer_code)
        .join(Product, Product.id == CurrentPrice.product_id)
        .join(Category, Category.code == Product.category_code)
        .where(
            StoreBranch.active.is_(True),
            Retailer.active.is_(True),
            Product.active.is_(True),
            Category.active.is_(True),
        )
    )
    if product_id:
        stmt = stmt.where(CurrentPrice.product_id == product_id)
    if branch_id:
        stmt = stmt.where(CurrentPrice.branch_id == branch_id)
    if locality_id:
        stmt = stmt.where(StoreBranch.locality_id == locality_id)
    now = datetime.now(timezone.utc)
    rows = db.scalars(
        stmt.where(
            CurrentPrice.verified_at <= now,
            or_(CurrentPrice.expires_at.is_(None), CurrentPrice.expires_at > now),
        )
        .order_by(CurrentPrice.verified_at.desc(), CurrentPrice.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        CurrentPriceResponse(
            id=str(row.id),
            product_id=str(row.product_id),
            branch_id=str(row.branch_id),
            price_eur=float(row.price_eur),
            source=row.source,
            verified_at=row.verified_at,
            expires_at=row.expires_at,
        )
        for row in rows
    ]


@app.get("/api/v1/promotions", response_model=list[PromotionResponse])
def active_promotions(
    locality_id: UUID | None = None,
    branch_id: UUID | None = None,
    product_id: UUID | None = None,
    limit: int = Query(default=500, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    stmt = (
        select(Promotion)
        .join(StoreBranch, StoreBranch.id == Promotion.branch_id)
        .join(Retailer, Retailer.code == StoreBranch.retailer_code)
        .join(Product, Product.id == Promotion.product_id)
        .join(Category, Category.code == Product.category_code)
    ).where(
        Retailer.active.is_(True),
        Product.active.is_(True),
        Category.active.is_(True),
        Promotion.verified.is_(True),
        Promotion.starts_at <= now,
        or_(Promotion.ends_at.is_(None), Promotion.ends_at >= now),
        StoreBranch.active.is_(True),
    )
    if locality_id:
        stmt = stmt.where(StoreBranch.locality_id == locality_id)
    if branch_id:
        stmt = stmt.where(Promotion.branch_id == branch_id)
    if product_id:
        stmt = stmt.where(Promotion.product_id == product_id)
    rows = db.scalars(
        stmt.order_by(Promotion.ends_at.asc().nullslast(), Promotion.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        PromotionResponse(
            id=str(row.id),
            product_id=str(row.product_id),
            branch_id=str(row.branch_id),
            promotional_price_eur=float(row.promotional_price_eur),
            regular_price_eur=float(row.regular_price_eur)
            if row.regular_price_eur is not None
            else None,
            starts_at=row.starts_at,
            ends_at=row.ends_at,
        )
        for row in rows
    ]


@app.get("/api/v1/grocery/groups")
def grocery_groups(db: Session = Depends(get_db)):
    rows = db.execute(
        select(GroceryGroup, func.count(GroceryIdentity.product_id))
        .outerjoin(GroceryIdentity, GroceryIdentity.group_code == GroceryGroup.code)
        .group_by(GroceryGroup.code)
        .order_by(GroceryGroup.sort_order, GroceryGroup.code)
    ).all()
    return [
        {"code": g.code, "name_bg": g.name_bg, "name_en": g.name_en, "count": count}
        for g, count in rows
    ]


def include_routers(application):
    from .write_api import router as write_router
    from .receipts import router as receipt_router
    from .catalog_api import router as catalog_router
    from .demo_api import router as demo_router
    from .worker_api import router as worker_router
    from .mobile_auth import router as mobile_auth_router
    from .feedback import router as feedback_router
    from .account import router as account_router
    from .thumbnails import router as thumbnail_router
    from .limits import ReceiptUploadLimit

    for router in (
        write_router,
        receipt_router,
        catalog_router,
        demo_router,
        worker_router,
        mobile_auth_router,
        feedback_router,
        account_router,
        thumbnail_router,
    ):
        application.include_router(router)
    application.add_middleware(ReceiptUploadLimit)


include_routers(app)


@app.middleware("http")
async def private_response_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(
        ("/api/v1/auth/", "/api/v1/receipts", "/api/v1/account")
    ):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
    return response
