"""The application layer: use cases and the ports they depend on.

This layer may import the domain. It may not import an adapter, a framework or
the composition root.

The distinction that matters here is *who owns the interface*. Both inbound and
outbound ports are declared in this package, because in both directions the
application is stating its own needs: what it offers to callers, and what it
requires from infrastructure. An adapter then adapts itself to the application,
never the reverse. That is the whole content of "dependencies point inward".
"""

from payment.application.errors import (
    ApplicationError,
    EventPublicationError,
    OutboundPortError,
    PaymentRepositoryError,
)

__all__ = [
    "ApplicationError",
    "EventPublicationError",
    "OutboundPortError",
    "PaymentRepositoryError",
]
