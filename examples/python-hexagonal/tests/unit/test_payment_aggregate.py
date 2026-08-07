"""Payment aggregate: invariants, lifecycle and event recording."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from payment.domain.errors import DomainError, InvalidPaymentTransitionError
from payment.domain.events import PaymentCreated
from payment.domain.payment import Payment, PaymentId, PaymentStatus
from tests.support import FIXED_INSTANT, ID_ONE, ID_TWO, a_money, a_payment, a_pix_key


class TestPaymentId:
    def test_accepts_a_uuid_shaped_value(self) -> None:
        assert PaymentId(ID_ONE).value == ID_ONE

    @pytest.mark.parametrize("value", ["", "not-a-uuid", "11111111-1111-1111-1111", "1" * 36])
    def test_rejects_anything_else(self, value: str) -> None:
        with pytest.raises(DomainError, match="not a valid payment identifier"):
            PaymentId(value)

    def test_is_compared_by_value(self) -> None:
        assert PaymentId(ID_ONE) == PaymentId(ID_ONE)
        assert PaymentId(ID_ONE) != PaymentId(ID_TWO)


class TestCreation:
    def test_a_new_payment_starts_pending(self) -> None:
        payment = a_payment()

        assert payment.status is PaymentStatus.PENDING
        assert payment.failure_reason is None

    def test_records_a_payment_created_event(self) -> None:
        payment = a_payment()

        events = payment.pull_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, PaymentCreated)
        assert event.payment_id == ID_ONE
        assert event.currency == "BRL"
        assert event.occurred_at == FIXED_INSTANT

    def test_the_event_carries_a_masked_key_not_a_raw_one(self) -> None:
        # An event crosses a boundary and often lands in a log aggregator with a
        # much wider audience than the service itself (SEC-004).
        payment = a_payment()

        event = payment.pull_events()[0]

        assert isinstance(event, PaymentCreated)
        assert event.masked_pix_key == "al***@example.com"
        assert "alice@example.com" not in str(event)

    def test_rejects_a_naive_created_at(self) -> None:
        with pytest.raises(DomainError, match="must be timezone-aware"):
            Payment.create(
                payment_id=PaymentId(ID_ONE),
                amount=a_money(),
                pix_key=a_pix_key(),
                created_at=datetime(2026, 3, 14, 15, 9, 26),  # noqa: DTZ001
                idempotency_key="idem-001",
            )

    @pytest.mark.parametrize("key", ["", "   "])
    def test_requires_an_idempotency_key(self, key: str) -> None:
        with pytest.raises(DomainError, match="idempotency key is required"):
            a_payment(idempotency_key=key)

    def test_rejects_an_over_long_idempotency_key(self) -> None:
        with pytest.raises(DomainError, match="cannot exceed 64 characters"):
            a_payment(idempotency_key="k" * 65)

    def test_rejects_an_over_long_description(self) -> None:
        with pytest.raises(DomainError, match="description cannot exceed"):
            a_payment(description="d" * 141)

    def test_accepts_a_description_at_the_limit(self) -> None:
        assert a_payment(description="d" * 140).description == "d" * 140


class TestLifecycle:
    def test_a_pending_payment_can_be_confirmed(self) -> None:
        payment = a_payment()

        payment.confirm()

        assert payment.status is PaymentStatus.CONFIRMED

    def test_a_pending_payment_can_be_cancelled(self) -> None:
        payment = a_payment()

        payment.cancel()

        assert payment.status is PaymentStatus.CANCELLED

    def test_a_pending_payment_can_fail_with_a_reason(self) -> None:
        payment = a_payment()

        payment.fail("insufficient funds")

        assert payment.status is PaymentStatus.FAILED
        assert payment.failure_reason == "insufficient funds"

    def test_failing_requires_a_reason(self) -> None:
        payment = a_payment()

        with pytest.raises(DomainError, match="failure reason is required"):
            payment.fail("   ")

        # The rejected transition must leave the aggregate untouched, otherwise
        # a caught exception would silently leave a half-changed payment behind.
        assert payment.status is PaymentStatus.PENDING

    @pytest.mark.parametrize("transition", ["confirm", "cancel"])
    def test_a_confirmed_payment_is_terminal(self, transition: str) -> None:
        payment = a_payment()
        payment.confirm()

        with pytest.raises(InvalidPaymentTransitionError) as caught:
            getattr(payment, transition)()

        assert caught.value.current == "CONFIRMED"

    def test_a_cancelled_payment_cannot_be_confirmed(self) -> None:
        payment = a_payment()
        payment.cancel()

        with pytest.raises(InvalidPaymentTransitionError, match="CANCELLED"):
            payment.confirm()

    def test_a_failed_payment_cannot_fail_again(self) -> None:
        payment = a_payment()
        payment.fail("first reason")

        with pytest.raises(InvalidPaymentTransitionError):
            payment.fail("second reason")

        assert payment.failure_reason == "first reason"

    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (PaymentStatus.PENDING, False),
            (PaymentStatus.CONFIRMED, True),
            (PaymentStatus.FAILED, True),
            (PaymentStatus.CANCELLED, True),
        ],
    )
    def test_terminal_statuses(self, status: PaymentStatus, expected: bool) -> None:
        assert status.is_terminal is expected


class TestEvents:
    def test_pulling_events_drains_them(self) -> None:
        payment = a_payment()

        first = payment.pull_events()
        second = payment.pull_events()

        # Draining is what makes publication exactly-once per unit of work: a
        # caller that publishes twice sends nothing the second time rather than
        # emitting a duplicate.
        assert len(first) == 1
        assert second == []


class TestIdentity:
    def test_payments_are_equal_by_identity_not_state(self) -> None:
        stored = a_payment()
        in_memory = a_payment()
        in_memory.confirm()

        # Same payment, different state — as happens whenever one copy is
        # loaded from storage and another has since moved on.
        assert stored == in_memory
        assert len({stored, in_memory}) == 1

    def test_different_ids_are_different_payments(self) -> None:
        assert a_payment(payment_id=ID_ONE) != a_payment(payment_id=ID_TWO)

    def test_is_not_equal_to_an_unrelated_object(self) -> None:
        assert a_payment() != "not a payment"

    def test_amount_and_creation_time_are_preserved(self) -> None:
        created_at = FIXED_INSTANT + timedelta(days=1)

        payment = a_payment(amount="99.99", created_at=created_at)

        assert payment.amount == a_money("99.99")
        assert payment.created_at == created_at
        assert payment.created_at.tzinfo is UTC
