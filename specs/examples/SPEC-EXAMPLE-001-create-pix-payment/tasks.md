# Task plan — SPEC-EXAMPLE-001

Small, ordered, individually verifiable steps. Each one states what proves it.

The ordering is inside-out on purpose: the domain is finished and fully tested
before any port exists, and every port exists before any adapter does. Building
outside-in tends to let transport concerns dictate the shape of the model.

## Phase 1 — Domain

| # | Task | Proven by | Status |
| --- | --- | --- | --- |
| 1.1 | Domain error hierarchy | compiles | ✅ |
| 1.2 | `Money` with INV-001…004 | float, NaN, Infinity, precision, currency tests | ✅ |
| 1.3 | `Money` arithmetic | commutativity + exact round-trip property tests | ✅ |
| 1.4 | `PixKey` with INV-005 | per-type valid and malformed tests | ✅ |
| 1.5 | `PixKey.masked()` | masking tests; raw value absent from output | ✅ |
| 1.6 | `PaymentId` validated by shape | rejects non-UUID; imports no uuid library | ✅ |
| 1.7 | `Payment.create` with INV-006, 009, 010 | creation tests | ✅ |
| 1.8 | Lifecycle transitions, INV-007, 008, 011 | transition tests, incl. unchanged-on-reject | ✅ |
| 1.9 | `PaymentCreated` with a masked key | event tests | ✅ |
| 1.10 | Identity-based equality | equality tests | ✅ |

**Gate:** domain tests pass with no framework, no I/O and no clock read.

## Phase 2 — Ports

| # | Task | Proven by | Status |
| --- | --- | --- | --- |
| 2.1 | `CreatePixPaymentCommand` / `Result` | compiles | ✅ |
| 2.2 | `CreatePixPaymentUseCase` inbound port | compiles | ✅ |
| 2.3 | `PaymentRepository` | compiles | ✅ |
| 2.4 | `Clock`, `IdGenerator` | compiles | ✅ |
| 2.5 | `PaymentEventPublisher` | compiles | ✅ |
| 2.6 | Application error hierarchy | compiles | ✅ |

**Gate:** no port name contains a technology (ARCH-008).

## Phase 3 — Use case

| # | Task | Proven by | Status |
| --- | --- | --- | --- |
| 3.1 | Fakes for all four outbound ports | used by every test below | ✅ |
| 3.2 | Happy path | AC-001, AC-002 | ✅ |
| 3.3 | Exact id and timestamp from ports | AC-001 | ✅ |
| 3.4 | Idempotent replay before any write | AC-003 | ✅ |
| 3.5 | Validation failures write nothing | AC-004…007 | ✅ |
| 3.6 | Infrastructure failures propagate | AC-008 | ✅ |

**Gate:** application coverage ≥ 95% line; no mocking library used.

## Phase 4 — Outbound adapters

| # | Task | Proven by | Status |
| --- | --- | --- | --- |
| 4.1 | In-memory repository | contract suite | ✅ |
| 4.2 | Persistence model separate from aggregate | ARCH-009 | ✅ |
| 4.3 | Relational repository + mapping | contract suite | ✅ |
| 4.4 | Driver exception translation | AC-008, ARCH-011 | ✅ |
| 4.5 | `UtcDateTime` decorator | AC-009 on every implementation | ✅ |
| 4.6 | Unique index on idempotency key | integration test | ✅ |
| 4.7 | System clock, UUID ids, logging publisher | e2e | ✅ |

**Gate:** AC-010 — one contract suite, every implementation, identical behaviour.

## Phase 5 — Inbound adapter

| # | Task | Proven by | Status |
| --- | --- | --- | --- |
| 5.1 | Request/response DTOs | e2e | ✅ |
| 5.2 | Controller calling only the inbound port | ARCH-004 | ✅ |
| 5.3 | 201 create / 200 replay | AC-003 | ✅ |
| 5.4 | Domain error → 422 | AC-004…007 | ✅ |
| 5.5 | Infrastructure error → 503, no internal detail | AC-008 | ✅ |

**Gate:** no business rule in the controller.

## Phase 6 — Composition

| # | Task | Proven by | Status |
| --- | --- | --- | --- |
| 6.1 | Composition root | e2e | ✅ |
| 6.2 | App factory with injectable adapters | e2e | ✅ |
| 6.3 | Nothing imports bootstrap | ARCH-007 | ✅ |

## Phase 7 — Architecture proofs

| # | Task | Proven by | Status |
| --- | --- | --- | --- |
| 7.1 | Contracts for every rule | all kept on the real project | ✅ |
| 7.2 | Valid fixture | accepted | ✅ |
| 7.3 | Framework-in-domain fixture | **rejected**, ARCH-001 | ✅ |
| 7.4 | Adapter-to-adapter fixture | **rejected**, ARCH-004 | ✅ |
| 7.5 | Contracts match canonical policy | drift test | ✅ |
| 7.6 | Meta-check: remove a violation, tests must fail | manual, recorded in evidence | ✅ |

**Gate:** AC-012 and the whole point of Phase 7 — a rule that has never failed is
a rule nobody has verified.

## Phase 8 — Java reference

| # | Task | Proven by | Status |
| --- | --- | --- | --- |
| 8.1 | Seven-module Maven build | `mvnw verify` | ⏳ CI |
| 8.2 | Domain as records and sealed types | ArchUnit | ⏳ CI |
| 8.3 | Ports and use case | unit tests | ⏳ CI |
| 8.4 | Adapters + contract suite | contract tests | ⏳ CI |
| 8.5 | ArchUnit rules | architecture tests | ⏳ CI |
| 8.6 | Java negative fixtures | **rejected** | ⏳ CI |

**⏳ CI** means the code is written but was not executed in the authoring
environment, which has no JDK. This is recorded as `NOT_EXECUTED` in
[`evidence.md`](evidence.md) rather than claimed as passing — Constitution
Article 7.

## Phase 9 — Closure

| # | Task | Status |
| --- | --- | --- |
| 9.1 | Evidence recorded with real results | ✅ |
| 9.2 | Traceability resolves | ✅ |
| 9.3 | Specification moved to RELEASED | ✅ |
