"""Logging implementation of the ``PaymentEventPublisher`` port.

Stands in for a broker so the example runs with no infrastructure. Swapping it
for Kafka, an outbox table or an in-process bus means writing one class and
changing one line in the composition root — no use case, no aggregate and no
test of either has to know.

What it logs is as deliberate as that it logs. ``PaymentCreated`` carries a
masked key rather than a raw one, so this adapter cannot leak a customer
identifier into a log aggregator that a much wider audience can read (SEC-004).
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from payment.domain.events import DomainEvent

_logger = logging.getLogger(__name__)


class LoggingEventPublisher:
    """Writes domain events to the application log."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or _logger

    def publish(self, events: Sequence[DomainEvent]) -> None:
        # An empty batch is a no-op by contract, so callers never need to ask
        # "were there any events?" before publishing.
        for event in events:
            self._logger.info(
                "domain event published: %s",
                event,
                extra={"event_type": type(event).__name__},
            )
