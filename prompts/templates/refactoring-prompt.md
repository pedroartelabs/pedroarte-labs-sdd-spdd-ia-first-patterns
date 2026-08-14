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

# Refactoring prompt — {title}

## Requirements

Refactor {what} to achieve {why}. No behaviour change.

**Specification:** {SPEC-ID}
**Constraint:** all existing tests must pass before and after, with no modification.

## Entities

**Affected:** {list of types being restructured}
**Unchanged:** {list of types that must not be touched}

## Approach

1. Run the full test suite — record the baseline
2. Make the structural change
3. Run the full test suite — confirm identical results
4. Run architecture checks — confirm no new violations

## Structure

**Files to modify:**

```
path/to/file  — what changes
```

**Files that must NOT change:** {list}

## Operations

```bash
# Before
python -m pytest tests/ -v
# Refactor
# After
python -m pytest tests/ -v
lint-imports
python -m mypy src/ tests/ --strict
```

## Norms

- No behaviour change. If a test needs updating, the refactoring changed behaviour.
- No new dependencies.
- No layer violations.

## Safeguards

- Do not modify test assertions
- Do not add or remove public API surface
- Do not introduce a framework into the domain
- Stop if any test fails after the change — the refactoring is wrong
