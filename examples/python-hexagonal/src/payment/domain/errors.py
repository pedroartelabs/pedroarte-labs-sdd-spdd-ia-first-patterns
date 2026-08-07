"""Domain errors.

These are *business* failures, expressed in the language of the domain. A
technical failure — a dropped connection, a serialization problem, a missing
table — is not a domain error and must be translated at the adapter boundary
(ARCH-011) rather than allowed to leak inward.

Keeping this hierarchy separate is what lets an inbound adapter map a domain
error to a 422 and an infrastructure error to a 503 without inspecting strings.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for every violation of a domain rule."""


class InvalidMoneyError(DomainError):
    """The amount or currency does not describe usable money."""


class InvalidPixKeyError(DomainError):
    """The PIX key is malformed for its declared type."""


class InvalidPaymentTransitionError(DomainError):
    """A payment was asked to move between states in a way the lifecycle forbids."""

    def __init__(self, current: str, requested: str) -> None:
        super().__init__(f"a payment in status {current} cannot transition to {requested}")
        self.current = current
        self.requested = requested
