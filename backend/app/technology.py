"""Technology classification and provenance; retailer codes are never GTINs."""

import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class TechnologyGroup(Base):
    __tablename__ = "technology_groups"
    code: Mapped[str] = mapped_column(String(40), primary_key=True)
    name_bg: Mapped[str] = mapped_column(String(120), nullable=False)
    name_en: Mapped[str] = mapped_column(String(120), nullable=False)
    aliases: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)


class TechnologyIdentity(Base):
    __tablename__ = "technology_catalog_identities"
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True
    )
    group_code: Mapped[str] = mapped_column(
        ForeignKey("technology_groups.code"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    source_product_code: Mapped[str] = mapped_column(String(100), nullable=False)
    source_category: Mapped[str] = mapped_column(String(300), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    __table_args__ = (
        UniqueConstraint(
            "source", "source_product_code", name="uq_technology_source_identity"
        ),
    )
