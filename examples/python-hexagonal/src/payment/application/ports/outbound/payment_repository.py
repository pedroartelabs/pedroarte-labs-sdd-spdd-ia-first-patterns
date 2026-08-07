"""Outbound port: payment storage.

Named for what the application needs, not for how it is satisfied — there is no
``Sql``, ``Jpa`` or ``Mongo`` anywhere in the name (ARCH-008/NAM-001). The
application declares this interface; an adapter implements it. That direction is
what keeps the dependency arrow pointing inward.

Every implementation must satisfy the same contract suite in
`tests/contract/`, so the in-memory implementation used by fast tests and the
SQL implementation used in production cannot quietly disagree about, say,
whether saving twice is an update or a duplicate.
"""

from __future__ import annotations

from typing import Protocol

from payment.domain.payment import Payment, PaymentId


class PaymentRepository(Protocol):
    """Persist and retrieve payments.

    Implementations must translate their technology's failures into
    ``PaymentRepositoryError`` rather than letting driver exceptions escape
    (ARCH-011).
    """

    def save(self, payment: Payment) -> None:
        """Store a payment, overwriting any previous state for the same id.

        Raises:
            payment.application.errors.PaymentRepositoryError: storage failed.
        """
        ...

    def find_by_id(self, payment_id: PaymentId) -> Payment | None:
        """Return the payment with this id, or None when there is none.

        Returning ``None`` rather than raising is deliberate: "not found" is an
        ordinary outcome the caller must handle, not an exceptional one.
        """
        ...

    def find_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        """Return the payment previously created under this key, if any.

        This is what makes retrying a create safe. A client that times out and
        retries with the same key gets the original payment back instead of a
        second one.
        """
        ...
