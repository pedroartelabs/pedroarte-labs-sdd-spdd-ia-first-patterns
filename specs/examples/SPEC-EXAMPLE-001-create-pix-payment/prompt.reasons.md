---
prompt_id: PROMPT-EXAMPLE-001
spec_id: SPEC-EXAMPLE-001
version: 1.1.0
status: APPROVED
model_agnostic: true
target_agent: coding-agent
created_at: 2026-08-06
approved_by: pedroartelabs
languages:
  - java
  - python
change_log:
  - version: 1.0.0
    date: 2026-08-06
    change: Initial prompt derived from the approved specification.
  - version: 1.1.0
    date: 2026-08-06
    change: >-
      Added the finite-amount invariant (INV-004) and the timezone-preservation
      requirement after clarifications CQ-003 and CQ-005 resolved.
---

# PROMPT-EXAMPLE-001 — Implement Create PIX Payment

Structured prompt following the REASONS model. Derived from
[`spec.md`](spec.md); it does not replace it. Where this prompt and the
specification disagree, the specification wins and this prompt is the thing that
must be corrected (Constitution Article 8).

---

## R — Requirements

**Problem.** A bounded context must accept a request to send money to a PIX key
and record that intent durably, exactly once per logical request.

**Objective.** Implement `CreatePixPaymentUseCase` in both the Java and Python
references, with the same functional intent, each written idiomatically for its
language.

**Acceptance criteria.** `AC-001` through `AC-012` in the specification. Every
one must be covered by an automated test.

**Definition of Done**

- Both references implement the use case.
- All acceptance criteria are covered by tests.
- Architecture gates pass and the negative fixtures are rejected.
- Coverage ≥ 95% line on domain and application.
- Evidence records the exact commands run and their real results.
- Traceability resolves.

**Out of scope.** Settlement, real integrations, authentication, authorisation,
rate limiting, fraud checks, currency conversion, and inbound ports for confirm
or cancel.

---

## E — Entities

**Aggregate root:** `Payment` — the consistency boundary. Owns every rule about
what a payment may be and how it may change.

**Value objects**

- `PaymentId` — validated by shape. The domain must **not** import a UUID
  library; identity generation belongs to a port.
- `Money` — exact amount plus currency. Never constructed from a float.
- `PixKey` — value plus type, validated against the declared type, able to mask
  itself for logs.

**Enumerations:** `PaymentStatus` (`PENDING`, `CONFIRMED`, `FAILED`,
`CANCELLED`), `PixKeyType` (`EMAIL`, `PHONE`, `TAX_ID`, `RANDOM`).

**Domain event:** `PaymentCreated` — primitives only, PIX key **masked**.

**Invariants:** `INV-001` … `INV-011` from the specification. Note `INV-004`
specifically: an amount must be finite, because Infinity is greater than zero
and would otherwise pass a naive positivity check.

**Commands and results:** `CreatePixPaymentCommand`,
`CreatePixPaymentResult` — primitives, so an inbound adapter can build one
without importing domain types.

**Contracts:** the four outbound ports named in the specification.

---

## A — Approach

**Chosen solution.** Hexagonal, package by bounded context first. The aggregate
enforces the rules; a thin use case orchestrates; adapters translate technology.
Clock and identity are injected so the aggregate is a pure function of its
inputs.

**Alternatives rejected**

- *Anaemic entity plus a fat service.* Would satisfy every architecture test
  while abandoning the substance: the layering would be correct and the rules
  would still live outside the domain.
- *Pydantic / JPA models as domain entities.* Saves a mapping file, costs the
  domain its independence — a required no-argument constructor, lazy-loading
  proxies, identity tied to a sequence, and an open session as a precondition
  for using a business object.
- *Reading the clock inside the aggregate.* Would force every time-dependent
  test to freeze global state or accept flakiness.
- *Transactional outbox for event publication.* Correct for production, and
  significant machinery that would obscure the ports-and-adapters lesson. Not
  chosen; the limitation is documented rather than hidden.

**Trade-offs accepted.** Publish-after-save can lose a notification if the
broker fails after a successful write. Recorded as a known limitation, pinned by
a test that asserts the actual behaviour rather than a hoped-for one.

**Risks.** See the specification's risk table. The highest is that architecture
rules pass without ever being *able* to fail; mitigated by negative fixtures.

**Incremental strategy.** Domain first and fully tested, then ports, then the
use case against fakes, then adapters, then composition, then end-to-end.

---

## S — Structure

**Bounded context:** `payment`.

**Layers and allowed dependencies**

```
domain            -> nothing
application       -> domain
adapters.inbound  -> domain, application
adapters.outbound -> domain, application
bootstrap         -> all of the above
```

**Forbidden dependencies**

- domain → application, adapters, bootstrap
- application → adapters, bootstrap
- inbound adapter ↔ outbound adapter
- anything → bootstrap

**Files that may be created or modified**

