"""SQL adapter specifics.

The behaviour every repository must share lives in `tests/contract/`. What
remains here is what is true only of the relational implementation: failure
translation, database-level constraints, and the timezone decorator.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from payment.adapters.outbound.persistence.models import Base, PaymentRow, UtcDateTime
from payment.adapters.outbound.persistence.sql_payment_repository import (
    SqlPaymentRepository,
)
from payment.application.errors import PaymentRepositoryError
from payment.domain.payment import PaymentId
from tests.support import ID_ONE, ID_TWO, a_payment

pytestmark = pytest.mark.integration


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    with Session(engine, future=True) as open_session:
        yield open_session
    engine.dispose()


@pytest.fixture
def repository(session: Session) -> SqlPaymentRepository:
    return SqlPaymentRepository(session)


class TestErrorTranslation:
    """ARCH-011: a driver exception must never cross the boundary."""

    def test_a_missing_table_becomes_a_repository_error_on_save(
        self, session: Session, repository: SqlPaymentRepository
    ) -> None:
        session.execute(text("DROP TABLE payments"))

        # The application layer must never have to catch SQLAlchemyError; if it
        # did, it would depend on SQLAlchemy while claiming not to.
        with pytest.raises(PaymentRepositoryError) as caught:
            repository.save(a_payment())

        assert caught.value.port == "PaymentRepository"

    def test_the_driver_message_is_not_leaked_outward(
        self, session: Session, repository: SqlPaymentRepository
    ) -> None:
        session.execute(text("DROP TABLE payments"))

        with pytest.raises(PaymentRepositoryError) as caught:
            repository.save(a_payment())

        # SEC-004: driver messages can carry hosts, schemas and occasionally
        # credentials. The original is chained for logs, not for the caller.
        message = str(caught.value)
        assert "sqlite" not in message.lower()
        assert caught.value.__cause__ is not None

    def test_a_dropped_table_becomes_a_repository_error_on_read(
        self, session: Session, repository: SqlPaymentRepository
    ) -> None:
        session.execute(text("DROP TABLE payments"))

        with pytest.raises(PaymentRepositoryError, match="could not read payment by id"):
            repository.find_by_id(PaymentId(ID_ONE))

    def test_a_dropped_table_becomes_a_repository_error_on_key_lookup(
        self, session: Session, repository: SqlPaymentRepository
    ) -> None:
        session.execute(text("DROP TABLE payments"))

        with pytest.raises(PaymentRepositoryError, match="idempotency key"):
            repository.find_by_idempotency_key("idem-001")


class TestDatabaseConstraints:
    def test_the_idempotency_key_is_unique_at_the_database_level(
        self, session: Session, repository: SqlPaymentRepository
    ) -> None:
        repository.save(a_payment(payment_id=ID_ONE, idempotency_key="idem-dup"))
        session.commit()

        # The application checks the key before creating, but only the database
        # can win the race between two concurrent requests carrying the same
        # key. An application-level check alone loses exactly the race it exists
        # to prevent.
        with pytest.raises((IntegrityError, PaymentRepositoryError)):
            repository.save(a_payment(payment_id=ID_TWO, idempotency_key="idem-dup"))
            session.commit()


class TestUtcDateTime:
    """The decorator that keeps the domain's timezone invariant true on SQLite."""

    def test_refuses_to_store_a_naive_datetime(self, session: Session) -> None:
        row = PaymentRow(
            id=ID_ONE,
            amount=1,
            currency="BRL",
            pix_key="alice@example.com",
            pix_key_type="EMAIL",
            status="PENDING",
            created_at=datetime(2026, 3, 14, 15, 9, 26),  # noqa: DTZ001
            idempotency_key="idem-naive",
        )
        session.add(row)

        with pytest.raises(Exception, match="naive datetime"):
            session.flush()

    def test_normalises_to_utc_on_the_way_in(
        self, session: Session, repository: SqlPaymentRepository
    ) -> None:
        repository.save(a_payment())
        session.flush()
        session.expunge_all()

        found = repository.find_by_id(PaymentId(ID_ONE))

        assert found is not None
        assert found.created_at.tzinfo is not None
        assert found.created_at.utcoffset() == UTC.utcoffset(None)

    def test_process_result_value_passes_none_through(self) -> None:
        assert UtcDateTime().process_result_value(None, None) is None  # type: ignore[arg-type]

    def test_process_bind_param_passes_none_through(self) -> None:
        assert UtcDateTime().process_bind_param(None, None) is None  # type: ignore[arg-type]
