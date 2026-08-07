"""Pytest fixtures.

Thin wrappers over the fakes and builders in `tests/support.py`. Keeping the
helpers in a separate module means a test can import a builder directly without
pytest ending up with two copies of this file under different module names.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from payment.adapters.outbound.memory.in_memory_payment_repository import (
    InMemoryPaymentRepository,
)
from tests.support import ID_ONE, ID_TWO, FixedClock, RecordingEventPublisher, SequentialIdGenerator


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture
def ids() -> SequentialIdGenerator:
    return SequentialIdGenerator(ID_ONE, ID_TWO)


@pytest.fixture
def publisher() -> RecordingEventPublisher:
    return RecordingEventPublisher()


@pytest.fixture
def in_memory_repository() -> Iterator[InMemoryPaymentRepository]:
    repository = InMemoryPaymentRepository()
    yield repository
    repository.clear()
