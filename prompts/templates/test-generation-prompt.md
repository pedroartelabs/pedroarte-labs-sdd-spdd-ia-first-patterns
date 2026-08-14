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

# Test generation prompt — {title}

## Requirements

Write tests for {SPEC-ID}, acceptance criteria {list}.

**Test level:** {domain / application / contract / integration / architecture / e2e}
**Target:** {the module or class under test}

## Entities

**Under test:** {list}
**Collaborators (fakes):** {list}

## Approach

- Each test proves one behaviour
- Name tests after what they prove, not what they call
- Use hand-written fakes, not mocks
- Property tests where a law exists (commutativity, round-trip, idempotency)

## Structure

```
tests/{level}/test_{name}.py
tests/support.py              — shared fakes and builders
```

## Operations

```bash
python -m pytest tests/{level}/test_{name}.py -v --tb=short
python -m pytest tests/ --cov={context} --cov-report=term-missing
```

## Norms

- Assertions must be specific — no bare `assert result` or `assert not exception`
- Tests must not depend on execution order or wall-clock time
- One concept per test; multiple assertions are fine if they test one thing

## Safeguards

- Do not skip or disable existing tests
- Do not weaken assertions to make a test pass
- Do not import frameworks in domain-level tests
