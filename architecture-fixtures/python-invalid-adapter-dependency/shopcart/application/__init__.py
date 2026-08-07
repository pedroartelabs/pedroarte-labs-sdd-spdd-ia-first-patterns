"""Application layer — CORRECT.

Declares its own ports and depends only on the domain.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from shopcart.domain import Cart, CartItem


class CartRepository(Protocol):
    """Outbound port. Named for the responsibility, not the technology."""

    def load(self, cart_id: str) -> Cart | None: ...

    def save(self, cart: Cart) -> None: ...


class AddItemUseCase(Protocol):
    """Inbound port."""

    def execute(self, cart_id: str, sku: str, quantity: int, unit_price: Decimal) -> Cart: ...


class AddItemService:
    def __init__(self, carts: CartRepository) -> None:
        self._carts = carts

    def execute(self, cart_id: str, sku: str, quantity: int, unit_price: Decimal) -> Cart:
        cart = self._carts.load(cart_id) or Cart(cart_id=cart_id)
        cart.add(CartItem(sku=sku, quantity=quantity, unit_price=unit_price))
        self._carts.save(cart)
        return cart
