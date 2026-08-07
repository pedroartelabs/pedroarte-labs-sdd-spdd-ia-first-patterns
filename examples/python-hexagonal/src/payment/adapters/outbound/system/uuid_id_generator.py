"""UUID implementation of the ``IdGenerator`` port.

This is the only module in the package permitted to import ``uuid``. The Import
Linter contract `domain-has-no-ambient-io` forbids it inward (ARCH-012), which
is what keeps every use-case test able to assert on an exact identifier instead
of matching a pattern or patching a module.

The name says ``Uuid`` because it is an adapter; the port it satisfies is called
``IdGenerator`` and says nothing about UUIDs (ARCH-008).
"""

from __future__ import annotations

import uuid

from payment.domain.payment import PaymentId


class UuidIdGenerator:
    """Generates payment identifiers as random UUIDv4 values."""

    def next_payment_id(self) -> PaymentId:
        return PaymentId(str(uuid.uuid4()))
