"""The PaymentRepository contract.

One suite, executed against every implementation via the parametrised
`repository` fixture. Each test below therefore runs twice: in-memory and SQL.

What belongs here is behaviour the *port* promises, expressed without naming any
technology. Anything that mentions a session, a table or a driver belongs in
`tests/integration/` instead.
"""

from __future__ import annotations

import pytest

from payment.application.ports.outbound.payment_repository import PaymentRepository
from payment.domain.payment import PaymentId, PaymentStatus
from tests.support import ID_ONE, ID_TWO, a_payment

pytestmark = pytest.mark.contract


class TestSaveAndFindById:
    def test_a_saved_payment_can_be_found(self, repository: PaymentRepository) -> None:
        payment = a_payment()

        repository.save(payment)

        found = repository.find_by_id(PaymentId(ID_ONE))
        assert found is not None
        assert found.id == payment.id

    def test_finding_an_unknown_id_returns_none(self, repository: PaymentRepository) -> None:
        # "Not found" is an ordinary outcome, not an exceptional one. Raising
        # here would force every caller into a try/except for the common case.
        assert repository.find_by_id(PaymentId(ID_TWO)) is None

    def test_the_full_aggregate_survives_a_round_trip(self, repository: PaymentRepository) -> None:
        payment = a_payment(amount="1234.56", description="rent for March")

        repository.save(payment)
        found = repository.find_by_id(payment.id)

        assert found is not None
        assert found.amount == payment.amount
        assert found.pix_key == payment.pix_key
        assert found.status is payment.status
        assert found.idempotency_key == payment.idempotency_key
        assert found.description == payment.description

    def test_the_timestamp_stays_timezone_aware(self, repository: PaymentRepository) -> None:
        # The invariant `Payment` enforces on creation must survive storage.
        # SQLite has no timezone concept, so without the adapter's UtcDateTime
        # decorator this passes in memory and fails in SQL — which is precisely
        # the kind of divergence a shared contract suite exists to catch.
        payment = a_payment()

        repository.save(payment)
        found = repository.find_by_id(payment.id)

        assert found is not None
        assert found.created_at.tzinfo is not None
        assert found.created_at == payment.created_at

    def test_the_exact_amount_is_preserved(self, repository: PaymentRepository) -> None:
        payment = a_payment(amount="0.01")

        repository.save(payment)
        found = repository.find_by_id(payment.id)

        assert found is not None
        assert str(found.amount.amount) == "0.01"


class TestSaveIsIdempotentOnIdentity:
    def test_saving_twice_updates_rather_than_duplicating(
        self, repository: PaymentRepository
    ) -> None:
        payment = a_payment()
        repository.save(payment)

        payment.confirm()
        repository.save(payment)

        found = repository.find_by_id(payment.id)
        assert found is not None
        assert found.status is PaymentStatus.CONFIRMED

    def test_a_failure_reason_is_persisted(self, repository: PaymentRepository) -> None:
        payment = a_payment()
        repository.save(payment)

        payment.fail("insufficient funds")
        repository.save(payment)

        found = repository.find_by_id(payment.id)
        assert found is not None
        assert found.status is PaymentStatus.FAILED
        assert found.failure_reason == "insufficient funds"


class TestFindByIdempotencyKey:
    def test_finds_a_payment_by_its_idempotency_key(self, repository: PaymentRepository) -> None:
        payment = a_payment(idempotency_key="idem-xyz")
        repository.save(payment)

        found = repository.find_by_idempotency_key("idem-xyz")

        assert found is not None
        assert found.id == payment.id

    def test_an_unknown_key_returns_none(self, repository: PaymentRepository) -> None:
        assert repository.find_by_idempotency_key("never-used") is None

    def test_keys_are_matched_exactly(self, repository: PaymentRepository) -> None:
        repository.save(a_payment(idempotency_key="idem-xyz"))

        assert repository.find_by_idempotency_key("IDEM-XYZ") is None
        assert repository.find_by_idempotency_key("idem-xy") is None

    def test_distinct_keys_resolve_to_distinct_payments(
        self, repository: PaymentRepository
    ) -> None:
        repository.save(a_payment(payment_id=ID_ONE, idempotency_key="idem-1"))
        repository.save(a_payment(payment_id=ID_TWO, idempotency_key="idem-2"))

        first = repository.find_by_idempotency_key("idem-1")
        second = repository.find_by_idempotency_key("idem-2")

        assert first is not None
        assert second is not None
        assert first.id != second.id

    def test_lookup_reflects_the_latest_state(self, repository: PaymentRepository) -> None:
        payment = a_payment(idempotency_key="idem-xyz")
        repository.save(payment)
        payment.cancel()
        repository.save(payment)

        found = repository.find_by_idempotency_key("idem-xyz")

        assert found is not None
        assert found.status is PaymentStatus.CANCELLED
