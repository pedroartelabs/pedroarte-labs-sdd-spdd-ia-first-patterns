---
id: SPEC-EXAMPLE-001
title: Create PIX payment
status: RELEASED
type: feature
owner: pedroartelabs
created_at: 2026-08-06
updated_at: 2026-08-06
languages:
  - java
  - python
bounded_context: payment
risk_level: medium
related_adrs:
  - ADR-0001
  - ADR-0003
  - ADR-0004
related_issues: []
prompt_artifacts:
  - PROMPT-EXAMPLE-001
---

# SPEC-EXAMPLE-001 — Create PIX payment

> **Educational only.** This specification describes a teaching example. There
> is no real bank integration, no real PIX endpoint, and no real personal or
> banking data. It exists to demonstrate the full SDD lifecycle end to end.

## Problem

A bounded context needs to accept a request to send money to a PIX key and
record that intent durably before anything else happens.

Today the reference repository has no worked example, so every explanation of
hexagonal architecture stops at a diagram. Readers cannot see what a port looks
like when a real invariant has to hold, what changes when time and identity are
injected rather than read, or what an idempotent create actually costs.

**Who is affected:** engineers adopting these patterns, and the AI agents
operating under them, both of which need one complete example rather than six
partial ones.

**Impact:** without it, the architecture rules read as opinion. With it, every
rule has a concrete referent and an executable check.

## Expected outcome

A caller can submit a payment request and receive a durable, uniquely
identified, `PENDING` payment. Retrying the same request produces the same
payment rather than a second one.

**Business value:** a demonstrable reference for accepting a financial
instruction safely — validated, idempotent, observable and testable — without
any real integration.

**Definition of Done**

- The use case exists in Java and Python with the same functional intent.
- Every acceptance criterion below is covered by an automated test.
- Architecture gates pass, and the negative fixtures are proven to be rejected.
- Coverage thresholds hold: 95% line on domain and application.
- Evidence is recorded with the exact commands executed and their real results.
- Traceability resolves from requirement to test.

## Scope

**Included**

- Accepting a PIX payment request through an inbound port.
- Validating amount, currency and PIX key.
- Generating an identifier and a creation timestamp through ports.
- Persisting the payment.
- Publishing a `PaymentCreated` domain event.
- Idempotent replay keyed by a caller-supplied idempotency key.

**Not included**

- Settlement, clearing, or any movement of money.
- Any real PIX or banking integration.
- Payment confirmation, cancellation or refund flows as *use cases*. The
  aggregate models the transitions; no inbound port exposes them yet.
- Authentication and authorisation.
- Rate limiting and fraud checks.
- Currency conversion.

**Assumptions**

- The caller supplies a stable idempotency key per logical request.
- A single bounded context owns payments; no cross-context transaction exists.
- Storage can enforce a unique constraint.

**Dependencies**

- None outside the bounded context.

## Ubiquitous language

| Term | Definition |
| --- | --- |
| **Payment** | A recorded intent to transfer a specific amount to a PIX key. Not a completed transfer. |
| **PIX key** | The destination identifier: an email, phone, tax id or random key. |
| **Amount** | An exact monetary value with a currency. Never a floating-point number. |
| **Idempotency key** | A caller-supplied token identifying one logical request across retries. |
| **PENDING** | Accepted and recorded; nothing has settled. |
| **Accept** | To validate and durably record a payment intent. Deliberately not "process". |

**Forbidden ambiguities**

- "Process a payment" — says nothing about whether money moved.
- "Transaction" — collides with the database meaning.
- "Send" — implies settlement this example does not perform.

## Domain model

**Aggregate root:** `Payment`

**Value objects**

- `PaymentId` — identity, validated by shape, never generated inside the domain.
- `Money` — exact amount plus currency.
- `PixKey` — destination key plus its type; knows how to mask itself for logs.

**Enumerations**

- `PaymentStatus` — `PENDING`, `CONFIRMED`, `FAILED`, `CANCELLED`.
- `PixKeyType` — `EMAIL`, `PHONE`, `TAX_ID`, `RANDOM`.

**Domain events**

- `PaymentCreated` — carries primitives and a **masked** key.

**Invariants**

