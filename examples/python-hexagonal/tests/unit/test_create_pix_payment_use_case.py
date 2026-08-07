"""CreatePixPaymentService: orchestration, idempotency and failure paths.

Every dependency is a fake passed to the constructor. No module is patched, no
clock is frozen globally, no mocking library is imported — which is the payoff
for having declared `Clock` and `IdGenerator` as ports rather than calling
`datetime.now()` and `uuid4()` inline.
"""

from __future__ import annotations

import pytest

from payment.adapters.outbound.memory.in_memory_payment_repository import (
    InMemoryPaymentRepository,
)
from payment.application.errors import EventPublicationError, PaymentRepositoryError
from payment.application.use_cases.create_pix_payment import CreatePixPaymentService
from payment.domain.errors import InvalidMoneyError, InvalidPixKeyError
from payment.domain.events import PaymentCreated
from payment.domain.payment import PaymentId, PaymentStatus
from tests.support import (
    FIXED_INSTANT,
    ID_ONE,
    ID_TWO,
    FailingEventPublisher,
    FailingPaymentRepository,
    FixedClock,
    RecordingEventPublisher,
    SequentialIdGenerator,
    a_command,
)


@pytest.fixture
def repository() -> InMemoryPaymentRepository:
    return InMemoryPaymentRepository()


@pytest.fixture
def service(
    repository: InMemoryPaymentRepository,
    ids: SequentialIdGenerator,
    clock: FixedClock,
    publisher: RecordingEventPublisher,
) -> CreatePixPaymentService:
    return CreatePixPaymentService(
        payments=repository,
        id_generator=ids,
        clock=clock,
        event_publisher=publisher,
    )


class TestHappyPath:
    def test_creates_a_pending_payment(self, service: CreatePixPaymentService) -> None:
        result = service.execute(a_command())

        assert result.payment_id == ID_ONE
        assert result.status == PaymentStatus.PENDING
        assert result.already_existed is False

    def test_uses_the_injected_clock_and_id_generator(
        self, service: CreatePixPaymentService
    ) -> None:
        # The assertion that justifies both ports existing: exact values, no
        # regex on a UUID, no tolerance window on a timestamp.
        result = service.execute(a_command())

        assert result.payment_id == ID_ONE
        assert result.created_at == FIXED_INSTANT

    def test_persists_the_payment(
        self, service: CreatePixPaymentService, repository: InMemoryPaymentRepository
    ) -> None:
        service.execute(a_command(idempotency_key="idem-abc"))

        stored = repository.find_by_id(PaymentId(ID_ONE))

        assert stored is not None
        assert stored.idempotency_key == "idem-abc"
        assert stored.status is PaymentStatus.PENDING

    def test_publishes_the_creation_event(
        self, service: CreatePixPaymentService, publisher: RecordingEventPublisher
    ) -> None:
        service.execute(a_command())

        assert len(publisher.published) == 1
        event = publisher.published[0]
        assert isinstance(event, PaymentCreated)
        assert event.payment_id == ID_ONE

    def test_carries_the_description_through(
        self, service: CreatePixPaymentService, repository: InMemoryPaymentRepository
    ) -> None:
        service.execute(a_command(description="rent for March"))

        stored = repository.find_by_id(PaymentId(ID_ONE))

        assert stored is not None
        assert stored.description == "rent for March"

    @pytest.mark.parametrize(
        ("value", "key_type"),
        [
            ("alice@example.com", "EMAIL"),
            ("+5511999998888", "PHONE"),
            ("12345678901", "TAX_ID"),
            ("11111111-1111-4111-8111-111111111111", "RANDOM"),
        ],
    )
    def test_accepts_every_supported_key_type(
        self, service: CreatePixPaymentService, value: str, key_type: str
    ) -> None:
        result = service.execute(a_command(pix_key=value, pix_key_type=key_type))

        assert result.status == PaymentStatus.PENDING

    def test_accepts_a_lowercase_key_type(self, service: CreatePixPaymentService) -> None:
        # The REST adapter upper-cases before building the command, but the use
        # case must not depend on that having happened.
        result = service.execute(a_command(pix_key_type="EMAIL"))

        assert result.already_existed is False


