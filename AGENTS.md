<!-- GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: governance/policies/
     Regenerate with: make generate-agent-rules
     Policy checksum: sha256:0357a6ebe4ab8a4e3a4f6d22d43e091de336ef57c1e32c34c9d43b0a4c870768
-->

# AGENTS.md

Tool-agnostic instructions for any coding agent operating in this repository.
Claude Code reads `CLAUDE.md`; other agents read this file. Both are generated
from `governance/policies/`.

## Ground rules

1. **No production code without an approved specification.** Production paths are
   `examples/java-hexagonal/**/src/main/**`, `examples/python-hexagonal/src/**`, `tools/**/src/**`.
2. **The prompt derives from the specification**, never replaces it.
3. **Prompts are versioned artifacts** with an id, a linked spec, constraints,
   stop conditions and a change log.
4. **Dependencies point inward.** Dependencies point inward. The domain is the centre and knows nothing about frameworks, transports or storage. Application orchestrates use cases behind ports. Adapters implement ports and translate technology. Bootstrap is the only place allowed to wire everything together.
5. **Architecture is executable.** Every important rule has an automated check.
6. **AI does not approve alone.** Deterministic architecture and quality gates are the blocking checks. An AI review adds a probabilistic second opinion; it must never be the only thing standing between a change and main.
7. **Evidence before completion.** Record the command and its real result.

## Structured prompts: the REASONS model

- **R — Requirements**: which problem is solved; for whom; expected behaviour; definition of done; acceptance criteria; out of scope
- **E — Entities**: entities, aggregates, value objects; commands and events; states and invariants; relationships; ubiquitous language
- **A — Approach**: implementation strategy; alternatives considered; trade-offs; technical decisions; risks; incremental strategy
- **S — Structure**: bounded context; modules and layers; ports and adapters; allowed dependencies; files that may be modified; files that must not be modified
- **O — Operations**: small steps in order; verifiable tasks; tests per step; validations; commands to execute
- **N — Norms**: code standards and conventions; observability; error handling; security practices; test style; documentation; compatibility and performance
- **S — Safeguards**: domain invariants; forbidden dependencies; security boundaries; minimum quality criteria; forbidden destructive actions; stop conditions; rollback; human approval requirements

## Architecture contract

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

### Rules

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

## Safeguards every agent must honour

- do not modify files outside the declared scope
- do not move domain logic into adapters
- do not introduce a framework into the domain
- do not disable or skip tests
- do not weaken quality gates
- do not suppress lint or type rules without a written justification
- do not run destructive commands
- stop on critical ambiguity instead of guessing
- present evidence before declaring completion

## Roles an agent may take

Allowed: specification analyst, planner, assistant architect, implementer, test generator, reviewer, architecture guardian, documenter, tool operator.

Forbidden: sole approver of a merge, authority on whether a quality gate may be weakened, source of truth about whether a command actually ran, author of secrets or credentials.

## Verification commands

```bash
make verify-architecture
make verify-java
make verify-python
make verify
```