- `INV-001` — An amount is strictly positive.
- `INV-002` — An amount carries at most minor-unit precision, and is never
  built from a float.
- `INV-003` — A currency is one of the supported codes, exact case.
- `INV-004` — An amount is finite. Infinity passes a naive positivity check.
- `INV-005` — A PIX key is well-formed **for its declared type**.
- `INV-006` — A new payment is `PENDING`.
- `INV-007` — Only a `PENDING` payment may transition; every other state is terminal.
- `INV-008` — A failure carries a non-blank reason.
- `INV-009` — `created_at` is timezone-aware.
- `INV-010` — An idempotency key is present and at most 64 characters.
- `INV-011` — A rejected transition leaves the aggregate unchanged.

**Domain errors**

`DomainError` ← `InvalidMoneyError`, `InvalidPixKeyError`,
`InvalidPaymentTransitionError`.

## Inbound port

**Name:** `CreatePixPaymentUseCase`

**Command:** `CreatePixPaymentCommand` — amount, currency, pix key, pix key
type, idempotency key, optional description. Primitives only, so an adapter can
build one from a parsed request without learning domain types.

**Result:** `CreatePixPaymentResult` — payment id, status, amount, currency,
created at, and `already_existed` so a replay is visible to the caller.

**Errors:** `DomainError` for a bad request; `OutboundPortError` for
infrastructure failure.

**Authorisation:** out of scope for this specification.

## Use case

**Pre-conditions:** the command is well-formed at the transport level.

**Main flow**

1. Convert amount and currency into `Money`; reject if invalid.
2. Convert key and key type into `PixKey`; reject if invalid.
3. Look up the idempotency key. If a payment exists, return it with
   `already_existed = true` and stop.
4. Obtain a new identifier from `IdGenerator`.
5. Obtain the current instant from `Clock`.
6. Build the `Payment` aggregate, which records `PaymentCreated`.
7. Persist the payment.
8. Drain and publish the recorded events.
9. Return the result.

**Alternative flows**

- Invalid input → domain error before anything is generated or written.
- Idempotent replay → step 3 returns; no identifier consumed, no event published.
- Storage failure → `PaymentRepositoryError`; nothing published.
- Publication failure → the payment is already stored. Documented honestly: this
  is publish-after-save, so a broker outage loses a notification, not a payment.
  A production system needs a transactional outbox.

**Post-conditions:** the payment is durable and exactly one `PaymentCreated` was
published per accepted payment.

**Idempotency:** guaranteed by the idempotency key, checked before any write.

**Concurrency:** the application-level check cannot win a race between two
simultaneous requests carrying the same key. The database unique constraint is
the actual guarantee.

## Outbound ports

### `PaymentRepository`

- **Responsibility:** store and retrieve payments.
- **Operations:** `save`, `find_by_id`, `find_by_idempotency_key`.
- **Not found:** returns empty, never raises. Absence is an ordinary outcome.
- **On failure:** raises `PaymentRepositoryError`; driver exceptions never cross
  the boundary.
- **Timeout / retry:** delegated to the adapter's technology; not modelled here.
- **Idempotency:** `save` is an upsert on identity.

### `IdGenerator`

- **Responsibility:** produce a unique `PaymentId`.
- **On failure:** `OutboundPortError`.

### `Clock`

- **Responsibility:** supply the current instant, timezone-aware.

### `PaymentEventPublisher`

- **Responsibility:** publish domain events.
- **Operations:** `publish(events)`; an empty batch is a no-op.
- **On failure:** `EventPublicationError`.

## Expected adapters

**Inbound**

- REST: `POST /payments`, idempotency key via the `Idempotency-Key` header.
  201 on creation, 200 on replay, 422 on a domain error, 503 on infrastructure
  failure.

**Outbound**

- In-memory repository — a real adapter, subject to the same contract suite.
- Relational repository — persistence models separate from domain entities.
- System clock, UUID identifier generator, logging event publisher.

**Composition:** a single composition root wires everything. Nothing imports it.

## Non-functional requirements

- **Security:** no secret, no real key, no real personal data. Logs carry masked
  keys only (SEC-004). Queries are parameterised (SEC-003).
- **Performance:** the in-memory path completes well inside a request budget;
  no specific latency target for a teaching example.