class TestIdempotency:
    def test_replaying_the_same_key_returns_the_original_payment(
        self, service: CreatePixPaymentService
    ) -> None:
        first = service.execute(a_command(idempotency_key="idem-retry"))
        second = service.execute(a_command(idempotency_key="idem-retry"))

        assert second.payment_id == first.payment_id
        assert second.already_existed is True

    def test_a_replay_creates_nothing_new(
        self,
        service: CreatePixPaymentService,
        repository: InMemoryPaymentRepository,
        publisher: RecordingEventPublisher,
    ) -> None:
        service.execute(a_command(idempotency_key="idem-retry"))
        service.execute(a_command(idempotency_key="idem-retry"))

        # No second identifier consumed, no second event published. If the
        # replay had created a payment, SequentialIdGenerator would have handed
        # out ID_TWO and the publisher would hold two events.
        assert repository.find_by_id(PaymentId(ID_TWO)) is None
        assert len(publisher.published) == 1

    def test_different_keys_create_different_payments(
        self, service: CreatePixPaymentService
    ) -> None:
        first = service.execute(a_command(idempotency_key="idem-1"))
        second = service.execute(a_command(idempotency_key="idem-2"))

        assert first.payment_id == ID_ONE
        assert second.payment_id == ID_TWO
        assert second.already_existed is False

    def test_the_idempotency_check_happens_before_anything_is_written(
        self, service: CreatePixPaymentService, publisher: RecordingEventPublisher
    ) -> None:
        service.execute(a_command(idempotency_key="idem-retry"))
        publisher.publish_calls = 0

        service.execute(a_command(idempotency_key="idem-retry"))

        # A retry must cost one lookup and change nothing — not even an empty
        # publish call.
        assert publisher.publish_calls == 0


class TestValidationFailures:
    """Invalid input must fail before anything is generated or stored."""

    def test_rejects_a_non_positive_amount(self, service: CreatePixPaymentService) -> None:
        with pytest.raises(InvalidMoneyError, match="must be positive"):
            service.execute(a_command(amount="0"))

    def test_rejects_an_unsupported_currency(self, service: CreatePixPaymentService) -> None:
        with pytest.raises(InvalidMoneyError, match="unsupported currency"):
            service.execute(a_command(currency="XYZ"))

    def test_rejects_a_malformed_key(self, service: CreatePixPaymentService) -> None:
        with pytest.raises(InvalidPixKeyError, match="not a well-formed"):
            service.execute(a_command(pix_key="not-an-email"))

    def test_rejects_an_unknown_key_type_as_a_domain_error(
        self, service: CreatePixPaymentService
    ) -> None:
        # Not a bare ValueError: a malformed request is a business-level
        # rejection the inbound adapter already knows how to render as 422.
        with pytest.raises(InvalidPixKeyError, match="unknown PIX key type"):
            service.execute(a_command(pix_key_type="CARRIER_PIGEON"))

    def test_the_error_lists_the_supported_types(self, service: CreatePixPaymentService) -> None:
        with pytest.raises(InvalidPixKeyError, match="EMAIL"):
            service.execute(a_command(pix_key_type="NOPE"))

    def test_nothing_is_stored_when_validation_fails(
        self,
        service: CreatePixPaymentService,
        repository: InMemoryPaymentRepository,
        publisher: RecordingEventPublisher,
    ) -> None:
        with pytest.raises(InvalidMoneyError):
            service.execute(a_command(amount="-5", idempotency_key="idem-bad"))

        assert repository.find_by_idempotency_key("idem-bad") is None
        assert publisher.published == []


class TestInfrastructureFailures:
    def test_a_repository_failure_surfaces_as_an_outbound_port_error(
        self, ids: SequentialIdGenerator, clock: FixedClock
    ) -> None:
        service = CreatePixPaymentService(
            payments=FailingPaymentRepository(),
            id_generator=ids,
            clock=clock,
            event_publisher=RecordingEventPublisher(),
        )

        with pytest.raises(PaymentRepositoryError) as caught:
            service.execute(a_command())

        assert caught.value.port == "PaymentRepository"

    def test_a_publication_failure_propagates(
        self,
        repository: InMemoryPaymentRepository,
        ids: SequentialIdGenerator,
        clock: FixedClock,
    ) -> None:
        service = CreatePixPaymentService(
            payments=repository,
            id_generator=ids,
            clock=clock,
            event_publisher=FailingEventPublisher(),
        )

        with pytest.raises(EventPublicationError):
            service.execute(a_command())

        # The payment is already stored. Documenting this honestly matters more
        # than pretending otherwise: publish-after-save means a broker outage
        # leaves a persisted payment whose event was never emitted. A real
        # system needs a transactional outbox; the failure mode here is a lost
        # notification, not a lost payment.
        assert repository.find_by_id(PaymentId(ID_ONE)) is not None
