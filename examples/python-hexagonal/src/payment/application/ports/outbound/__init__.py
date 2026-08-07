"""Outbound ports: what this bounded context requires.

Four ports, and each exists because something outside the hexagon would
otherwise reach inside it:

* `PaymentRepository`  — storage
* `PaymentEventPublisher` — messaging
* `Clock` — the current time
* `IdGenerator` — identity

The last two are the ones teams most often skip, and they are the ones that
quietly make a codebase untestable. `datetime.now()` and `uuid4()` are side
effects wearing the clothes of pure functions.
"""

from payment.application.ports.outbound.clock import Clock
from payment.application.ports.outbound.id_generator import IdGenerator
from payment.application.ports.outbound.payment_event_publisher import (
    PaymentEventPublisher,
)
from payment.application.ports.outbound.payment_repository import PaymentRepository

__all__ = [
    "Clock",
    "IdGenerator",
    "PaymentEventPublisher",
    "PaymentRepository",
]
