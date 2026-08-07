"""Inbound adapter — DELIBERATELY BROKEN (ARCH-004).

**This file violates the architecture on purpose.** It exists so the suite can
prove the `adapter-independence` contract actually fails when it should. Do not
copy this pattern, and do not "fix" it — the test asserts it is rejected.

The violation is the import of the outbound adapter, and the `get_total` method
that uses it to reach storage directly.

This is how the mistake genuinely happens. A read-only endpoint needs a total.
Routing it through the use case looks like ceremony for a one-line lookup, so
the controller talks to the repository instead. It works, it is shorter, and
the reviewer waves it through.

What it costs: the application layer is no longer the only path to the data.
Whatever the use case would have applied — authorisation, a currency rule, an
audit record — now exists only on the write path. Add a CLI or a message
consumer later and the read behaviour silently differs by transport, because
the rule was never in a place all three could reach.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from shopcart.application import AddItemUseCase

# >>> THE VIOLATION (ARCH-004): an inbound adapter importing an outbound adapter.
from shopcart.adapters.outbound import InMemoryCartRepository


class CartController:
    def __init__(self, add_item: AddItemUseCase) -> None:
        self._add_item = add_item
        # Reaching straight past the application layer into storage.
        self._carts = InMemoryCartRepository()

    def post_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        cart = self._add_item.execute(
            cart_id=str(payload["cart_id"]),
            sku=str(payload["sku"]),
            quantity=int(payload["quantity"]),
            unit_price=Decimal(str(payload["unit_price"])),
        )
        return {"cart_id": cart.cart_id, "total": str(cart.total)}

    def get_total(self, cart_id: str) -> dict[str, Any]:
        """Skips the use case entirely — the defect this fixture demonstrates."""
        cart = self._carts.load(cart_id)
        return {"cart_id": cart_id, "total": str(cart.total) if cart else "0"}
