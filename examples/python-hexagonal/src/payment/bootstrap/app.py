"""HTTP application factory.

Bootstrap is where the framework is finally allowed to appear at the top level.
Everything inward has been framework-free, which is why this file can decide to
serve the same use case over FastAPI today and over something else later
without touching a single business rule.

A factory rather than a module-level ``app = FastAPI()``: a global app is
created at import time, which makes it impossible to build two differently
configured instances and forces tests to mutate shared state.
"""

from __future__ import annotations

from fastapi import FastAPI

from payment.adapters.inbound.rest.payment_controller import create_payment_router
from payment.application.ports.outbound.clock import Clock
from payment.application.ports.outbound.id_generator import IdGenerator
from payment.application.ports.outbound.payment_event_publisher import PaymentEventPublisher
from payment.application.ports.outbound.payment_repository import PaymentRepository
from payment.bootstrap.container import build_payment_components

_DESCRIPTION = """
Reference implementation of hexagonal architecture in Python.

**Educational only.** There is no real bank integration behind this API, no real
PIX endpoint, and no real payment is ever made. It exists to demonstrate ports,
adapters and architecture fitness functions.
"""


def create_app(
    *,
    payments: PaymentRepository | None = None,
    clock: Clock | None = None,
    id_generator: IdGenerator | None = None,
    event_publisher: PaymentEventPublisher | None = None,
) -> FastAPI:
    """Build the HTTP application over the given adapters.

    Adapters are passed straight through to the composition root, so an
    end-to-end test can pin the clock and the id generator while keeping the
    real controller, the real use case and the real aggregate in the path.
    """
    components = build_payment_components(
        payments=payments,
        clock=clock,
        id_generator=id_generator,
        event_publisher=event_publisher,
    )

    app = FastAPI(
        title="Payment (PIX) — hexagonal reference",
        description=_DESCRIPTION,
        version="0.1.0",
    )
    app.include_router(create_payment_router(components.create_pix_payment))

    @app.get("/health", tags=["operations"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
