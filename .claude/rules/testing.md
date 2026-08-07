<!-- GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: governance/policies/
     Regenerate with: make generate-agent-rules
     Policy checksum: sha256:0357a6ebe4ab8a4e3a4f6d22d43e091de336ef57c1e32c34c9d43b0a4c870768
-->

# Testing rules

Tests are organised by what they prove, not by folder habit. Domain tests are fast and pure. Application tests use fakes for outbound ports. Contract tests prove every implementation of a port behaves identically. Architecture tests prove the structure itself.

## Levels

- **Domain tests** — fast, pure, no framework, no database, no network. Focus: invariants, value object equality, state transitions, domain events.
- **Application tests** — fakes for outbound ports, no real infrastructure. Focus: use case orchestration, success and failure paths, idempotency, authorization.
- **Port contract tests** — one shared contract suite executed against every implementation. Focus: in-memory and persistence adapters must satisfy the same contract.
- **Adapter and integration tests** — real serialization, real mapping, real storage where it matters. Focus: serialization, mapping, error translation, persistence.
- **Architecture tests** — deterministic, blocking, run on every pull request. Focus: dependency direction, isolation, cycles, forbidden frameworks, naming, composition.
- **End-to-end tests** — few, representative, stable, no unnecessary external dependency. Focus: the whole slice from inbound adapter to outbound adapter.

## Coverage

- `domain_and_application`: line ≥ 95%, branch ≥ 90% (blocking)
- `repository_overall`: line ≥ 85%, branch ≥ 75% (blocking)

Coverage is a floor, not a goal. A covered line is not a tested behaviour.
Lowering a threshold requires an ADR and a CODEOWNERS approval.

## Mutation testing

Mutation testing is valuable but slow. Keeping it out of the pull request critical path preserves fast feedback without losing the signal.
Java: pitest. Python: mutmut.
Runs as a separate-job.

## Forbidden

- **TEST-001** (blocker) — A test must not be skipped, ignored or disabled without a linked issue and a written reason.
- **TEST-002** (blocker) — Architecture tests must never be suppressed to make a change pass.
- **TEST-003** (medium) — Assertions must be specific. A test that only asserts "no exception" proves almost nothing.
- **TEST-004** (high) — Tests must not depend on execution order or on wall-clock time.
- **TEST-005** (blocker) — Negative architecture fixtures must be asserted as rejected, never as accepted.

## Negative fixtures

Showing valid code proves nothing about enforcement. Each control ships with a deliberately invalid fixture and a test asserting the control rejects it.

- `architecture-fixtures/java-valid` → expected **accepted**
- `architecture-fixtures/java-invalid-domain-framework-import` → expected **rejected** (violates ARCH-001)
- `architecture-fixtures/java-invalid-adapter-dependency` → expected **rejected** (violates ARCH-004)
- `architecture-fixtures/python-valid` → expected **accepted**
- `architecture-fixtures/python-invalid-domain-framework-import` → expected **rejected** (violates ARCH-001)
- `architecture-fixtures/python-invalid-adapter-dependency` → expected **rejected** (violates ARCH-004)
