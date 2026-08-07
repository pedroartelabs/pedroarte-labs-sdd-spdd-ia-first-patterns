"""Ports: the application's boundary, in both directions.

    inbound/   what the application offers to the outside world
    outbound/  what the application requires from infrastructure

Ports are `typing.Protocol` definitions. Structural typing suits this job well:
an adapter satisfies a port by having the right shape, without inheriting from
it and without importing anything beyond the domain types in the signature. The
coupling stays one-directional even in the type system.

Port names describe responsibilities, never technologies. `PaymentRepository`,
not `SqlPaymentRepository`; `PaymentEventPublisher`, not `KafkaPublisher`
(ARCH-008 / NAM-001). A technology name in a port is a boundary that has
already leaked.
"""

__all__: list[str] = []
