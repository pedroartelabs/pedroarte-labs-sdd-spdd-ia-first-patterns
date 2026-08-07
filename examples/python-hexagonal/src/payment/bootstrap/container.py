"""Composition root.

This is the one module allowed to know every other module (ARCH-007). It wires
concrete adapters into the use case and hands back something the rest of the
system can hold without knowing what is inside it.

The wiring is plain constructor calls. No framework, no decorators, no registry,
no service locator — because the entire dependency graph of this application
fits in one readable function, and a DI container would hide that rather than
help. If the graph ever outgrows this file, that is a signal about the design,
not a reason to reach for magic.
"""

from __future__ import annotations

from dataclasses import dataclass

from payment.adapters.outbound.memory.in_memory_payment_repository import (
    InMemoryPaymentRepository,
)
from payment.adapters.outbound.system.logging_event_publisher import LoggingEventPublisher
from payment.adapters.outbound.system.system_clock import SystemClock
from payment.adapters.outbound.system.uuid_id_generator import UuidIdGenerator
from payment.application.ports.inbound.create_pix_payment import CreatePixPaymentUseCase
from payment.application.ports.outbound.clock import Clock
from payment.application.ports.outbound.id_generator import IdGenerator
from payment.application.ports.outbound.payment_event_publisher import PaymentEventPublisher
from payment.application.ports.outbound.payment_repository import PaymentRepository
from payment.application.use_cases.create_pix_payment import CreatePixPaymentService


@dataclass(frozen=True, slots=True)
class PaymentComponents:
    """Everything the transport layer needs, already wired."""

    create_pix_payment: CreatePixPaymentUseCase
    payments: PaymentRepository


def build_payment_components(
    *,
    payments: PaymentRepository | None = None,
    clock: Clock | None = None,
    id_generator: IdGenerator | None = None,
    event_publisher: PaymentEventPublisher | None = None,
) -> PaymentComponents:
    """Wire the payment use case over the given adapters.

    Every dependency is injectable and every one has a working default, which
    is what lets an end-to-end test replace exactly one adapter — a fixed clock,
    say — while keeping the rest of the real composition intact. Tests that
    build the object graph by hand tend to stop resembling production.

    The default repository is in-memory so the example runs with no
    infrastructure at all. Pass a ``SqlPaymentRepository`` to exercise the
    persistence path; both satisfy the same contract suite.
    """
    repository: PaymentRepository = (
        payments if payments is not None else InMemoryPaymentRepository()
    )

    use_case = CreatePixPaymentService(
        payments=repository,
        id_generator=id_generator if id_generator is not None else UuidIdGenerator(),
        clock=clock if clock is not None else SystemClock(),
        event_publisher=(
            event_publisher if event_publisher is not None else LoggingEventPublisher()
        ),
    )

    return PaymentComponents(create_pix_payment=use_case, payments=repository)
