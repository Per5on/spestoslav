"""Additive workflow tables, shared by fresh installs and legacy preview."""

import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class ReviewSubmission(Base):
    __tablename__ = "review_submissions"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_subject: Mapped[str] = mapped_column(String(200), nullable=False)
    request_key: Mapped[str] = mapped_column(String(100), nullable=False)
    cache_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("price_cache.id"), nullable=False, unique=True
    )
    reviewed_by: Mapped[str | None] = mapped_column(String(200))
    review_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        UniqueConstraint("owner_subject", "request_key", name="uq_review_request"),
        Index("ix_review_owner", "owner_subject", "created_at"),
    )


class CollectionSource(Base):
    __tablename__ = "collection_sources"
    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    retailer_code: Mapped[str] = mapped_column(
        ForeignKey("catalog_retailers.code"), nullable=False
    )
    origin: Mapped[str] = mapped_column(String(500), nullable=False)
    kind: Mapped[str] = mapped_column(
        String(24), nullable=False, default="OFFICIAL", server_default="OFFICIAL"
    )
    enabled: Mapped[bool] = mapped_column(nullable=False, default=False)


class ReceiptJob(Base):
    __tablename__ = "receipt_jobs"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("receipt_scans.id"), nullable=False, unique=True
    )
    owner_subject: Mapped[str] = mapped_column(String(200), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(String(300))
    request_key: Mapped[str | None] = mapped_column(String(100))
    upload_fingerprint: Mapped[str | None] = mapped_column(String(64))
    __table_args__ = (Index("ix_receipt_job_owner", "owner_subject"), Index("uq_receipt_upload_request", "owner_subject", "request_key", unique=True))


class ProductIdentificationRequest(Base):
    __tablename__ = "product_identification_requests"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_subject: Mapped[str] = mapped_column(String(200), nullable=False)
    barcode: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.id"))
    reviewed_by: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        UniqueConstraint(
            "owner_subject", "barcode", name="uq_identification_owner_barcode"
        ),
    )


class ProductImage(Base):
    __tablename__ = "product_images"
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), primary_key=True
    )
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)


class NationalOffer(Base):
    __tablename__ = "national_offers"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    retailer_code: Mapped[str] = mapped_column(
        ForeignKey("catalog_retailers.code"), nullable=False
    )
    price_eur: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(1000), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    verified_by: Mapped[str] = mapped_column(String(200), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    __table_args__ = (
        Index(
            "ix_national_offer_product_retailer",
            "product_id",
            "retailer_code",
            "observed_at",
        ),
    )
