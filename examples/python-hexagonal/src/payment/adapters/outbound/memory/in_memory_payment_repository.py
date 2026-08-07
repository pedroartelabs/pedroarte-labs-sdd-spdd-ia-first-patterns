"""In-memory implementation of ``PaymentRepository``.

Not a test double living in a test folder — a first-class adapter. That
distinction matters: it is subject to the same contract suite as the SQL
implementation (`tests/contract/`), so the two cannot drift apart, and a
developer can run the whole application without a database.

It stores aggregates directly, which is honest about what it is. A production
store must map to its own persistence model instead (ARCH-010).
"""

from __future__ import annotations

import threading

from payment.domain.payment import Payment, PaymentId


class InMemoryPaymentRepository:
    """Keeps payments in a dictionary, guarded by a lock.

    The lock is not decoration. FastAPI runs sync endpoints in a thread pool, so
    two concurrent requests genuinely can reach this object at the same time,
    and an unsynchronised dict would make the idempotency lookup racy in exactly
    the situation idempotency exists to handle.
    """

    def __init__(self) -> None:
        self._by_id: dict[str, Payment] = {}
        self._id_by_idempotency_key: dict[str, str] = {}
        self._lock = threading.RLock()

    def save(self, payment: Payment) -> None:
        with self._lock:
            self._by_id[payment.id.value] = payment
            self._id_by_idempotency_key[payment.idempotency_key] = payment.id.value

    def find_by_id(self, payment_id: PaymentId) -> Payment | None:
        with self._lock:
            return self._by_id.get(payment_id.value)

    def find_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        with self._lock:
            payment_id = self._id_by_idempotency_key.get(idempotency_key)
            if payment_id is None:
                return None
            return self._by_id.get(payment_id)

    def clear(self) -> None:
        """Empty the store.

        Present for test setup only; it is not part of ``PaymentRepository``, so
        no application code can reach it through the port.
        """
        with self._lock:
            self._by_id.clear()
            self._id_by_idempotency_key.clear()