- `examples/python-hexagonal/src/payment/**`
- `examples/python-hexagonal/tests/**`
- `examples/java-hexagonal/payment-*/src/**`
- `architecture-fixtures/**` when adding a negative proof

**Files that must NOT be modified**

- `governance/policies/**` — the canonical rules
- `CLAUDE.md`, `AGENTS.md`, `.claude/rules/**`, `.cursor/rules/**`,
  `.github/copilot-instructions.md` — generated
- `.github/workflows/**` — quality gates
- `schemas/**`
- Any coverage threshold or architecture rule

---

## O — Operations

1. **Domain errors.** Define the hierarchy. → No test yet.
2. **`Money`.** Implement with `INV-001`–`INV-004`. → Unit tests including
   float rejection, NaN, Infinity, precision, currency. Property tests for
   commutativity and exact round-tripping.
3. **`PixKey`.** Implement `INV-005` plus masking. → Unit tests per key type,
   valid and malformed, plus masking assertions.
4. **`Payment` and `PaymentId`.** Implement `INV-006`–`INV-011`, event
   recording, identity-based equality. → Unit tests for lifecycle and events.
5. **Outbound ports.** Declare all four. → No test; they are interfaces.
6. **Inbound port.** Declare the use case, command and result.
7. **Use case.** Implement the main flow. → Tests with fakes: happy path,
   idempotent replay, each validation failure, each infrastructure failure.
8. **In-memory repository.** → Contract suite.
9. **Relational adapter.** Persistence model separate from the aggregate;
   translate driver exceptions; preserve timezone. → Same contract suite, plus
   integration tests for error translation and the unique constraint.
10. **System adapters.** Clock, identifier generator, event publisher.
11. **REST adapter.** DTOs, status codes, error mapping. → No business rule here.
12. **Composition root.** Wire everything; nothing imports it.
13. **Architecture contracts.** Write them, then **prove they can fail** using
    the negative fixtures.
14. **End-to-end.** Through the real composition root.

**Commands to run**

```bash
# Python
cd examples/python-hexagonal
pytest -q
lint-imports --config .importlinter
mypy
ruff check . && ruff format --check .

# Java
cd examples/java-hexagonal
./mvnw -q verify

# Everything
make verify
```

**Expected evidence.** For each command: the exact invocation and its real
result. `NOT_EXECUTED` with a reason is acceptable; an unearned `PASS` is not.

---

## N — Norms

- **Naming.** Ports carry no technology name. Inbound ports end in `UseCase`.
  Outbound ports name a responsibility: `Repository`, `Publisher`, `Clock`,
  `IdGenerator`.
- **Errors.** Domain errors are business failures; technical failures are
  translated at the adapter boundary. Error responses never leak driver
  messages, hostnames or credentials.
- **Logging.** PIX keys are masked wherever rendered. No credential, token or
  full identifier reaches a log.
- **Typing.** Python: explicit annotations on public APIs, `Protocol` ports,
  no blanket `Any`, no unexplained `type: ignore`. Java: records for value
  objects, sealed hierarchies where the set of cases is closed.
- **Tests.** Prefer hand-written fakes over mocks. Assert outcomes, not calls.
  One shared contract suite per port. Every test name states the behaviour.
- **Documentation.** Comments explain *why*, never *what*. Every non-obvious
  trade-off is written down at the point where it was made.
- **Compatibility.** Java on current and previous LTS. Python 3.11–3.14.

---

## S — Safeguards

**Non-negotiable**

- Do not modify files outside the declared scope.
- Do not move domain logic into an adapter.
- Do not introduce a framework into the domain.
- Do not disable, skip or delete a test.
- Do not weaken a quality gate or lower a coverage threshold.
- Do not suppress a lint or type rule without a written justification — and
  prefer fixing the code over justifying the suppression.
- Do not run a destructive command.
- Do not use real personal, banking or credential data.
- Do not present a command as passing unless it ran and passed.

**Stop conditions.** Halt and ask when:

- The specification and an acceptance criterion contradict each other.
- An invariant cannot be enforced without violating an architecture rule.
- A gate fails and the only apparent fix is to change the gate.
- A change would need to touch a forbidden file.

**Change budget.** Roughly 60 source and test files across both references. A
significantly larger diff means the scope drifted — stop and re-read.

**Tools permitted:** read, write and edit within scope; run tests, linters, type
checkers and architecture gates; run git status, diff and log.

**Tools forbidden:** force push, history rewrite, branch or release deletion,
dependency installation outside the declared manifests, network calls to any
real payment service.

**Rollback plan.** Every step is independently revertable. The reference modules
have no consumers, so removing them is sufficient.

**Human approval required for:** any policy change, any new architecture rule,
any exception, and any deviation from this prompt's Structure section.

**Final report format**

```
Implemented: <what>
Commands run:
  <command> -> PASS | FAIL | NOT_EXECUTED (reason)
Acceptance criteria covered: AC-xxx ...
Not covered: <list with reasons>
Files changed: <count>
Deviations from this prompt: <list, or "none">
Known limitations: <list>
```
