"""Inbound port: create a PIX payment.

The port is the application's offer to the outside world, expressed without any
knowledge of who will call it. A REST controller, a CLI, a message consumer and
a test all use this same interface, which is what makes the REST adapter
replaceable rather than load-bearing.

The command carries primitives rather than domain value objects on purpose: an
inbound adapter should be able to build one from a parsed request body without
first learning the domain's internal types. Turning those primitives into
``Money`` and ``PixKey`` — and rejecting them if they are not valid — is the
use case's job.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CreatePixPaymentCommand:
    """A request to accept a new PIX payment."""

    amount: Decimal
    currency: str
    pix_key: str
    pix_key_type: str
    idempotency_key: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class CreatePixPaymentResult:
    """What the caller gets back.

    ``already_existed`` makes the idempotent replay visible. A caller retrying
    after a timeout gets the same payment and can tell that nothing new
    happened — useful for logging, and honest about what the system did.
    """

    payment_id: str
    status: str
    amount: Decimal
    currency: str
    created_at: datetime
    already_existed: bool


class CreatePixPaymentUseCase(Protocol):
    """Accept a PIX payment request.

    Raises:
        payment.domain.errors.DomainError: the request violates a business rule.
        payment.application.errors.OutboundPortError: infrastructure failed.
    """

    def execute(self, command: CreatePixPaymentCommand) -> CreatePixPaymentResult:
        """Accept the payment, or fail explaining why."""
        ...
