# Clarification log — SPEC-EXAMPLE-001

Ambiguities found while reviewing the draft, and how they were resolved.

The point of this log is not bureaucracy. Every entry below is a question that,
left unanswered, would have been silently decided by whoever wrote the code
first — and then discovered much later as "why does it do that?".

**Status legend:** `OPEN` blocks approval · `RESOLVED` decided · `DEFERRED`
explicitly out of scope

---

## CQ-001 — What does "create a payment" actually mean?

**Status:** RESOLVED · **Raised by:** spec-analyst · **Blocking:** yes

**Question.** Does accepting a payment move money, reserve funds, or only record
an intent?

**Why it matters.** It determines whether the aggregate needs a settlement
lifecycle, whether the operation must be transactional across systems, and
whether "failure" means a rejected request or a failed transfer.

**Decision.** Creating a payment records an **intent** and nothing else. No money
moves. The ubiquitous language uses *accept*, never *process* or *send*.

**Consequence.** `PENDING` is the only state a new payment can hold. The other
states exist on the aggregate for lifecycle completeness but no inbound port
exposes them yet.

---

## CQ-002 — Is a duplicate request an error or a replay?

**Status:** RESOLVED · **Raised by:** domain-modeler · **Blocking:** yes

**Question.** When the same idempotency key arrives twice, should the second
call return `409 Conflict` or the original payment?

**Why it matters.** A client retrying after a network timeout does not know
whether the first call succeeded. Returning 409 forces every client to
implement a reconciliation query; returning the original payment makes the retry
trivially safe.

**Decision.** Return the original payment with `already_existed = true`, and
**200** rather than **201** — because nothing was created and a 201 would be a
lie.

**Rejected alternative.** Comparing the replayed request body against the
original and returning 409 on mismatch. Defensible, and it doubles the surface
area of the example for a case the acceptance criteria do not cover. Deferred.

---

## CQ-003 — Which amounts are invalid?

**Status:** RESOLVED · **Raised by:** test-architect · **Blocking:** yes

**Question.** The draft said "the amount must be positive". Does that cover NaN,
Infinity, and sub-cent precision?

**Why it matters.** `Decimal("Infinity") > 0` is **true**. A naive positivity
check accepts it, and the precision check then fails with a `TypeError` instead
of a domain error — a 500 where a 422 belongs.

**Decision.** Four separate invariants, `INV-001` to `INV-004`: positive, minor-unit
precision at most, supported currency, and **finite**. Float is rejected at
construction with an explicit message rather than silently converted.

**Consequence.** Prompt bumped to 1.1.0. `test_rejects_infinity` exists
specifically because this was nearly missed.

---

## CQ-004 — Should the PIX key be validated, and how strictly?

**Status:** RESOLVED · **Raised by:** spec-analyst · **Blocking:** no

**Question.** Full validation including tax-id check digits and phone
normalisation, or format only?

**Decision.** Format only, validated **against the declared type**. Documented
as illustrative in both the value object and the specification.

**Rationale.** Real check-digit validation teaches nothing about hexagonal
boundaries and adds a page of arithmetic to a file whose job is to demonstrate
an invariant. Validating against the declared type, however, does earn its
place: it catches a client that swapped two fields, which is a real bug class.

---

## CQ-005 — Must `created_at` carry a timezone?

**Status:** RESOLVED · **Raised by:** hexagonal-architect · **Blocking:** yes

**Question.** Is a naive local timestamp acceptable?

**Why it matters.** A naive timestamp is ambiguous twice a year under DST and
meaningless once a second region writes to the same store.

**Decision.** `INV-009` — `created_at` must be timezone-aware; the aggregate
rejects a naive value outright.

**Complication found during implementation.** PostgreSQL honours `TIMESTAMPTZ`
and returns an aware value. SQLite has no timezone concept and returns a naive
one. The invariant therefore held in production and broke under the fast test
suite — the worst arrangement possible, because the tests would have been the
thing lying.

**Resolution.** A `UtcDateTime` type decorator in the persistence adapter
normalises on write and reattaches UTC on read. The adapter absorbs the backend
difference; the domain rule is untouched. A contract test asserts timezone
survival on **every** repository implementation, which is how the divergence was
caught in the first place.

---

## CQ-006 — What happens if the event cannot be published?

**Status:** RESOLVED · **Raised by:** hexagonal-architect · **Blocking:** yes

**Question.** Publish before or after saving? What if the second step fails?

**Decision.** Save first, then publish. On publication failure the error
propagates and **the payment remains stored**.

**Rationale.** Publishing first risks announcing a payment that was never stored,
and a consumer cannot un-see an event. Save-then-publish means a broker outage
loses a *notification*, not a *payment* — the strictly better failure.

**Known limitation, stated rather than hidden.** This is not exactly-once
delivery. A production system needs a transactional outbox. That machinery would
obscure the ports-and-adapters lesson, so it is out of scope, documented in the
spec's risk table, and pinned by a test that asserts the real behaviour instead
of a hoped-for one.

---

## CQ-007 — Should `Clock` and `IdGenerator` really be ports?

**Status:** RESOLVED · **Raised by:** java-engineer · **Blocking:** no

**Question.** Two interfaces and two adapters for what is ultimately
`datetime.now()` and `uuid4()`. Is that ceremony?

**Why it was asked.** It is a fair challenge. The repository's own review policy
says an abstraction must be *earned*, and a port introduced for one
implementation that will never have a second is ceremony.

**Decision.** Keep them as ports.

**Rationale.** They pay for themselves immediately and visibly: every use-case
test asserts an **exact** identifier and an **exact** timestamp, with no
patching, no frozen global clock and no mocking library anywhere in the suite.
The cost is three tiny classes. The alternative cost is that every
time-dependent or identity-dependent test becomes either imprecise or fragile.

This is recorded because "why is there a Clock interface?" is the single most
common objection newcomers raise, and the answer belongs somewhere durable.

---

## CQ-008 — Should confirm and cancel be exposed as use cases?

**Status:** DEFERRED · **Raised by:** spec-analyst · **Blocking:** no

**Decision.** The aggregate models the transitions and tests them. No inbound
port exposes them in this specification.

**Rationale.** They add no new architectural concept — the same ports, the same
layering, one more controller method each. Scope is kept to what teaches
something new. Tracked as a future specification.
