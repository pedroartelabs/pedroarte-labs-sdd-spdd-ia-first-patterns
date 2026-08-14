# Test plan — {SPEC-ID}

What each level proves, and why it exists at that level rather than another.

## Principle

Tests are organised by **what they prove**, not by folder habit.

## Level 1 — Domain

**Proves:** invariants, value semantics, lifecycle, event recording.
**Characteristics:** microseconds, pure, no framework, no I/O.

| Target | Cases |
| --- | --- |

## Level 2 — Application

**Proves:** orchestration, idempotency, failure handling.
**Doubles:** hand-written fakes for all outbound ports.

| Scenario | Criterion |
| --- | --- |

## Level 3 — Contract

**Proves:** every implementation of a port behaves identically.
**Mechanism:** one suite, parametrised over each implementation.

## Level 4 — Integration

**Proves:** what is true only of a specific technology adapter.

## Level 5 — Architecture

**Proves:** the structure itself. Deterministic and blocking.

## Level 6 — End-to-end

**Proves:** the whole slice through the real composition root.
**Few, representative, stable.**

## Coverage

| Scope | Line | Branch |
| --- | --- | --- |
| Domain + application | ≥ 95% | ≥ 90% |
| Overall | ≥ 85% | ≥ 75% |

## Explicitly not tested

_What is out of scope for this specification and why._
