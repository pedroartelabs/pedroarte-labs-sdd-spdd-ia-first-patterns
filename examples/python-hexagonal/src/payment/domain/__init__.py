"""The payment domain: the centre of the hexagon.

Nothing in this package may import a framework, a database driver, a transport
library, the application layer, an adapter or the composition root. It depends
on the Python standard library and on itself, and that is the whole point:
every rule here can be tested in microseconds and will outlive whatever web
framework the adapters currently use.

The Import Linter contracts in `.importlinter` enforce this, and
`architecture-fixtures/python-invalid-domain-framework-import` proves the
enforcement actually fires.
"""

from payment.domain.errors import (
    DomainError,
    InvalidMoneyError,
    InvalidPaymentTransitionError,
    InvalidPixKeyError,
)
from payment.domain.events import DomainEvent, PaymentCreated
from payment.domain.money import Money
from payment.domain.payment import Payment, PaymentId, PaymentStatus
from payment.domain.pix_key import PixKey, PixKeyType

__all__ = [
    "DomainError",
    "DomainEvent",
    "InvalidMoneyError",
    "InvalidPaymentTransitionError",
    "InvalidPixKeyError",
    "Money",
    "Payment",
    "PaymentCreated",
    "PaymentId",
    "PaymentStatus",
    "PixKey",
    "PixKeyType",
]
