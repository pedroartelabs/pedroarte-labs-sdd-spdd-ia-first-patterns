"""In-memory outbound adapters.

A real adapter, not a mock. It ships in `src/`, satisfies the same contract
suite as the SQL implementation, and lets the whole application run with no
infrastructure — which is what keeps the fast feedback loop fast.
"""

from payment.adapters.outbound.memory.in_memory_payment_repository import (
    InMemoryPaymentRepository,
)

__all__ = ["InMemoryPaymentRepository"]
