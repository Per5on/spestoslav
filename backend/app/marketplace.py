import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class ProductBarcode(Base):
    __tablename__ = "product_barcodes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    barcode: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="ADMIN")
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class CurrentPrice(Base):
    __tablename__ = "current_prices"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("store_branches.id", ondelete="CASCADE"), nullable=False)
    price_eur: Mapped[Decimal] = mapped_column(Numeric(12,4), nullable=False)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("product_id","branch_id",name="uq_current_price_product_branch"), CheckConstraint("price_eur > 0",name="ck_current_price_positive"))

class PriceCache(Base):
    __tablename__ = "price_cache"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("store_branches.id", ondelete="SET NULL"))
    raw_product_description: Mapped[str | None] = mapped_column(String(400))
    submitted_price_eur: Mapped[Decimal] = mapped_column(Numeric(12,4), nullable=False)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("submitted_price_eur > 0",name="ck_price_cache_positive"), CheckConstraint("status IN ('PENDING','VERIFIED','REJECTED','EXPIRED')",name="ck_price_cache_status"))

class Promotion(Base):
    __tablename__ = "promotions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("store_branches.id", ondelete="CASCADE"), nullable=False)
    promotional_price_eur: Mapped[Decimal] = mapped_column(Numeric(12,4), nullable=False)
    regular_price_eur: Mapped[Decimal | None] = mapped_column(Numeric(12,4))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    __table_args__ = (CheckConstraint("promotional_price_eur > 0",name="ck_promotion_price_positive"), CheckConstraint("regular_price_eur IS NULL OR regular_price_eur > 0",name="ck_promotion_regular_price_positive"))

class ReceiptScan(Base):
    __tablename__ = "receipt_scans"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="UPLOADED")
    extracted_text: Mapped[str | None] = mapped_column(Text)
    branch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("store_branches.id", ondelete="SET NULL"))
    receipt_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("receipt_scans.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"))
    raw_description: Mapped[str] = mapped_column(String(400), nullable=False)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12,3))
    unit_price_eur: Mapped[Decimal | None] = mapped_column(Numeric(12,4))
    line_total_eur: Mapped[Decimal | None] = mapped_column(Numeric(12,4))
    match_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5,4))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="UNMATCHED")
