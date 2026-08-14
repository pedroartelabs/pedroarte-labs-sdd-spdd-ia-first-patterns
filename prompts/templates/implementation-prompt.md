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

# Implementation prompt — {title}

## Requirements

Implement {SPEC-ID}, acceptance criteria {list}.

The specification is at `specs/{SPEC-ID}/spec.md`. Read it before writing code.

## Entities

{Copy from the specification's domain model section.}

## Approach

Build inside-out: domain first, then ports, then use case, then adapters, then
bootstrap. Each phase ends with passing tests at that level before moving to the
next.

1. Domain value objects and aggregate with invariants
2. Ports as protocols/interfaces
3. Use case with hand-written fakes
4. Outbound adapters with contract tests
5. Inbound adapter with integration tests
6. Composition root with end-to-end tests
7. Architecture proofs

## Structure

```
src/{context}/domain/         — aggregates, value objects, events, errors
src/{context}/application/    — ports, use cases, application errors
src/{context}/adapters/       — inbound and outbound adapters
src/{context}/bootstrap/      — composition root
tests/                        — organised by test level
```

## Operations

After each phase:

```bash
python -m pytest tests/ -v --tb=short
python -m mypy src/ tests/ --strict
python -m ruff check src/ tests/
```

After all phases:

```bash
python -m pytest tests/ --cov={context} --cov-report=term-missing --cov-branch
lint-imports
```

## Norms

{Copy from the REASONS canvas or the specification.}

## Safeguards

{Copy the mandatory safeguards from ai-first-policy.yaml.}
