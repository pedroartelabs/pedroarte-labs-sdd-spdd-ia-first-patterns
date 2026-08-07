"""Use case: create a PIX payment.

This is the orchestration layer, and it is deliberately thin. It converts input
into domain types, consults the ports it was given, lets the aggregate enforce
the rules, and reports what happened. Every business decision lives in
``Payment``; every technical decision lives in an adapter.

Notice what is absent: no HTTP, no SQL, no serialization, no clock read, no
identifier generation, no logging framework. That absence is what lets the whole
class be tested with three small fakes and no mocking library.
"""

from __future__ import annotations

from payment.application.ports.inbound.create_pix_payment import (
    CreatePixPaymentCommand,
    CreatePixPaymentResult,
)
from payment.application.ports.outbound.clock import Clock
from payment.application.ports.outbound.id_generator import IdGenerator
from payment.application.ports.outbound.payment_event_publisher import (
    PaymentEventPublisher,
)
from payment.application.ports.outbound.payment_repository import PaymentRepository
from payment.domain.errors import InvalidPixKeyError
from payment.domain.money import Money
from payment.domain.payment import Payment
from payment.domain.pix_key import PixKey, PixKeyType


class CreatePixPaymentService:
    """Default implementation of ``CreatePixPaymentUseCase``.

    Dependencies arrive through the constructor. There is no container lookup
    and no import of the composition root, so reading this class tells you
    everything it can possibly touch (ARCH-007).
    """

    def __init__(
        self,
        *,
        payments: PaymentRepository,
        id_generator: IdGenerator,
        clock: Clock,
        event_publisher: PaymentEventPublisher,
    ) -> None:
        self._payments = payments
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher

    def execute(self, command: CreatePixPaymentCommand) -> CreatePixPaymentResult:
        """Accept a PIX payment request.

        The idempotency check runs *before* anything is generated or written, so
        a retried request costs one lookup and changes nothing.
        """
        amount = Money.of(command.amount, command.currency)
        pix_key = self._parse_pix_key(command.pix_key, command.pix_key_type)

        existing = self._payments.find_by_idempotency_key(command.idempotency_key)
        if existing is not None:
            # The contract of an idempotent create is "the same request produces
            # the same outcome", so we return the original payment rather than
            # creating a second one or raising a conflict.
            return self._to_result(existing, already_existed=True)

        payment = Payment.create(
            payment_id=self._id_generator.next_payment_id(),
            amount=amount,
            pix_key=pix_key,
            created_at=self._clock.now(),
            idempotency_key=command.idempotency_key,
            description=command.description,
        )

        self._payments.save(payment)
        # Events are drained after the save. Publishing first would risk
        # announcing a payment that was never stored — and a consumer cannot
        # un-see an event.
        self._event_publisher.publish(payment.pull_events())

        return self._to_result(payment, already_existed=False)

    @staticmethod
    def _parse_pix_key(value: str, key_type: str) -> PixKey:
        """Turn transport strings into a validated PixKey.

        An unknown key type is a malformed request, not a programming error, so
        it becomes ``InvalidPixKeyError`` — which the inbound adapter already knows
        how to render as a 422 — rather than a bare ``ValueError``.
        """
        try:
            parsed_type = PixKeyType(key_type)
        except ValueError as exc:
            supported = ", ".join(t.value for t in PixKeyType)
            raise InvalidPixKeyError(
                f"unknown PIX key type {key_type!r}; supported: {supported}"
            ) from exc
        return PixKey(value=value, key_type=parsed_type)

    @staticmethod
    def _to_result(payment: Payment, *, already_existed: bool) -> CreatePixPaymentResult:
        return CreatePixPaymentResult(
            payment_id=payment.id.value,
            status=str(payment.status),
            amount=payment.amount.amount,
            currency=payment.amount.currency,
            created_at=payment.created_at,
            already_existed=already_existed,
        )
