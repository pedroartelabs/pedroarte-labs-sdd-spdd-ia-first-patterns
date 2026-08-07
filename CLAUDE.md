<!-- GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: governance/policies/
     Regenerate with: make generate-agent-rules
     Policy checksum: sha256:0357a6ebe4ab8a4e3a4f6d22d43e091de336ef57c1e32c34c9d43b0a4c870768
-->

# CLAUDE.md

## Mission

This repository is a public reference for **AI-First software delivery under
governance**: SDD, SPDD, Hexagonal Architecture, architecture tests, Claude Code
Skills, and deterministic quality gates for Java and Python.

In an AI-First process, artificial intelligence is not merely a code generator. It is a governed participant in the engineering cycle, working from specifications, structured prompts, architectural policy and automated validation.

AI-First is **not** Vibe coding, Unrestricted code generation, Merging on a model's opinion.

## Canonical source of rules

Every rule below is projected from `governance/policies/`. That directory is the
single source of truth.

- Do **not** edit `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`,
  `.github/copilot-instructions.md` or `.cursor/rules/*.mdc` by hand.
- Change the YAML policy, then run `make generate-agent-rules`.
- `make check-rule-drift` fails the build when a generated file was hand-edited
  or when a policy changed without regeneration.

## Core commands

```bash
make doctor                 # verify the local toolchain
make setup                  # install dev dependencies
make generate-agent-rules   # regenerate agent instruction files from policy
make check-rule-drift       # fail if generated files drifted from policy
make spec-new NAME="..." TYPE=feature
make validate-specs         # SDD lifecycle and schema validation
make validate-prompts       # SPDD REASONS validation
make validate-traceability  # requirement -> code -> test -> evidence
make verify-architecture    # ArchUnit + Import Linter + negative fixtures
make verify-java
make verify-python
make verify-security
make verify-docs
make verify                 # everything that must pass before a pull request
```

## Mandatory workflow

No production code without an approved specification. The golden path:

1. Intake
2. Draft specification — `/sdd-init then /sdd-specify`
3. Clarification — `/sdd-clarify`
4. Specification review
5. Approval
6. Architecture plan — `/sdd-plan`
7. Task decomposition — `/sdd-plan`
8. SPDD prompt generation — `/spdd-generate`
9. Incremental implementation — `/implement-java-feature or /implement-python-feature`
10. Automated verification
11. Architecture review — `/architecture-check`
12. Human review
13. Evidence collection
14. Release
15. Specification closure — `/close-spec`

Skills implement these steps. Prefer `/sdd-specify`, `/sdd-clarify`, `/sdd-plan`,
`/spdd-generate`, `/implement-java-feature`, `/implement-python-feature`,
`/architecture-check`, `/review-change`, `/create-adr`, `/close-spec` over
improvising the process.

## Architecture rules (non-negotiable)

Dependencies point inward. The domain is the centre and knows nothing about frameworks, transports or storage. Application orchestrates use cases behind ports. Adapters implement ports and translate technology. Bootstrap is the only place allowed to wire everything together.

| Layer | May depend on | Java package | Python module |
| --- | --- | --- | --- |
| `domain` | *(nothing)* | `..domain..` | `payment.domain` |
| `application` | domain | `..application..` | `payment.application` |
| `adapter_inbound` | domain, application | `..adapter.in..` | `payment.adapters.inbound` |
| `adapter_outbound` | domain, application | `..adapter.out..` | `payment.adapters.outbound` |
| `bootstrap` | domain, application, adapter_inbound, adapter_outbound | `..bootstrap..` | `payment.bootstrap` |

- `domain` must not depend on `application`, `adapter_inbound`, `adapter_outbound`, `bootstrap` — The domain is the centre; nothing inside it may point outward.
- `application` must not depend on `adapter_inbound`, `adapter_outbound`, `bootstrap` — The application talks to technology only through ports it declares.
- `adapter_inbound` must not depend on `adapter_outbound`, `bootstrap` — Adapters are siblings; they must never call each other directly.
- `adapter_outbound` must not depend on `adapter_inbound`, `bootstrap` — Adapters are siblings; they must never call each other directly.

- **ARCH-001** (blocker) — Domain must not depend on frameworks. Enforced by: archunit, import-linter, post-edit-hook, architecture-gate.
- **ARCH-002** (blocker) — Domain must not depend on application, adapters or bootstrap. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-003** (blocker) — Application must not depend on adapters. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-004** (blocker) — Inbound adapters must not depend on outbound adapters. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-005** (blocker) — Outbound adapters must not depend on inbound adapters. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-006** (blocker) — There must be no dependency cycles between packages or modules. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-007** (blocker) — Only bootstrap may perform composition. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-008** (high) — Ports must not carry technology names. Enforced by: archunit, architecture-gate.
- **ARCH-009** (blocker) — Domain entities must not be ORM entities and must carry no technical annotations. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-010** (high) — Persistence models live in the outbound persistence adapter, transport DTOs live in the inbound adapter. Enforced by: archunit, architecture-gate.
- **ARCH-011** (high) — Technical exceptions must be translated at the adapter boundary. Enforced by: review, ai-review.
- **ARCH-012** (high) — Time, randomness and identifier generation must be abstracted behind outbound ports when they affect business rules. Enforced by: archunit, import-linter, review.
- **ARCH-013** (blocker) — Every deliberate deviation requires an ADR with owner, justification and review date. Enforced by: architecture-exceptions, review, validate-repository.

### Forbidden imports in the domain

- **Java:** `org.springframework`, `jakarta.persistence`, `jakarta.servlet`, `javax.persistence`, `org.hibernate`, `com.fasterxml.jackson`, `org.apache.kafka`, `software.amazon.awssdk`, `java.sql`, `javax.sql`, `java.net.http`, `io.micrometer`, `org.slf4j`
- **Python:** `fastapi`, `flask`, `django`, `starlette`, `sqlalchemy`, `pydantic`, `boto3`, `botocore`, `httpx`, `requests`, `aiohttp`, `kafka`, `confluent_kafka`, `redis`, `psycopg`, `pymongo`

A deliberate deviation requires an ADR with owner, justification and review date
(`governance/architecture-exceptions.md`).

## Definition of Done

A change is done only when all of the following are true and **proven**:

- The specification exists, is approved, and matches what was built.
- The SPDD prompt is versioned and linked to that specification.
- Implementation is incremental and stays inside the declared file scope.
- Unit, contract, integration and architecture tests pass.
- Coverage thresholds hold (domain/application 95% line, repository 85%).
- No quality gate was weakened, no test disabled, no rule suppressed.
- Traceability is updated.
- Security checks pass and no secret was introduced.
- Evidence is recorded: the exact commands run and their real results.

## Evidence discipline

Never report a command as passing unless it actually ran and actually passed.
When something could not be executed, say so explicitly and record it as
`NOT_EXECUTED` with the reason. A confident summary is not evidence.

There are 20 blocking quality gates; see
`docs/reference/quality-gates.md` for the full catalogue.

## Safeguards

- do not modify files outside the declared scope
- do not move domain logic into adapters
- do not introduce a framework into the domain
- do not disable or skip tests
- do not weaken quality gates
- do not suppress lint or type rules without a written justification
- do not run destructive commands
- stop on critical ambiguity instead of guessing
- present evidence before declaring completion

## AI is not the approver

Deterministic architecture and quality gates are the blocking checks. An AI review adds a probabilistic second opinion; it must never be the only thing standing between a change and main.
