"""SQL implementation of ``PaymentRepository``.

Two responsibilities, both of them translation:

1. **Model translation.** Aggregate to row on the way out, row to aggregate on
   the way in. Explicit, boring, and the reason the domain never learns what a
   session is.
2. **Failure translation.** SQLAlchemy exceptions become ``PaymentRepositoryError``
   before they cross the boundary (ARCH-011). Without this, the application
   layer would have to catch ``OperationalError`` — and would therefore depend
   on SQLAlchemy while pretending not to.

Reconstructing the aggregate goes through ``_row_to_payment``, which rebuilds
state without replaying the creation event: loading a payment from storage is
not the same business occurrence as accepting a new one, and must not publish
``PaymentCreated`` a second time.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from payment.adapters.outbound.persistence.models import PaymentRow
from payment.application.errors import PaymentRepositoryError
from payment.domain.money import Money
from payment.domain.payment import Payment, PaymentId, PaymentStatus
from payment.domain.pix_key import PixKey, PixKeyType


class SqlPaymentRepository:
    """Stores payments in a relational database."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, payment: Payment) -> None:
        try:
            row = self._session.get(PaymentRow, payment.id.value)
            if row is None:
                self._session.add(self._payment_to_row(payment))
            else:
                self._update_row(row, payment)
            self._session.flush()
        except SQLAlchemyError as exc:
            self._session.rollback()
            # The driver message can name hosts, schemas and occasionally
            # credentials, so it is logged by infrastructure but not carried
            # outward (SEC-004).
            raise PaymentRepositoryError(f"could not save payment {payment.id}") from exc

    def find_by_id(self, payment_id: PaymentId) -> Payment | None:
        try:
            row = self._session.get(PaymentRow, payment_id.value)
        except SQLAlchemyError as exc:
            raise PaymentRepositoryError("could not read payment by id") from exc
        return None if row is None else self._row_to_payment(row)

    def find_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        try:
            row = self._session.scalars(
                select(PaymentRow).where(PaymentRow.idempotency_key == idempotency_key)
            ).one_or_none()
        except SQLAlchemyError as exc:
            raise PaymentRepositoryError("could not read payment by idempotency key") from exc
        return None if row is None else self._row_to_payment(row)

    # -- mapping -----------------------------------------------------------

    @staticmethod
    def _payment_to_row(payment: Payment) -> PaymentRow:
        return PaymentRow(
            id=payment.id.value,
            amount=payment.amount.amount,
            currency=payment.amount.currency,
            pix_key=payment.pix_key.value,
            pix_key_type=str(payment.pix_key.key_type),
            status=str(payment.status),
            created_at=payment.created_at,
            idempotency_key=payment.idempotency_key,
            description=payment.description,
            failure_reason=payment.failure_reason,
        )

    @staticmethod
    def _update_row(row: PaymentRow, payment: Payment) -> None:
        # Only the mutable parts of the lifecycle. Identity, amount, key and
        # creation time are immutable by design, and quietly overwriting them
        # here would let a bug in one place corrupt history everywhere.
        row.status = str(payment.status)
        row.failure_reason = payment.failure_reason

    @staticmethod
    def _row_to_payment(row: PaymentRow) -> Payment:
        return Payment(
            id=PaymentId(row.id),
            amount=Money(amount=row.amount, currency=row.currency),
            pix_key=PixKey(value=row.pix_key, key_type=PixKeyType(row.pix_key_type)),
            status=PaymentStatus(row.status),
            created_at=row.created_at,
            idempotency_key=row.idempotency_key,
            description=row.description,
            failure_reason=row.failure_reason,
        )
