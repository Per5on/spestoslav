"""Authenticated catalog, review and collection APIs. Pending data stays private."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import (
    BaseModel,
    Field,
    AwareDatetime,
    HttpUrl,
    ConfigDict,
    field_validator,
)
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .auth import Principal, admin_user, auth_base_url, collector_user, current_user
from .db import get_db
from .models import Category, Product, Retailer, StoreBranch, PriceObservation
from .marketplace import CurrentPrice, PriceCache, ProductBarcode
from .workflows import ReviewSubmission, CollectionSource, ProductImage

router = APIRouter(prefix="/api/v1")
Money = Decimal


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProductInput(Input):
    category_code: str = Field(min_length=1, max_length=40)
    barcode: str | None = Field(default=None, pattern=r"^\d{8,14}$")
    name: str = Field(min_length=2, max_length=300)
    brand: str | None = Field(default=None, max_length=160)
    package_quantity: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=3
    )
    package_unit: str | None = Field(default=None, max_length=32)

    @field_validator("barcode")
    @classmethod
    def gtin_checksum(cls, value):
        if value is None:
            return value
        if (
            len(value) not in (8, 12, 13, 14)
            or (
                sum(
                    int(n) * (3 if i % 2 == 0 else 1)
                    for i, n in enumerate(reversed(value[:-1]))
                )
                + int(value[-1])
            )
            % 10
        ):
            raise ValueError("Invalid GTIN length or check digit")
        return value


class PriceInput(Input):
    product_id: UUID
    branch_id: UUID
    price_eur: Decimal = Field(gt=0, max_digits=12, decimal_places=4)
    source_reference: str = Field(min_length=1, max_length=500)
    expires_at: AwareDatetime
    observed_at: AwareDatetime | None = None

    @field_validator("expires_at")
    @classmethod
    def future_expiry(cls, value):
        now = datetime.now(timezone.utc)
        if not now < value <= now + timedelta(days=31):
            raise ValueError("Expiry must be in the next 31 days")
        return value


class ReviewInput(Input):
    decision: str = Field(pattern="^(APPROVED|REJECTED)$")
    note: str = Field(min_length=3, max_length=2000)
    confirmed_source_reference: HttpUrl | None = None


class SourceInput(Input):
    code: str = Field(pattern="^[a-z0-9_-]{1,64}$")
    retailer_code: str = Field(min_length=1, max_length=64)
    origin: HttpUrl
    enabled: bool = False
    kind: str = Field(default="OFFICIAL", pattern="^(OFFICIAL|AGGREGATOR)$")

    @field_validator("origin")
    @classmethod
    def https_origin(cls, value):
        p = urlsplit(str(value))
        if (
            p.scheme != "https"
            or p.username
            or p.password
            or p.path not in ("", "/")
            or p.query
            or p.fragment
        ):
            raise ValueError(
                "Provide an HTTPS origin without credentials, path or query"
            )
        return value


class CollectedPrice(PriceInput):
    external_id: str = Field(min_length=1, max_length=80)
    source_code: str = Field(min_length=1, max_length=64)


class CollectionBatch(Input):
    observations: list[CollectedPrice] = Field(min_length=1, max_length=100)


def active_pair(db, product_id, branch_id):
    product = db.get(Product, product_id)
    branch = db.get(StoreBranch, branch_id)
    retailer = db.get(Retailer, branch.retailer_code) if branch else None
    category = db.get(Category, product.category_code) if product else None
    if not all(x and x.active for x in (product, branch, retailer, category)):
        raise HTTPException(
            422, "Product, branch, retailer and category must be active"
        )
    if product.category_code != retailer.category_code:
        raise HTTPException(422, "Product and retailer categories do not match")
    return product, branch


def submission_view(row, cache):
    return {
        "id": str(row.id),
        "status": cache.status,
        "product_id": str(cache.product_id),
        "branch_id": str(cache.branch_id),
        "price_eur": str(cache.submitted_price_eur),
        "expires_at": cache.expires_at,
        "source": cache.source,
        "source_reference": cache.source_reference,
        "created_at": row.created_at,
        "review_note": row.review_note,
    }


def enqueue(db, payload, principal, request_key, source):
    existing = db.scalar(
        select(ReviewSubmission).where(
            ReviewSubmission.owner_subject == principal.subject,
            ReviewSubmission.request_key == request_key,
        )
    )
    if existing:
        cache = db.get(PriceCache, existing.cache_id)
        if (
            cache.product_id,
            cache.branch_id,
            cache.submitted_price_eur,
            cache.source_reference,
        ) != (
            payload.product_id,
            payload.branch_id,
            payload.price_eur,
            payload.source_reference,
        ):
            raise HTTPException(409, "Idempotency key was used for another payload")
        expiry = cache.expires_at
        if expiry and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry != payload.expires_at:
            raise HTTPException(409, "Idempotency key expiry differs")
        return existing, cache
    active_pair(db, payload.product_id, payload.branch_id)
    now = datetime.now(timezone.utc)
    if payload.observed_at and (
        payload.observed_at > now or payload.observed_at >= payload.expires_at
    ):
        raise HTTPException(
            422, "Observation time must be in the past and before expiry"
        )
    cache = PriceCache(
        product_id=payload.product_id,
        branch_id=payload.branch_id,
        submitted_price_eur=payload.price_eur,
        source=source,
        source_reference=payload.source_reference,
        expires_at=payload.expires_at,
        status="PENDING",
        collected_at=payload.observed_at or datetime.now(timezone.utc),
    )
    db.add(cache)
    db.flush()
    row = ReviewSubmission(
        owner_subject=principal.subject, request_key=request_key, cache_id=cache.id
    )
    db.add(row)
    db.flush()
    return row, cache


@router.get("/auth/config")
def auth_config():
    return {"provider": "neon", "base_url": auth_base_url(), "token_type": "Bearer"}


@router.get("/auth/me")
def me(principal: Principal = Depends(current_user)):
    return {"subject": principal.subject, "role": principal.role}


@router.post("/admin/products", status_code=201)
def create_product(
    payload: ProductInput, principal=Depends(admin_user), db: Session = Depends(get_db)
):
    category = db.get(Category, payload.category_code)
    if not category or not category.active:
        raise HTTPException(422, "Unknown or inactive category")
    if payload.barcode is None and payload.category_code != "fuel":
        raise HTTPException(422, "A verified GTIN is required for packaged products")
    existing = (
        db.scalar(
            select(ProductBarcode).where(ProductBarcode.barcode == payload.barcode)
        )
        if payload.barcode
        else None
    )
    canonical = (
        db.scalar(select(Product).where(Product.barcode == payload.barcode))
        if payload.barcode
        else db.scalar(
            select(Product).where(
                Product.category_code == payload.category_code,
                Product.normalized_name == payload.name.casefold(),
            )
        )
    )
    if existing or canonical:
        raise HTTPException(409, "Barcode already exists")
    product = Product(
        **payload.model_dump(), normalized_name=payload.name.casefold(), active=True
    )
    db.add(product)
    db.flush()
    if payload.barcode:
        db.add(
            ProductBarcode(
                product_id=product.id,
                barcode=payload.barcode,
                source="ADMIN",
                verified=True,
            )
        )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Barcode already exists") from None
    return {"id": str(product.id), "barcode": payload.barcode, "name": product.name}


@router.post("/submissions/prices", status_code=201)
def submit_price(
    payload: PriceInput,
    idempotency_key: str = Header(min_length=8, max_length=100),
    principal=Depends(current_user),
    db: Session = Depends(get_db),
):
    try:
        row, cache = enqueue(db, payload, principal, idempotency_key, "USER")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409, "Concurrent request; retry with the same idempotency key"
        ) from None
    return submission_view(row, cache)


@router.get("/submissions")
def own_submissions(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    principal=Depends(current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(ReviewSubmission, PriceCache)
        .join(PriceCache, PriceCache.id == ReviewSubmission.cache_id)
        .where(ReviewSubmission.owner_subject == principal.subject)
        .order_by(ReviewSubmission.created_at.desc(), ReviewSubmission.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return [submission_view(r, c) for r, c in rows]


@router.get("/admin/submissions")
def review_queue(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    principal=Depends(admin_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(ReviewSubmission, PriceCache)
        .join(PriceCache, PriceCache.id == ReviewSubmission.cache_id)
        .where(PriceCache.status == "PENDING")
        .order_by(ReviewSubmission.created_at, ReviewSubmission.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return [submission_view(r, c) for r, c in rows]


@router.post("/admin/submissions/{submission_id}/review")
def review(
    submission_id: UUID,
    payload: ReviewInput,
    principal=Depends(admin_user),
    db: Session = Depends(get_db),
):
    row = db.scalar(
        select(ReviewSubmission)
        .where(ReviewSubmission.id == submission_id)
        .with_for_update()
    )
    if not row:
        raise HTTPException(404, "Submission not found")
    cache = db.get(PriceCache, row.cache_id)
    if cache.status != "PENDING":
        raise HTTPException(409, "Submission has already been reviewed")
    now = datetime.now(timezone.utc)
    expiry = cache.expires_at
    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if payload.decision == "APPROVED":
        if not expiry or expiry <= now:
            raise HTTPException(409, "Observation expired; cannot publish")
        active_pair(db, cache.product_id, cache.branch_id)
        published_source = cache.source
        published_reference = cache.source_reference
        if cache.source == "AGGREGATOR_UNKNOWN":
            evidence = str(payload.confirmed_source_reference or "")
            branch = db.get(StoreBranch, cache.branch_id)
            retailer = db.get(Retailer, branch.retailer_code)
            official = urlsplit(retailer.website_url or "").hostname
            parsed = urlsplit(evidence)
            if (
                not official
                or parsed.scheme != "https"
                or parsed.hostname != official
                or parsed.username
                or parsed.password
            ):
                raise HTTPException(
                    409,
                    "Aggregator certainty is unknown; independent official station evidence is required",
                )
            published_source = "ADMIN_VERIFIED_AGGREGATOR"
            published_reference = evidence
        # Dialect upsert prevents two approved submissions creating duplicate current prices.
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        insert = pg_insert if db.bind.dialect.name == "postgresql" else sqlite_insert
        observed = cache.collected_at
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=timezone.utc)
        values = dict(
            product_id=cache.product_id,
            branch_id=cache.branch_id,
            observed_at=observed,
            price_eur=cache.submitted_price_eur,
            source=published_source,
            verified_at=now,
            expires_at=expiry,
        )
        statement = insert(CurrentPrice).values(**values)
        published = (
            db.execute(
                statement.on_conflict_do_update(
                    index_elements=["product_id", "branch_id"],
                    set_={
                        k: v
                        for k, v in values.items()
                        if k not in ("product_id", "branch_id")
                    },
                    where=func.coalesce(
                        CurrentPrice.observed_at, CurrentPrice.verified_at
                    )
                    <= observed,
                ).returning(CurrentPrice.id)
            ).scalar_one_or_none()
            is not None
        )
        db.add(
            PriceObservation(
                product_id=cache.product_id,
                branch_id=cache.branch_id,
                price_eur=cache.submitted_price_eur,
                source=published_source,
                source_reference=published_reference,
                verified=True,
                valid_from=observed,
                valid_until=expiry,
                collected_at=observed,
            )
        )
        cache.status = "VERIFIED"
    else:
        cache.status = "REJECTED"
    cache.reviewed_at = now
    row.reviewed_by = principal.subject
    row.review_note = payload.note + (
        "\nIndependent evidence: " + str(payload.confirmed_source_reference)
        if payload.confirmed_source_reference
        else ""
    )
    db.commit()
    return dict(
        submission_view(row, cache),
        published_as_current=published if payload.decision == "APPROVED" else False,
    )


@router.post("/admin/collection-sources", status_code=201)
def register_source(
    payload: SourceInput, principal=Depends(admin_user), db: Session = Depends(get_db)
):
    retailer = db.get(Retailer, payload.retailer_code)
    if not retailer or not retailer.active:
        raise HTTPException(422, "Unknown or inactive retailer")
    if db.get(CollectionSource, payload.code):
        raise HTTPException(409, "Source code already exists")
    if (
        urlsplit(str(payload.origin)).hostname in ("api.fuelo.net", "bg.fuelo.net")
        and payload.kind != "AGGREGATOR"
    ):
        raise HTTPException(
            422, "Fuelo is an aggregator, not an official retailer source"
        )
    source = CollectionSource(
        **payload.model_dump(exclude={"origin"}), origin=str(payload.origin).rstrip("/")
    )
    db.add(source)
    db.commit()
    return {"code": source.code, "origin": source.origin, "enabled": source.enabled}


@router.post("/collector/observations", status_code=201)
def ingest(
    payload: CollectionBatch,
    principal=Depends(collector_user),
    db: Session = Depends(get_db),
):
    results = []
    for item in payload.observations:
        source = db.get(CollectionSource, item.source_code)
        if not source or not source.enabled:
            raise HTTPException(422, "Source is not approved and enabled")
        reference = urlsplit(item.source_reference)
        if (
            reference.scheme != "https"
            or reference.username
            or reference.password
            or (reference.scheme, reference.netloc)
            != (urlsplit(source.origin).scheme, urlsplit(source.origin).netloc)
        ):
            raise HTTPException(
                422, "Evidence URL must match the approved source origin"
            )
        product, branch = active_pair(db, item.product_id, item.branch_id)
        if branch.retailer_code != source.retailer_code:
            raise HTTPException(422, "Source does not match branch retailer")
        key = hashlib.sha256(
            (item.source_code + "|" + item.external_id).encode()
        ).hexdigest()
        row, cache = enqueue(
            db,
            item,
            principal,
            key,
            "AGGREGATOR_UNKNOWN" if source.kind == "AGGREGATOR" else "RETAILER",
        )
        results.append(submission_view(row, cache))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent duplicate; retry batch") from None
    return results


@router.get("/products")
def browse_products(
    q: str = Query(default="", max_length=80),
    category_code: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    statement = (
        select(Product, ProductImage.image_url)
        .outerjoin(ProductImage, ProductImage.product_id == Product.id)
        .join(Category, Category.code == Product.category_code)
        .where(Product.active.is_(True), Category.active.is_(True))
    )
    if category_code:
        statement = statement.where(Product.category_code == category_code)
    if q.strip():
        statement = statement.where(
            Product.normalized_name.contains(q.strip().casefold(), autoescape=True)
        )
    rows = db.execute(
        statement.order_by(Product.name, Product.id).offset(offset).limit(limit)
    ).all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "category_code": p.category_code,
            "brand": p.brand,
            "package_quantity": str(p.package_quantity)
            if p.package_quantity is not None
            else None,
            "package_unit": p.package_unit,
            "barcode": p.barcode,
            "image_url": image_url,
        }
        for p, image_url in rows
    ]


@router.get("/admin/receipts/{scan_id}")
def receipt_for_review(
    scan_id: UUID, principal=Depends(admin_user), db: Session = Depends(get_db)
):
    from .marketplace import ReceiptScan, ReceiptItem
    from .workflows import ReceiptJob

    row = db.execute(
        select(ReceiptJob, ReceiptScan)
        .join(ReceiptScan, ReceiptScan.id == ReceiptJob.scan_id)
        .where(ReceiptJob.scan_id == scan_id)
    ).first()
    if not row:
        raise HTTPException(404, "Receipt not found")
    job, scan = row
    return {
        "id": str(scan.id),
        "status": scan.status,
        "extracted_text": scan.extracted_text,
        "items": [
            {
                "id": str(i.id),
                "description": i.raw_description,
                "line_total_eur": str(i.line_total_eur) if i.line_total_eur else None,
            }
            for i in db.scalars(
                select(ReceiptItem).where(ReceiptItem.receipt_scan_id == scan.id)
            ).all()
        ],
    }
