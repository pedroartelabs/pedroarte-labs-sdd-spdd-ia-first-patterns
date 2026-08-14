# ADR-0006: Negative architecture fixtures proving enforcement capability

## Status

Accepted

## Context

An architecture rule that has never failed is a rule nobody has verified.
Showing that valid code passes proves the tooling runs; it does not prove it
catches violations.

## Decision

Ship deliberately broken code in `architecture-fixtures/` with tests that
assert the violations are detected. Each invalid fixture names the ARCH rule
it violates. Tests verify three things: the fixture is rejected, the correct
rule fires, and only one rule fires (no false positives).

## Consequences

### Positive

- Proves enforcement capability, not just green-on-valid
- Meta-verification: removing the violation makes the test fail
- Each rule has a documented example of what violation looks like

### Negative

- More code to maintain (fixture packages, additional tests)

### Neutral

- Fixtures are tiny packages with one file each

## Compliance

- **Architecture rules affected:** ARCH-001, ARCH-004, ARCH-005, TEST-005
- **Fitness functions:** test_fixtures_are_rejected.py
- **Review date:** 2026-11-06
