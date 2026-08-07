"""Relational persistence adapter.

SQLAlchemy lives here and nowhere inward. `models.py` holds rows, not domain
entities (ARCH-009); `sql_payment_repository.py` maps between the two and
translates driver failures into ``PaymentRepositoryError`` (ARCH-011).
"""

from payment.adapters.outbound.persistence.models import Base, PaymentRow
from payment.adapters.outbound.persistence.sql_payment_repository import SqlPaymentRepository

__all__ = ["Base", "PaymentRow", "SqlPaymentRepository"]
