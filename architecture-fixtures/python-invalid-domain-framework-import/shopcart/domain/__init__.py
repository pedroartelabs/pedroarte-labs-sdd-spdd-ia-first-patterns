"""Shopping cart domain — DELIBERATELY BROKEN (ARCH-001).

**This file violates the architecture on purpose.** It exists so the suite can
prove the `domain-is-framework-free` contract actually fails when it should.
Do not copy this pattern, and do not "fix" it — the test asserts it is rejected.

The violation is the single import below.

It is written the way this mistake really arrives: not as a wild decision, but
as one small convenience. Someone wants a `Numeric` column type for prices,
imports it into the entity that already describes prices, and everything works.
Nothing breaks that day.

What it costs shows up later. The domain can no longer be imported without
SQLAlchemy installed, so the fast test suite acquires a database dependency.
The entity gradually grows a no-argument constructor, lazy-loading proxies and
an identity tied to a sequence. Eventually a business object cannot be
constructed without an open session, and the "domain" is a schema with methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

# >>> THE VIOLATION (ARCH-001): a persistence framework inside the domain.
from sqlalchemy import Numeric  # noqa: F401  — unused on purpose; the import is the defect


class CartError(Exception):
    """A cart rule was violated."""


@dataclass(frozen=True, slots=True)
class CartItem:
    sku: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise CartError("quantity must be at least 1")
        if self.unit_price <= 0:
            raise CartError("unit price must be positive")

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(slots=True)
class Cart:
    cart_id: str
    items: list[CartItem] = field(default_factory=list)

    MAX_ITEMS = 50

    def add(self, item: CartItem) -> None:
        if len(self.items) >= self.MAX_ITEMS:
            raise CartError(f"a cart cannot hold more than {self.MAX_ITEMS} items")
        self.items.append(item)

    @property
    def total(self) -> Decimal:
        return sum((item.subtotal for item in self.items), Decimal("0"))
