"""Composition root — CORRECT.

The only module that knows every other module, and only in order to wire them.
"""

from __future__ import annotations

from shopcart.adapters.inbound import CartController
from shopcart.adapters.outbound import InMemoryCartRepository
from shopcart.application import AddItemService


def build_controller() -> CartController:
    return CartController(AddItemService(InMemoryCartRepository()))
