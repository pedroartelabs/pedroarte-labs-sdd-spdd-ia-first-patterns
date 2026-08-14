# ADR-0001: Hexagonal architecture per bounded context

## Status

Accepted

## Context

The repository needs a reference architecture that demonstrates clear separation
between business logic and infrastructure, supports multiple implementations of
the same port, and enables architecture enforcement through automated fitness
functions.

## Decision

Use hexagonal architecture (ports and adapters) organised by bounded context
first, then hexagonal layers inside. Dependencies always point inward: domain
knows nothing about the outside; application defines ports; adapters implement
them; bootstrap wires everything together.

## Consequences

### Positive

- Domain logic is testable without any framework
- Infrastructure is swappable per-port (in-memory for tests, SQL for production)
- Architecture rules are enforceable by Import Linter (Python) and ArchUnit (Java)

### Negative

- More files and indirection than a flat structure
- Explicit mapping between domain and persistence models

### Neutral

- Requires discipline to keep the boundaries clean

## Compliance

- **Architecture rules affected:** ARCH-001 through ARCH-013
- **Fitness functions:** Import Linter contracts, ArchUnit tests, Maven module boundaries
- **Review date:** 2026-11-06
