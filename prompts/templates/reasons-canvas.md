---
prompt_id: "PROMPT-YYYY-NNN"
spec_id: "SPEC-YYYY-NNN"
version: "1.0.0"
status: DRAFT
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
approved_by: "pending"
language: ""
bounded_context: ""
change_budget: []
---

# SPDD prompt — {title}

## Requirements

**Specification:** {SPEC-ID}
**Acceptance criteria in scope:** {list}
**Constraints:** {from the specification}

## Entities

**Aggregates:** {list with brief role}
**Value objects:** {list}
**Domain events:** {list}
**Inbound ports:** {list}
**Outbound ports:** {list}

## Approach

**Layer order:** domain → application → adapters → bootstrap (inside-out)
**Strategy:** {incremental, one test level at a time}
**Key decisions:** {link to ADRs}

## Structure

**Files to create or modify:**

```
path/to/file.py   — purpose
```

**Module boundaries:** {which layer each file belongs to}

## Operations

**Build and test:**

```bash
command to run tests
```

**Verification:**

```bash
command to check architecture
command to check coverage
```

**Evidence to collect:** {which EVIDENCE-NNN entries}

## Norms

- Follow the project's naming conventions
- Types are explicit; no bare `Any`
- Errors carry machine-readable codes
- No framework imports in domain or application
- {additional project-specific norms}

## Safeguards

- Do not modify files outside the declared scope
- Do not move domain logic into adapters
- Do not introduce a framework into the domain
- Do not disable or skip tests
- Do not weaken quality gates
- Do not suppress lint or type rules without a written justification
- Do not run destructive commands
- Stop on critical ambiguity instead of guessing
- Present evidence before declaring completion
