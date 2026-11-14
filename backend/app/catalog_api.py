"""Catalog and price scope contracts shared by the upcoming Android screens."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime, Field, HttpUrl, field_validator
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .auth import admin_user, current_user
from .db import get_db
from .models import Category, Product, Retailer, StoreBranch, PriceObservation
from .marketplace import CurrentPrice, ProductBarcode
from .workflows import ProductIdentificationRequest, ProductImage, NationalOffer
from .write_api import Input, ProductInput, PriceInput

router = APIRouter(prefix="/api/v1")


class IdentificationInput(Input):
    barcode: str = Field(pattern=r"^\d{8,14}$")
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("barcode")
    @classmethod
    def validate_gtin(cls, value):
        return ProductInput.gtin_checksum(value)


class IdentificationReview(Input):
    product_id: UUID


class ImageInput(Input):
    image_url: HttpUrl
    source_url: HttpUrl

    @field_validator("image_url", "source_url")
    @classmethod
    def https(cls, value):
        if value.scheme != "https" or value.username or value.password:
            raise ValueError("HTTPS without credentials required")
        if len(str(value)) > 1000:
            raise ValueError("URL too long")
        return value


class NationalOfferInput(Input):
    product_id: UUID
    retailer_code: str = Field(min_length=1, max_length=64)
    price_eur: Decimal = Field(gt=0, max_digits=12, decimal_places=4)
    source_reference: HttpUrl
    observed_at: AwareDatetime
    valid_until: AwareDatetime


@router.post("/product-identification-requests", status_code=201)
def identify(
    payload: IdentificationInput,
    principal=Depends(current_user),
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(ProductIdentificationRequest).where(
            ProductIdentificationRequest.owner_subject == principal.subject,
            ProductIdentificationRequest.barcode == payload.barcode,
        )
    )
    if existing:
        return {"id": str(existing.id), "status": existing.status}
    request = ProductIdentificationRequest(
        owner_subject=principal.subject, **payload.model_dump()
    )
    db.add(request)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Request already exists; retry") from None
    return {"id": str(request.id), "status": request.status}


@router.get("/product-identification-requests")
def own_identifications(
    principal=Depends(current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rows = db.scalars(
        select(ProductIdentificationRequest)
        .where(ProductIdentificationRequest.owner_subject == principal.subject)
        .order_by(
            ProductIdentificationRequest.created_at.desc(),
            ProductIdentificationRequest.id,
        )
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        {
            "id": str(r.id),
            "barcode": r.barcode,
            "status": r.status,
            "product_id": str(r.product_id) if r.product_id else None,
        }
        for r in rows
    ]


@router.get("/admin/product-identification-requests")
def identification_queue(
    principal=Depends(admin_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rows = db.scalars(
        select(ProductIdentificationRequest)
        .where(ProductIdentificationRequest.status == "PENDING")
        .order_by(
            ProductIdentificationRequest.created_at, ProductIdentificationRequest.id
        )
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        {"id": str(r.id), "barcode": r.barcode, "description": r.description}
        for r in rows
    ]


@router.post("/admin/product-identification-requests/{request_id}/resolve")
def resolve_identification(
    request_id: UUID,
    payload: IdentificationReview,
    principal=Depends(admin_user),
    db: Session = Depends(get_db),
):
    request = db.scalar(
        select(ProductIdentificationRequest)
        .where(ProductIdentificationRequest.id == request_id)
        .with_for_update()
    )
    if not request:
        raise HTTPException(404, "Identification request not found")
    if request.status != "PENDING":
        raise HTTPException(409, "Request already resolved")
    product = db.get(Product, payload.product_id)
    if not product or not product.active:
        raise HTTPException(422, "Unknown or inactive product")
    canonical = db.scalar(select(Product).where(Product.barcode == request.barcode))
    alias = db.scalar(
        select(ProductBarcode).where(ProductBarcode.barcode == request.barcode)
    )
    if (canonical and canonical.id != product.id) or (
        alias and alias.product_id != product.id
    ):
        raise HTTPException(409, "Barcode belongs to another product")
    if alias:
        alias.verified = True
        alias.source = "ADMIN"
    else:
        db.add(
            ProductBarcode(
                product_id=product.id,
                barcode=request.barcode,
                source="ADMIN",
                verified=True,
            )
        )
    request.status = "RESOLVED"
    request.product_id = product.id
    request.reviewed_by = principal.subject
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent barcode update; review again") from None
    return {
        "id": str(request.id),
        "status": request.status,
        "product_id": str(product.id),
    }


@router.put("/admin/products/{product_id}/image")
def set_product_image(
    product_id: UUID,
    payload: ImageInput,
    principal=Depends(admin_user),
    db: Session = Depends(get_db),
):
    if not db.get(Product, product_id):
        raise HTTPException(404, "Product not found")
    image = db.get(ProductImage, product_id)
    if image:
        image.image_url = str(payload.image_url)
        image.source_url = str(payload.source_url)
    else:
        db.add(
            ProductImage(
                product_id=product_id,
                image_url=str(payload.image_url),
                source_url=str(payload.source_url),
            )
        )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent image update; retry") from None
    return {"product_id": str(product_id), "image_url": str(payload.image_url)}


@router.get("/catalog")
def catalog(
    locality_id: UUID | None = None,
    category_code: str | None = None,
    db: Session = Depends(get_db),
):
    categories = db.scalars(
        select(Category)
        .where(Category.active.is_(True))
        .order_by(Category.sort_order, Category.code)
    ).all()
    statement = (
        select(Retailer)
        .join(Category, Category.code == Retailer.category_code)
        .where(Retailer.active.is_(True), Category.active.is_(True))
    )
    if category_code:
        statement = statement.where(Retailer.category_code == category_code)
    if locality_id:
        statement = statement.where(
            select(StoreBranch.id)
            .where(
                StoreBranch.retailer_code == Retailer.code,
                StoreBranch.locality_id == locality_id,
                StoreBranch.active.is_(True),
            )
            .exists()
        )
    retailers = db.scalars(statement.order_by(Retailer.name)).all()
    return {
        "categories": [
            {"code": c.code, "name_bg": c.name_bg, "name_en": c.name_en}
            for c in categories
        ],
        "retailers": [
            {
                "code": r.code,
                "name": r.name,
                "category_code": r.category_code,
                "website_url": r.website_url,
            }
            for r in retailers
        ],
    }


@router.post("/admin/national-offers", status_code=201)
def create_national_offer(
    payload: NationalOfferInput,
    principal=Depends(admin_user),
    db: Session = Depends(get_db),
):
    from urllib.parse import urlsplit

    now = datetime.now(timezone.utc)
    product = db.get(Product, payload.product_id)
    retailer = db.get(Retailer, payload.retailer_code)
    category = db.get(Category, product.category_code) if product else None
    if (
        not all(x and x.active for x in (product, retailer, category))
        or product.category_code != retailer.category_code
    ):
        raise HTTPException(
            422, "Active product, retailer and matching category required"
        )
    official = urlsplit(retailer.website_url or "").hostname
    source = urlsplit(str(payload.source_reference))
    if (
        not official
        or source.scheme != "https"
        or source.hostname != official
        or source.username
        or source.password
    ):
        raise HTTPException(422, "An official retailer evidence URL is required")
    from datetime import timedelta

    if (
        not payload.observed_at <= now < payload.valid_until <= now + timedelta(days=31)
        or payload.observed_at >= payload.valid_until
    ):
        raise HTTPException(
            422, "Offer must have a past observation and future expiry within 31 days"
        )
    offer = NationalOffer(
        **payload.model_dump(exclude={"source_reference"}),
        source_reference=str(payload.source_reference),
        verified_at=now,
        verified_by=principal.subject,
    )
    db.add(offer)
    db.commit()
    return {"id": str(offer.id), "price_scope": "NATIONAL_ONLINE", "branch_id": None}


def national_rows(db, product_id=None, retailer_code=None):
    now = datetime.now(timezone.utc)
    ranks = (
        select(
            NationalOffer.id,
            func.row_number()
            .over(
                partition_by=(NationalOffer.product_id, NationalOffer.retailer_code),
                order_by=(
                    NationalOffer.observed_at.desc(),
                    NationalOffer.verified_at.desc(),
                    NationalOffer.id,
                ),
            )
            .label("rank"),
        )
        .where(
            NationalOffer.valid_until > now,
            NationalOffer.observed_at <= now,
            NationalOffer.verified_at <= now,
        )
        .subquery()
    )
    statement = (
        select(NationalOffer)
        .join(ranks, ranks.c.id == NationalOffer.id)
        .join(Product, Product.id == NationalOffer.product_id)
        .join(Retailer, Retailer.code == NationalOffer.retailer_code)
        .join(Category, Category.code == Product.category_code)
        .where(
            ranks.c.rank == 1,
            Product.active.is_(True),
            Retailer.active.is_(True),
            Category.active.is_(True),
        )
    )
    if product_id:
        statement = statement.where(NationalOffer.product_id == product_id)
    if retailer_code:
        statement = statement.where(NationalOffer.retailer_code == retailer_code)
    return statement


@router.get("/national-offers")
def national_offers(
    product_id: UUID | None = None,
    retailer_code: str | None = None,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rows = db.scalars(
        national_rows(db, product_id, retailer_code)
        .order_by(NationalOffer.product_id, NationalOffer.retailer_code)
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        {
            "id": str(o.id),
            "product_id": str(o.product_id),
            "retailer_code": o.retailer_code,
            "price_eur": str(o.price_eur),
            "price_scope": "NATIONAL_ONLINE",
            "branch_id": None,
            "observed_at": o.observed_at,
            "verified_at": o.verified_at,
            "valid_until": o.valid_until,
            "source_reference": o.source_reference,
        }
        for o in rows
    ]


@router.get("/prices/history")
def price_history(
    product_id: UUID,
    branch_id: UUID | None = None,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    statement = select(PriceObservation).where(
        PriceObservation.product_id == product_id, PriceObservation.verified.is_(True)
    )
    if branch_id:
        statement = statement.where(PriceObservation.branch_id == branch_id)
    rows = db.scalars(
        statement.order_by(PriceObservation.collected_at.desc(), PriceObservation.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        {
            "id": str(p.id),
            "product_id": str(p.product_id),
            "branch_id": str(p.branch_id),
            "price_scope": "BRANCH",
            "price_eur": str(p.price_eur),
            "observed_at": p.collected_at,
            "valid_from": p.valid_from,
            "valid_until": p.valid_until,
            "source": p.source,
            "source_reference": p.source_reference,
        }
        for p in rows
    ]


class BasketItem(Input):
    product_id: UUID
    quantity: Decimal = Field(
        default=Decimal("1"), gt=0, le=1000, max_digits=7, decimal_places=3
    )


class BasketInput(Input):
    locality_id: UUID
    items: list[BasketItem] = Field(min_length=1, max_length=100)
    include_online: bool = False


@router.post("/baskets/compare")
def compare_basket(payload: BasketInput, db: Session = Depends(get_db)):
    from .models import Locality
    from .marketplace import Promotion

    product_ids = [i.product_id for i in payload.items]
    if len(set(product_ids)) != len(product_ids):
        raise HTTPException(422, "Combine repeated product IDs into one quantity")
    if not db.get(Locality, payload.locality_id):
        raise HTTPException(422, "Unknown locality")
    products = db.scalars(
        select(Product)
        .join(Category, Category.code == Product.category_code)
        .where(
            Product.id.in_(product_ids),
            Product.active.is_(True),
            Category.active.is_(True),
        )
    ).all()
    if len(products) != len(product_ids):
        raise HTTPException(422, "Unknown or inactive product")
    categories = {p.category_code for p in products}
    if len(categories) != 1:
        raise HTTPException(422, "Compare one category per basket")
    branches = db.scalars(
        select(StoreBranch)
        .join(Retailer, Retailer.code == StoreBranch.retailer_code)
        .where(
            StoreBranch.locality_id == payload.locality_id,
            StoreBranch.active.is_(True),
            Retailer.active.is_(True),
            Retailer.category_code == next(iter(categories)),
        )
    ).all()
    branch_ids = [b.id for b in branches]
    now = datetime.now(timezone.utc)
    prices = db.scalars(
        select(CurrentPrice).where(
            CurrentPrice.branch_id.in_(branch_ids),
            CurrentPrice.product_id.in_(product_ids),
            CurrentPrice.verified_at <= now,
            (CurrentPrice.expires_at.is_(None)) | (CurrentPrice.expires_at > now),
        )
    ).all()
    values = {(p.branch_id, p.product_id): p.price_eur for p in prices}
    promotions = db.scalars(
        select(Promotion).where(
            Promotion.branch_id.in_(branch_ids),
            Promotion.product_id.in_(product_ids),
            Promotion.verified.is_(True),
            Promotion.starts_at <= now,
            (Promotion.ends_at.is_(None)) | (Promotion.ends_at > now),
        )
    ).all()
    for promotion in promotions:
        key = (promotion.branch_id, promotion.product_id)
        values[key] = min(
            values.get(key, promotion.promotional_price_eur),
            promotion.promotional_price_eur,
        )
    quotes = []

    def quote(scope, identity, retailer, product_prices):
        missing = [
            str(i.product_id)
            for i in payload.items
            if i.product_id not in product_prices
        ]
        total = (
            None
            if missing
            else sum(
                (i.quantity * product_prices[i.product_id] for i in payload.items),
                Decimal("0"),
            )
        )
        return {
            "price_scope": scope,
            "branch_id": str(identity) if identity else None,
            "retailer_code": retailer,
            "complete": not missing,
            "missing_product_ids": missing,
            "total_eur": str(total) if total is not None else None,
        }

    for branch in branches:
        quotes.append(
            quote(
                "BRANCH",
                branch.id,
                branch.retailer_code,
                {p: price for (b, p), price in values.items() if b == branch.id},
            )
        )
    if payload.include_online:
        offers = db.scalars(
            national_rows(db).where(NationalOffer.product_id.in_(product_ids))
        ).all()
        online = {}
        for offer in offers:
            online.setdefault(offer.retailer_code, {})[offer.product_id] = (
                offer.price_eur
            )
        for retailer, product_prices in online.items():
            quotes.append(quote("NATIONAL_ONLINE", None, retailer, product_prices))
    quotes.sort(
        key=lambda q: (
            not q["complete"],
            Decimal(q["total_eur"]) if q["complete"] else Decimal("Infinity"),
            q["retailer_code"],
            q["branch_id"] or "",
        )
    )
    return {
        "currency": "EUR",
        "quotes": quotes,
        "cheapest": quotes[0] if quotes and quotes[0]["complete"] else None,
        "shipping_and_travel_included": False,
    }
