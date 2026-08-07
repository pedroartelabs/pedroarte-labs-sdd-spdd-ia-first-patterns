"""The Payment aggregate.

This is the consistency boundary of the example: every rule about what a
payment may be, and how it may change, is enforced here rather than in a
service, a controller or a database constraint.

Two design points worth noticing:

* The aggregate never reads a clock and never generates an identifier. Both
  arrive as arguments (ARCH-012). That is what makes every test below
  deterministic without a mocking framework.
* State changes go through named methods that encode the lifecycle. There is no
  public ``status`` setter, so an illegal transition is not something a caller
  can express by accident.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from payment.domain.errors import DomainError, InvalidPaymentTransitionError
from payment.domain.events import DomainEvent, PaymentCreated
from payment.domain.money import Money
from payment.domain.pix_key import PixKey

_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

_MAX_DESCRIPTION_LENGTH = 140
_MAX_IDEMPOTENCY_KEY_LENGTH = 64


class PaymentStatus(StrEnum):
    """Where a payment sits in its lifecycle."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal(self) -> bool:
        return self in {PaymentStatus.CONFIRMED, PaymentStatus.FAILED, PaymentStatus.CANCELLED}


@dataclass(frozen=True, slots=True)
class PaymentId:
    """The identity of a payment.

    Validated by shape rather than by importing ``uuid``: the domain must not
    depend on an identifier *generator* (ARCH-012), only on what a valid
    identifier looks like. Generation belongs to the IdGenerator port.
    """

    value: str

    def __post_init__(self) -> None:
        if not _UUID_PATTERN.match(self.value):
            raise DomainError(f"{self.value!r} is not a valid payment identifier")

    def __str__(self) -> str:
        return self.value


@dataclass(eq=False, slots=True)
class Payment:
    """A PIX payment request and its lifecycle.

    Educational only: accepting a payment here means recording an intent, not
    moving money. There is no bank, no settlement and no real PIX endpoint
    behind this type.
    """

    id: PaymentId
    amount: Money
    pix_key: PixKey
    status: PaymentStatus
    created_at: datetime
    idempotency_key: str
    description: str | None = None
    failure_reason: str | None = None
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        payment_id: PaymentId,
        amount: Money,
        pix_key: PixKey,
        created_at: datetime,
        idempotency_key: str,
        description: str | None = None,
    ) -> Payment:
        """Accept a new payment request, recording that it happened.

        ``created_at`` and ``payment_id`` are supplied by the caller — the use
        case obtains them from the Clock and IdGenerator ports — so that the
        aggregate stays a pure function of its inputs.
        """
        cls._validate_created_at(created_at)
        cls._validate_idempotency_key(idempotency_key)
        cls._validate_description(description)

        payment = cls(
            id=payment_id,
            amount=amount,
            pix_key=pix_key,
            status=PaymentStatus.PENDING,
            created_at=created_at,
            idempotency_key=idempotency_key,
            description=description,
        )
        payment._events.append(
            PaymentCreated(
                occurred_at=created_at,
                payment_id=payment_id.value,
                amount=amount.amount,
                currency=amount.currency,
                pix_key_type=str(pix_key.key_type),
                masked_pix_key=pix_key.masked(),
            )
        )
        return payment

    # -- lifecycle ---------------------------------------------------------

    def confirm(self) -> None:
        """Mark the payment as settled."""
        self._require_pending(PaymentStatus.CONFIRMED)
        self.status = PaymentStatus.CONFIRMED

    def fail(self, reason: str) -> None:
        """Mark the payment as failed, keeping why."""
        self._require_pending(PaymentStatus.FAILED)
        if not reason or not reason.strip():
            raise DomainError("a failure reason is required")
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason.strip()

    def cancel(self) -> None:
        """Withdraw a payment that has not settled."""
        self._require_pending(PaymentStatus.CANCELLED)
        self.status = PaymentStatus.CANCELLED

    def _require_pending(self, requested: PaymentStatus) -> None:
        if self.status is not PaymentStatus.PENDING:
            raise InvalidPaymentTransitionError(str(self.status), str(requested))

    # -- events ------------------------------------------------------------

    def pull_events(self) -> list[DomainEvent]:
        """Hand over the recorded events and forget them.

        Draining rather than exposing keeps publication exactly-once per unit of
        work: a caller that publishes twice gets an empty list the second time
        instead of a duplicate.
        """
        drained = list(self._events)
        self._events.clear()
        return drained

    # -- identity ----------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Aggregates are equal when their identity is equal, not their state.

        A payment loaded from storage and the same payment held in memory are
        the same payment even if one has since been confirmed.
        """
        if not isinstance(other, Payment):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- validation --------------------------------------------------------

    @staticmethod
    def _validate_created_at(created_at: datetime) -> None:
        if created_at.tzinfo is None or created_at.tzinfo.utcoffset(created_at) is None:
            raise DomainError("created_at must be timezone-aware; a naive timestamp is ambiguous")

    @staticmethod
    def _validate_idempotency_key(key: str) -> None:
        if not key or not key.strip():
            raise DomainError("an idempotency key is required")
        if len(key) > _MAX_IDEMPOTENCY_KEY_LENGTH:
            raise DomainError(
                f"idempotency key cannot exceed {_MAX_IDEMPOTENCY_KEY_LENGTH} characters"
            )

    @staticmethod
    def _validate_description(description: str | None) -> None:
        if description is not None and len(description) > _MAX_DESCRIPTION_LENGTH:
            raise DomainError(f"description cannot exceed {_MAX_DESCRIPTION_LENGTH} characters")
