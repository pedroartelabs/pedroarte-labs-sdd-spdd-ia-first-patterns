---
name: spdd-generate
description: Generate a SPDD REASONS prompt from an approved specification
user_invocable: true
---

# /spdd-generate

Generate a structured SPDD prompt using the REASONS model.

## Steps

1. Read the specification, architecture plan, and task plan
2. Generate a PROMPT-ID matching the SPEC-ID pattern
3. Create `prompt.reasons.md` with all seven REASONS sections:
   - **Requirements**: SPEC-ID, acceptance criteria, constraints
   - **Entities**: aggregates, value objects, events, ports
   - **Approach**: inside-out, incremental, key decisions
   - **Structure**: file paths, module boundaries
   - **Operations**: build/test commands, verification, evidence collection
   - **Norms**: coding standards, naming, error handling
   - **Safeguards**: mandatory safeguards from ai-first-policy.yaml
4. Set status=DRAFT, version=1.0.0
5. Add the change budget (list of files the implementation may touch)
6. Link the prompt in the specification's frontmatter

## Rules

- Every REASONS section must have content — none may be empty
- The safeguards section must include all mandatory safeguards from policy
- The change budget must be explicit — no "and related files"
- Status is DRAFT until a human reviews and approves it
