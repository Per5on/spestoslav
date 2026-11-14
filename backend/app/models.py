import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Category(Base):
    __tablename__ = "product_categories"
    code: Mapped[str] = mapped_column(String(40), primary_key=True)
    name_bg: Mapped[str] = mapped_column(String(120), nullable=False)
    name_en: Mapped[str] = mapped_column(String(120), nullable=False)
    description_bg: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    description_en: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class Locality(Base):
    __tablename__ = "inhabited_localities"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    name_bg: Mapped[str | None] = mapped_column(String(180))
    name_latin: Mapped[str | None] = mapped_column(String(180))
    municipality_code: Mapped[str | None] = mapped_column(String(20))
    region_code: Mapped[str | None] = mapped_column(String(12))
    postal_code: Mapped[str | None] = mapped_column(String(12))
    type: Mapped[str] = mapped_column(String(24), nullable=False, default="OTHER")
    municipality: Mapped[str | None] = mapped_column(String(160))
    region: Mapped[str | None] = mapped_column(String(160))
    on_map: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_inhabited_locality_source"),)

class Retailer(Base):
    __tablename__ = "catalog_retailers"
    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category_code: Mapped[str] = mapped_column(ForeignKey("product_categories.code"), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(500))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_code: Mapped[str] = mapped_column(ForeignKey("product_categories.code"), nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(64))
    brand: Mapped[str | None] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    variant: Mapped[str | None] = mapped_column(String(200))
    package_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    package_unit: Mapped[str | None] = mapped_column(String(32))
    normalized_name: Mapped[str] = mapped_column(String(400), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class StoreBranch(Base):
    __tablename__ = "store_branches"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    retailer_code: Mapped[str] = mapped_column(ForeignKey("catalog_retailers.code"), nullable=False)
    locality_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inhabited_localities.id"), nullable=False)
    branch_name: Mapped[str | None] = mapped_column(String(160))
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(12))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="MANUAL")
    source_id: Mapped[str | None] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class PriceObservation(Base):
    __tablename__ = "price_observations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("store_branches.id"), nullable=False)
    price_eur: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    regular_price_eur: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(500))
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class UserSubmission(Base):
    __tablename__ = "user_submissions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_type: Mapped[str] = mapped_column(String(40), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    locality_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("inhabited_localities.id"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LocalityPostalCode(Base):
    __tablename__ = "locality_postal_codes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    locality_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inhabited_localities.id", ondelete="CASCADE"), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(12), nullable=False)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="GEONAMES")
    __table_args__ = (UniqueConstraint("locality_id", "postal_code", name="uq_locality_postal_code"),)
