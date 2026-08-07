"""Outbound port: identifier generation.

Same reasoning as the Clock: identity generation is a side effect. A use case
that calls ``uuid4()`` inline produces a different result on every run, so
asserting on the identifier means either not asserting on it or patching a
module — both of which are worse than passing a generator in.

The Import Linter contract `domain-has-no-ambient-io` forbids importing ``uuid``
inside the domain for exactly this reason (ARCH-012).
"""

from __future__ import annotations

from typing import Protocol

from payment.domain.payment import PaymentId


class IdGenerator(Protocol):
    """Produces new payment identifiers."""

    def next_payment_id(self) -> PaymentId:
        """Return a fresh, unique payment identifier.

        Named for the thing it produces rather than the algorithm that produces
        it: swapping UUIDv4 for ULID or a snowflake id must not require touching
        a single caller.
        """
        ...
