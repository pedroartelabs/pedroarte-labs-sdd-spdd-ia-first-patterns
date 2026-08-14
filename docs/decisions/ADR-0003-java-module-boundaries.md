# ADR-0003: Java multi-module to enforce boundaries at compile time

## Status

Accepted

## Context

Java has no language-level mechanism to prevent imports between packages in the
same JAR. ArchUnit tests can check at test time, but a developer can delete
the test. Maven module boundaries enforce at compile time — the build itself
refuses a forbidden dependency.

## Decision

Structure the Java reference as seven Maven modules:
payment-domain, payment-application, payment-adapter-in-rest,
payment-adapter-out-memory, payment-adapter-out-persistence,
payment-bootstrap, payment-architecture-tests.

Each module's POM declares only the dependencies it is allowed to have.

## Consequences

### Positive

- Architecture violations fail at compile time, not test time
- A deleted ArchUnit test does not remove the boundary
- Each module can be released independently if needed

### Negative

- More complex build configuration
- IDE needs to handle multi-module projects

### Neutral

- ArchUnit tests still exist as a second layer of verification

## Compliance

- **Architecture rules affected:** ARCH-002, ARCH-003, ARCH-004, ARCH-005, ARCH-007
- **Fitness functions:** Maven dependency resolution, ArchUnit tests
- **Review date:** 2026-11-06
