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

# Migration prompt — {title}

## Requirements

Migrate {what} from {current state} to {target state}.

**Specification:** {SPEC-ID}
**Rollback plan:** {how to reverse if it goes wrong}

## Entities

**Moving:** {list}
**Staying:** {list}

## Approach

1. Create the target structure alongside the current one
2. Migrate one component at a time with tests passing after each step
3. Remove the old structure only after all tests pass on the new one
4. Run architecture checks to confirm no regressions

## Structure

**New files:**

```
path/to/new  — purpose
```

**Files to remove (after migration):**

```
path/to/old  — why it is no longer needed
```

## Operations

```bash
# After each migration step
python -m pytest tests/ -v
lint-imports
python -m mypy src/ tests/ --strict
```

## Norms

- Never have a commit where tests fail
- Never remove the old code before the new code passes all tests
- Document the migration in the ADR

## Safeguards

- Do not migrate and refactor in the same step
- Do not change behaviour during migration
- Stop if removing old code breaks anything — something still depends on it
