"""Outbound adapter — CORRECT.

Implements the application's port. Depends on domain and application, never on
the inbound adapter.
"""

from __future__ import annotations

from shopcart.domain import Cart


class InMemoryCartRepository:
    def __init__(self) -> None:
        self._carts: dict[str, Cart] = {}

    def load(self, cart_id: str) -> Cart | None:
        return self._carts.get(cart_id)

    def save(self, cart: Cart) -> None:
        self._carts[cart.cart_id] = cart
