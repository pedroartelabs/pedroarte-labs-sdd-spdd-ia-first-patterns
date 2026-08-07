"""Transport DTOs for the REST adapter.

These live here and nowhere else (ARCH-010). They are shaped by HTTP and JSON —
field names a client will read, validation a client will see as 422 — and they
are free to change whenever the API version changes, precisely because nothing
inward depends on them.

Pydantic is used deliberately at this boundary and forbidden in the domain. It
is excellent at "is this parsed input well-formed?" and a poor fit for "is this
aggregate in a legal state?", which is a question about behaviour over time
rather than about a single construction.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from payment.application.ports.inbound.create_pix_payment import (
    CreatePixPaymentCommand,
    CreatePixPaymentResult,
)


class CreatePaymentRequest(BaseModel):
    """The JSON body a client posts to create a payment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    amount: Decimal = Field(gt=0, description="Amount in the major unit, e.g. 10.50")
    currency: str = Field(min_length=3, max_length=3, examples=["BRL"])
    pix_key: str = Field(min_length=1, max_length=77)
    pix_key_type: str = Field(examples=["EMAIL", "PHONE", "TAX_ID", "RANDOM"])
    description: str | None = Field(default=None, max_length=140)

    def to_command(self, idempotency_key: str) -> CreatePixPaymentCommand:
        """Translate transport into an application command.

        Mapping is explicit rather than automatic. An implicit mapper would let
        a new HTTP field silently become a new domain concept, which is exactly
        the coupling this boundary exists to prevent.
        """
        return CreatePixPaymentCommand(
            amount=self.amount,
            currency=self.currency.upper(),
            pix_key=self.pix_key,
            pix_key_type=self.pix_key_type.upper(),
            idempotency_key=idempotency_key,
            description=self.description,
        )


class CreatePaymentResponse(BaseModel):
    """The JSON body returned after a payment is accepted."""

    model_config = ConfigDict(frozen=True)

    payment_id: str
    status: str
    amount: Decimal
    currency: str
    created_at: datetime

    @classmethod
    def from_result(cls, result: CreatePixPaymentResult) -> CreatePaymentResponse:
        return cls(
            payment_id=result.payment_id,
            status=result.status,
            amount=result.amount,
            currency=result.currency,
            created_at=result.created_at,
        )


class ErrorResponse(BaseModel):
    """A problem, rendered for a client.

    Carries a stable machine-readable ``code`` alongside the human ``message``.
    Clients that branch on message text break the moment wording improves.
    """

    model_config = ConfigDict(frozen=True)

    code: str
    message: str
