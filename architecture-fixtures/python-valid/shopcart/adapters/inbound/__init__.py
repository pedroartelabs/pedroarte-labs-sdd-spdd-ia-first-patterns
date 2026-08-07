"""Inbound adapter — CORRECT.

Depends on the application port only. It has no idea which repository
implementation is in play, and could not reach one if it tried.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from shopcart.application import AddItemUseCase


class CartController:
    def __init__(self, add_item: AddItemUseCase) -> None:
        self._add_item = add_item

    def post_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        cart = self._add_item.execute(
            cart_id=str(payload["cart_id"]),
            sku=str(payload["sku"]),
            quantity=int(payload["quantity"]),
            unit_price=Decimal(str(payload["unit_price"])),
        )
        return {"cart_id": cart.cart_id, "total": str(cart.total)}
