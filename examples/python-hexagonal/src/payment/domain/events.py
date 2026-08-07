"""Domain events.

An event records something that already happened, in the language of the
domain. It is deliberately *not* a transport message: there is no JSON here, no
schema registry, no topic name. An outbound adapter decides how a
``PaymentCreated`` becomes bytes on a wire; the domain only decides that it
occurred and what it means.

Note that ``occurred_at`` is a value the aggregate was given, never one it read
from a clock. ARCH-012.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Base type for anything the domain records as having happened."""

    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PaymentCreated(DomainEvent):
    """A payment was accepted into the system and is awaiting settlement.

    Carries primitives rather than value objects so that a publisher can
    serialise it without importing the domain's internal types — the event is
    the contract, and a contract made of your own classes is hard to honour
    from the other side of a wire.
    """

    payment_id: str
    amount: Decimal
    currency: str
    pix_key_type: str
    masked_pix_key: str

    def __str__(self) -> str:
        return (
            f"PaymentCreated(payment_id={self.payment_id}, "
            f"amount={self.amount} {self.currency}, "
            f"pix_key={self.masked_pix_key})"
        )
