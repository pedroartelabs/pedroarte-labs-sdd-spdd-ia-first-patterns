# ADR-0004: Import Linter as the Python architecture fitness function

## Status

Accepted

## Context

Python has no compile-time module system that can refuse an import. Any file
can import any other file, and the violation is only discoverable at runtime
or through static analysis.

## Decision

Use Import Linter with six contracts that run as pytest tests. Each contract
maps to one or more ARCH rules and is named after them. The contracts are
kept in `.importlinter` and verified against the canonical policy by a drift
test.

Negative architecture fixtures (deliberately broken packages) prove each
contract can actually fail.

## Consequences

### Positive

- Architecture enforcement runs in the test suite, on every PR
- Negative fixtures prove enforcement capability
- Contract naming links directly to ARCH rule IDs

### Negative

- Import Linter only checks top-level imports; runtime `importlib` calls are invisible
- Adding a new bounded context requires new contracts

### Neutral

- Contracts are checked bidirectionally against canonical policy

## Compliance

- **Architecture rules affected:** ARCH-001, ARCH-002, ARCH-003, ARCH-004, ARCH-005, ARCH-007, ARCH-012
- **Fitness functions:** Import Linter contracts, test_contracts_match_policy.py, test_fixtures_are_rejected.py
- **Review date:** 2026-11-06
