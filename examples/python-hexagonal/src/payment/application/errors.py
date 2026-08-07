"""Application-level errors.

These sit between domain errors (a business rule was violated) and raw
technical exceptions (a socket closed, a table is missing).

An outbound adapter must translate its technology's exceptions into one of
these before letting them cross the boundary (ARCH-011). Without that
translation the application layer would have to catch ``OperationalError`` to
work with SQLAlchemy and something else entirely to work with an in-memory
implementation — which would mean the application had a hidden dependency on
its infrastructure after all.
"""

from __future__ import annotations


class ApplicationError(Exception):
    """Base class for failures the application layer can reason about."""


class OutboundPortError(ApplicationError):
    """An outbound port could not do its job for a technical reason.

    Distinct from a domain error: nothing about the request was wrong, so the
    correct response is usually to retry or to return 503, not to tell the
    caller to fix their input.
    """

    def __init__(self, port: str, message: str) -> None:
        super().__init__(f"{port}: {message}")
        self.port = port


class PaymentRepositoryError(OutboundPortError):
    """The payment store could not be read or written."""

    def __init__(self, message: str) -> None:
        super().__init__("PaymentRepository", message)


class EventPublicationError(OutboundPortError):
    """A domain event could not be published."""

    def __init__(self, message: str) -> None:
        super().__init__("PaymentEventPublisher", message)
