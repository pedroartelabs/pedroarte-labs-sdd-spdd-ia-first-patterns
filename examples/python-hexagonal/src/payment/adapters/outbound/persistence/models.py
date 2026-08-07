"""Persistence models.

These are **not** domain entities (ARCH-009). They are rows: shaped by what a
relational store can index, constrain and migrate, holding primitives and
nothing else.

The temptation to annotate ``Payment`` with ``@mapped_column`` and delete this
file is strong, and giving in is how a domain acquires a lazy-loading proxy, a
required no-argument constructor, an identity tied to a database sequence, and
a hard dependency on a session being open. The mapping below costs one small
file and buys a domain that can be constructed, tested and reasoned about
without any of that.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, Dialect, Index, Numeric, String, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UtcDateTime(TypeDecorator[datetime]):
    """A timestamp that is always timezone-aware, whatever the backend does.

    This exists because of a real leak. ``Payment`` refuses a naive
    ``created_at`` — a bare local time is ambiguous across a DST boundary and
    meaningless once a second region writes to the same store. PostgreSQL
    honours ``TIMESTAMPTZ`` and hands back an aware value; SQLite has no
    timezone concept at all and hands back a naive one.

    Without this decorator the domain invariant would hold in production and
    silently break under the SQLite used by the fast tests — which is the worst
    possible arrangement, because the tests would be the thing lying.

    Absorbing the difference here is exactly what an outbound adapter is for.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("refusing to store a naive datetime; supply an aware one")
        return value.astimezone(UTC)

    def process_result_value(self, value: Any, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        if not isinstance(value, datetime):  # pragma: no cover - driver contract
            raise TypeError(f"expected datetime from the driver, got {type(value).__name__}")
        # Everything was normalised to UTC on the way in, so a naive value
        # coming back is a backend that dropped the offset, not local time.
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


class Base(DeclarativeBase):
    """Declarative base for this adapter's tables only."""


class PaymentRow(Base):
    """A stored payment."""

    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    pix_key: Mapped[str] = mapped_column(String(77), nullable=False)
    pix_key_type: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)
    # Unique, because the database is the only place that can actually enforce
    # "at most one payment per idempotency key" under concurrency. An
    # application-level check alone loses the race it exists to prevent.
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(140), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (Index("ix_payments_created_at", "created_at"),)
