"""Outbound port: domain event publication.

The application decides *that* events are published and *when*. How they travel
— Kafka, an outbox table, a log line, an in-process handler — is an adapter
decision that must not leak back inward.

Note the port takes domain events, not messages. Serialization, topic naming,
partition keys, headers and schema evolution all belong to the adapter.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from payment.domain.events import DomainEvent


class PaymentEventPublisher(Protocol):
    """Publishes events recorded by the payment aggregate."""

    def publish(self, events: Sequence[DomainEvent]) -> None:
        """Publish a batch of domain events.

        Takes a sequence rather than a single event so an implementation can
        publish a unit of work atomically where its technology allows it.
        Publishing an empty sequence must be a no-op, which keeps the calling
        code free of "did anything happen?" branches.

        Raises:
            payment.application.errors.EventPublicationError: publication failed.
        """
        ...
