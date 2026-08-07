"""Test doubles and builders.

These are **fakes**, not mocks: real working implementations of the outbound
ports, kept trivially simple. The choice is deliberate.

A mock asserts that a method was called. A fake lets you assert on the outcome.
The first couples the test to how the use case is written, so a harmless
refactor breaks it; the second couples it to what the use case achieves, which
is the thing actually worth protecting.

Because every port is injected, no test in this suite patches a module, freezes
global time, or needs a mocking library at all.

This module holds the helpers; `conftest.py` wraps them as pytest fixtures. They
are separate so tests can import a builder directly without pytest loading
`conftest` twice under two different module names.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

from payment.application.errors import EventPublicationError, PaymentRepositoryError
from payment.application.ports.inbound.create_pix_payment import CreatePixPaymentCommand
from payment.domain.events import DomainEvent
from payment.domain.money import Money
from payment.domain.payment import Payment, PaymentId
from payment.domain.pix_key import PixKey, PixKeyType

FIXED_INSTANT = datetime(2026, 3, 14, 15, 9, 26, tzinfo=UTC)

# Deterministic, obviously-fake identifiers. Valid UUIDv4 shape so PaymentId
# accepts them, but recognisable at a glance in a failure message.
ID_ONE = "aaaaaaaa-1111-4111-8111-aaaaaaaaaaaa"
ID_TWO = "bbbbbbbb-2222-4222-8222-bbbbbbbbbbbb"


class FixedClock:
    """A clock that never moves."""

    def __init__(self, instant: datetime = FIXED_INSTANT) -> None:
        self._instant = instant

    def now(self) -> datetime:
        return self._instant


class SequentialIdGenerator:
    """Hands out a scripted sequence of identifiers.

    Running out raises rather than wrapping around: a test that asked for more
    identifiers than it scripted has done something it did not intend, and
    silently recycling one would surface later as a confusing collision.
    """

    def __init__(self, *ids: str) -> None:
        self._ids = list(ids) or [ID_ONE]
        self._index = 0

    def next_payment_id(self) -> PaymentId:
        if self._index >= len(self._ids):
            raise AssertionError(
                f"SequentialIdGenerator exhausted after {len(self._ids)} id(s); "
                "the code under test requested more identifiers than expected"
            )
        value = self._ids[self._index]
        self._index += 1
        return PaymentId(value)


class RecordingEventPublisher:
    """Keeps published events so a test can assert on them."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []
        self.publish_calls = 0

    def publish(self, events: Sequence[DomainEvent]) -> None:
        self.publish_calls += 1
        self.published.extend(events)


class FailingEventPublisher:
    """Always fails, for exercising the publication failure path."""

    def publish(self, events: Sequence[DomainEvent]) -> None:
        raise EventPublicationError("broker unreachable")


class FailingPaymentRepository:
    """Always fails, for exercising error translation at the boundary."""

    def save(self, payment: Payment) -> None:
        raise PaymentRepositoryError("storage unreachable")

    def find_by_id(self, payment_id: PaymentId) -> Payment | None:
        raise PaymentRepositoryError("storage unreachable")

    def find_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        raise PaymentRepositoryError("storage unreachable")


# ---------------------------------------------------------------------------
# Builders
#
# Every field has a sensible default so a test names only what it cares about.
# A test that says `a_payment(amount="0.01")` is stating its intent; one that
# spells out six irrelevant arguments buries it.
# ---------------------------------------------------------------------------


def a_money(amount: str = "10.50", currency: str = "BRL") -> Money:
    return Money.of(amount, currency)


def a_pix_key(
    value: str = "alice@example.com",
    key_type: PixKeyType = PixKeyType.EMAIL,
) -> PixKey:
    return PixKey(value=value, key_type=key_type)


def a_payment(
    *,
    payment_id: str = ID_ONE,
    amount: str = "10.50",
    currency: str = "BRL",
    idempotency_key: str = "idem-001",
    created_at: datetime = FIXED_INSTANT,
    description: str | None = None,
) -> Payment:
    """A valid PENDING payment."""
    return Payment.create(
        payment_id=PaymentId(payment_id),
        amount=Money.of(amount, currency),
        pix_key=a_pix_key(),
        created_at=created_at,
        idempotency_key=idempotency_key,
        description=description,
    )


def a_command(
    *,
    amount: str = "10.50",
    currency: str = "BRL",
    pix_key: str = "alice@example.com",
    pix_key_type: str = "EMAIL",
    idempotency_key: str = "idem-001",
    description: str | None = None,
) -> CreatePixPaymentCommand:
    return CreatePixPaymentCommand(
        amount=Decimal(amount),
        currency=currency,
        pix_key=pix_key,
        pix_key_type=pix_key_type,
        idempotency_key=idempotency_key,
        description=description,
    )