- **Observability:** each published event is logged with its type and a masked key.
- **Resilience:** infrastructure failure surfaces as 503, never as 4xx.
- **Compatibility:** Java on the current and previous LTS; Python 3.11–3.14.
- **Privacy:** PIX keys are masked wherever they are rendered.

## Acceptance criteria

- **AC-001** — Given a valid request, When it is submitted, Then a `PENDING`
  payment is created with a generated identifier and returned to the caller.
- **AC-002** — Given a valid request, When it is submitted, Then exactly one
  `PaymentCreated` event is published.
- **AC-003** — Given a request already submitted with an idempotency key, When
  the same key is submitted again, Then the original payment is returned,
  `already_existed` is true, and no new payment or event is created.
- **AC-004** — Given an amount of zero or less, When submitted, Then the request
  is rejected with a domain error and nothing is stored.
- **AC-005** — Given an unsupported currency, When submitted, Then the request
  is rejected with a domain error.
- **AC-006** — Given a PIX key malformed for its declared type, When submitted,
  Then the request is rejected with a domain error.
- **AC-007** — Given an unknown PIX key type, When submitted, Then the request
  is rejected with a domain error naming the supported types.
- **AC-008** — Given the repository is unavailable, When a request is submitted,
  Then the caller receives a 503 carrying no internal detail.
- **AC-009** — Given a stored payment, When it is retrieved, Then the amount is
  exact and the timestamp is still timezone-aware.
- **AC-010** — Given any repository implementation, When the contract suite
  runs, Then every implementation behaves identically.
- **AC-011** — Given a payment in a terminal state, When a transition is
  attempted, Then it is rejected and the aggregate is unchanged.
- **AC-012** — Given a published event, When it is rendered, Then the PIX key is
  masked.

## Test strategy

- **Domain** — invariants, value semantics, lifecycle transitions, event
  recording. Property-based tests for monetary arithmetic. No framework, no I/O.
- **Application** — use case orchestration with hand-written fakes for all four
  outbound ports. Success, validation failure, infrastructure failure and
  idempotent replay.
- **Contract** — one suite parametrised over every `PaymentRepository`
  implementation, so in-memory and relational cannot diverge.
- **Integration** — relational adapter only: error translation, the unique
  constraint, and timezone preservation.
- **Architecture** — dependency direction, adapter isolation, cycles, forbidden
  framework imports, composition, plus the negative fixtures.
- **End-to-end** — HTTP in, HTTP out, through the real composition root with
  only the clock and identifier generator replaced.
- **Security** — static analysis; assertions that error responses leak no
  internal detail and that logs carry masked keys.

**Coverage:** domain and application ≥ 95% line, ≥ 90% branch.

## Migration and rollback

- **Data impact:** creates a `payments` table with a unique index on the
  idempotency key. No existing data.
- **Compatibility:** new endpoint; nothing pre-existing changes.
- **Rollout:** ships with the reference example; not deployed anywhere.
- **Rollback:** remove the module. No consumer depends on it.
- **Feature flag:** not applicable.

## Risks

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| Readers mistake the example for a usable payment implementation | Medium | High | Explicit warnings in the spec, README, API description and an end-to-end test asserting the OpenAPI description says "Educational only" |
| Publish-after-save loses an event on broker failure | Medium | Medium | Documented explicitly as a known limitation with the outbox pattern named as the real fix; a test pins the actual behaviour |
| SQLite and PostgreSQL disagree about timezones, breaking INV-009 silently | High | High | `UtcDateTime` decorator in the adapter, plus a contract test asserting timezone survival on every implementation |
| Concurrent requests with the same idempotency key create duplicates | Medium | High | Database unique constraint, plus an integration test proving it fires |
| Architecture rules pass without ever being able to fail | Medium | Critical | Negative fixtures asserted as rejected; verified by removing a violation and confirming the tests fail |

## Open questions

None blocking. Resolved questions are recorded in
[`clarifications.md`](clarifications.md).

Deferred, non-blocking, and tracked for a future specification:

- Should confirmation and cancellation be exposed as inbound ports?
- Should the outbox pattern replace publish-after-save in the reference?

Neither affects the acceptance criteria above.
