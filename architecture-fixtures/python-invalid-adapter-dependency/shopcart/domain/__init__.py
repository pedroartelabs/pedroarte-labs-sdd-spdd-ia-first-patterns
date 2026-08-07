"""Shopping cart domain — CORRECT.

Standard library only. No framework, no I/O, no knowledge of any layer outside
itself. This is what the contracts are meant to allow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


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
