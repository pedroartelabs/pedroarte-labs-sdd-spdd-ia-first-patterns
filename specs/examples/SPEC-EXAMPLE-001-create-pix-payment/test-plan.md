# Test plan — SPEC-EXAMPLE-001

What each level proves, and why it exists at that level rather than another.

## Principle

Tests are organised by **what they prove**, not by folder habit. Pushing a test
down a level makes it faster and more precise; pushing it up makes it slower and
vaguer. The correct level is the lowest one that can actually observe the
behaviour.

## Level 1 — Domain

**Proves:** invariants, value semantics, lifecycle, event recording.
**Characteristics:** microseconds, pure, no framework, no I/O, no clock.

| Target | Cases |
| --- | --- |
| `Money` | float rejection, NaN, Infinity, non-positive, sub-cent precision, unsupported and lowercase currency, immutability, hashability, cross-currency addition |
| `PixKey` | valid and malformed per type, blank, over-long, unknown type, valid-value-wrong-declared-type, masking per type |
| `PaymentId` | UUID shape accepted, everything else rejected |
| `Payment` | PENDING on creation, event recorded with a masked key, naive timestamp rejected, idempotency key required and bounded, description bounded |
| lifecycle | confirm / cancel / fail from PENDING, every terminal transition rejected, failure requires a reason, rejected transition leaves state unchanged |
| identity | equal by id regardless of state |

**Property-based** where a law exists rather than an example: addition is
commutative, every positive cent amount is valid, and a string round trip is
**exact**. That last one is the whole reason `Money` exists.

## Level 2 — Application

**Proves:** orchestration, idempotency, failure handling.
**Doubles:** hand-written fakes for all four outbound ports. No mocking library.

A fake asserts on outcomes; a mock asserts on calls. The first survives a
refactor, the second breaks on one.

| Scenario | Criterion |
| --- | --- |
| Happy path creates PENDING and publishes once | AC-001, AC-002 |
| Exact id and timestamp come from the ports | AC-001 |
| Replay returns the original, consumes no id, publishes nothing | AC-003 |
| Distinct keys create distinct payments | AC-003 |
| Each validation failure stores and publishes nothing | AC-004…007 |
| Repository failure surfaces as `OutboundPortError` | AC-008 |
| Publication failure propagates, payment stays stored | documented limitation |

## Level 3 — Contract

**Proves:** every implementation of a port behaves identically.
**Mechanism:** one suite, parametrised over each implementation.

This is the level that stops the fast in-memory adapter used by every unit test
from quietly disagreeing with the relational one that runs in production. It is
also what caught the SQLite timezone divergence — see
[CQ-005](clarifications.md#cq-005--must-created_at-carry-a-timezone).

Cases: round trip, not-found returns empty, save-twice updates rather than
duplicates, failure reason persisted, lookup by idempotency key is exact-match,
lookup reflects latest state, exact amount preserved, **timestamp stays
timezone-aware**. Covers AC-009, AC-010.

## Level 4 — Integration

**Proves:** what is true only of the relational adapter.

Anything the port promises belongs in Level 3; only technology-specific
behaviour belongs here.

- Missing table → `PaymentRepositoryError`, on both read paths and on save.
- The driver message does not reach the caller (SEC-004), but is chained for logs.
- The unique index on the idempotency key fires under duplicate insert.
- `UtcDateTime` refuses a naive value and normalises to UTC.

## Level 5 — Architecture

**Proves:** the structure itself. Deterministic and blocking.

- All contracts kept on the real project.
- The expected **number** of contracts ran — a contract matching nothing reports
  KEPT forever.
- Each contract name carries its `ARCH-xxx` id, so a failure is lookup-able.
- `.importlinter` has not drifted from the canonical policy, in **both**
  directions.
- Negative fixtures: valid accepted, each invalid one **rejected**, by the
  **right** rule, and by **exactly one** rule.

## Level 6 — End-to-end

**Proves:** the whole slice through the real composition root.
**Few, representative, stable.** Only the clock and id generator are replaced.

Health, creation, 201-vs-200 on replay, idempotency key required, Pydantic-level
rejection, domain-level rejection, 503 with no leaked internals, OpenAPI
generated and stating "Educational only".

## Coverage

| Scope | Line | Branch |
| --- | --- | --- |
| Domain + application | ≥ 95% | ≥ 90% |
| Repository overall | ≥ 85% | ≥ 75% |

A floor, not a target. A covered line is not a tested behaviour — which is why
the domain level carries property tests and the architecture level carries
negative fixtures.

## Mutation testing

Runs on a schedule, not on the pull-request path. Valuable signal, poor
fit for the critical path: slow feedback that arrives after a developer has
context-switched is feedback that does not get acted on.

## Explicitly not tested

- Real PIX or bank integration — none exists.
- Settlement — out of scope.
- Load and performance — no target for a teaching example.
- Confirm/cancel **use cases** — the aggregate transitions are tested; no
  inbound port exposes them.
