"""REST inbound adapter.

FastAPI and Pydantic are used here and forbidden inward. Request and response
DTOs live in `dto.py` and belong to the HTTP contract, not to the domain
(ARCH-010): they may change with an API version without any business rule
changing, and that independence is the point.
"""

from payment.adapters.inbound.rest.payment_controller import create_payment_router

__all__ = ["create_payment_router"]
