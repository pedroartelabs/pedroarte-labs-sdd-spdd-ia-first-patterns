<!-- GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: governance/policies/
     Regenerate with: make generate-agent-rules
     Policy checksum: sha256:0357a6ebe4ab8a4e3a4f6d22d43e091de336ef57c1e32c34c9d43b0a4c870768
-->

# Specification rules

An explicit, versioned, reviewable and testable specification drives planning, implementation, tests and validation. The specification is not a disposable document: it remains the source of intent, scope, rules, acceptance criteria, constraints, risks, decisions and traceability.

## Identifier

Pattern: `^SPEC-(?:[0-9]{4}-[0-9]{3}|EXAMPLE-[0-9]{3})$` — for example
`SPEC-2026-001`, `SPEC-EXAMPLE-001`.

## Lifecycle

- **DRAFT** — Being written. No production code may be produced yet.
- **IN_REVIEW** — Under human review; clarifications are being collected.
- **APPROVED** — Reviewed and accepted. Architecture and tasks exist.
- **IMPLEMENTING** — Implementation in progress against a versioned SPDD prompt.
- **VERIFIED** — All acceptance criteria proven by recorded evidence.
- **RELEASED** — Shipped and traceable end to end.
- **REJECTED** — Declined. Terminal.
- **SUPERSEDED** — Replaced by another specification. Terminal.
- **DEPRECATED** — Still historically true but no longer the target behaviour.
- **CANCELLED** — Abandoned before completion. Terminal.
- **HOTFIX** — Emergency path; requires retroactive specification within the SLA.

## Allowed transitions

- `DRAFT` → `IN_REVIEW`, `CANCELLED`, `REJECTED`
- `IN_REVIEW` → `DRAFT`, `APPROVED`, `REJECTED`, `CANCELLED`
- `APPROVED` → `IMPLEMENTING`, `SUPERSEDED`, `CANCELLED`, `DEPRECATED`
- `IMPLEMENTING` → `VERIFIED`, `APPROVED`, `CANCELLED`
- `VERIFIED` → `RELEASED`, `IMPLEMENTING`
- `RELEASED` → `SUPERSEDED`, `DEPRECATED`
- `HOTFIX` → `VERIFIED`, `RELEASED`, `CANCELLED`
- `REJECTED` → *(terminal)*
- `SUPERSEDED` → *(terminal)*
- `CANCELLED` → *(terminal)*
- `DEPRECATED` → `SUPERSEDED`

## Entry requirements

### Entering `IN_REVIEW`

- **SPEC-GATE-001** — fails when the problem statement section is empty
- **SPEC-GATE-002** — fails when the expected outcome / definition of done is empty

### Entering `APPROVED`

- **SPEC-GATE-010** — fails when acceptance criteria are missing
- **SPEC-GATE-011** — fails when acceptance criteria are not written in Given/When/Then form
- **SPEC-GATE-012** — fails when outbound ports are undefined
- **SPEC-GATE-013** — fails when the inbound port is undefined
- **SPEC-GATE-014** — fails when test strategy is incomplete
- **SPEC-GATE-015** — fails when architecture.md is missing
- **SPEC-GATE-016** — fails when blocking open questions are still unresolved
- **SPEC-GATE-017** — fails when the ubiquitous language section is empty

### Entering `IMPLEMENTING`

- **SPEC-GATE-020** — fails when no versioned SPDD prompt (prompt.reasons.md) is linked
- **SPEC-GATE-021** — fails when tasks.md is missing

### Entering `VERIFIED`

- **SPEC-GATE-030** — fails when evidence.md is missing or records no executed command
- **SPEC-GATE-031** — fails when not every acceptance criterion is covered by evidence

### Entering `RELEASED`

- **SPEC-GATE-040** — fails when traceability.yaml is missing
- **SPEC-GATE-041** — fails when traceability.yaml references files or tests that do not exist

## Required frontmatter

`id`, `title`, `status`, `type`, `owner`, `created_at`, `updated_at`, `languages`, `bounded_context`, `risk_level`.

Optional: `related_adrs`, `related_issues`, `prompt_artifacts`, `supersedes`, `superseded_by`.

## Pull request linkage

A pull request touching production paths must reference an approved
`SPEC-ID` matching `SPEC-(?:[0-9]{4}-[0-9]{3}|EXAMPLE-[0-9]{3})`, and once the
specification is `IMPLEMENTING` it must also reference a `PROMPT-ID` matching
`PROMPT-(?:[0-9]{4}-[0-9]{3}|EXAMPLE-[0-9]{3})`.
