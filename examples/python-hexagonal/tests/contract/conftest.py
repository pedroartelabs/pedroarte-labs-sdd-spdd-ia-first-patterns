"""Contract-test fixtures: one suite, every implementation.

The `repository` fixture is parametrised over every implementation of
`PaymentRepository`. The single test module in this package therefore runs
twice — once against the in-memory adapter and once against the SQL adapter —
and both must behave identically.

This is the mechanism that stops the fast implementation every unit test relies
on from quietly disagreeing with the one that runs in production. Without it,
"the tests pass" and "the system works" gradually stop being the same claim.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from payment.adapters.outbound.memory.in_memory_payment_repository import (
    InMemoryPaymentRepository,
)
from payment.adapters.outbound.persistence.models import Base
from payment.adapters.outbound.persistence.sql_payment_repository import (
    SqlPaymentRepository,
)
from payment.application.ports.outbound.payment_repository import PaymentRepository


@pytest.fixture
def sql_session() -> Iterator[Session]:
    """A SQLite in-memory database, created and dropped per test.

    SQLite is used here because it needs no Docker and keeps the contract suite
    runnable everywhere. It is not identical to the production engine, which is
    exactly why `UtcDateTime` exists in the persistence adapter: the timezone
    behaviour differs, and the adapter — not the domain — absorbs it.
    """
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    with Session(engine, future=True) as session:
        yield session
    engine.dispose()


@pytest.fixture(params=["in-memory", "sql"])
def repository(request: pytest.FixtureRequest, sql_session: Session) -> PaymentRepository:
    if request.param == "in-memory":
        return InMemoryPaymentRepository()
    return SqlPaymentRepository(sql_session)
