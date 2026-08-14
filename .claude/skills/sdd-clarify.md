---
name: sdd-clarify
description: Identify and record ambiguities in a specification
user_invocable: true
---

# /sdd-clarify

Review a specification for ambiguities and record them in the clarification log.

## Steps

1. Read the specification at the provided path
2. Read the existing clarification log
3. For each ambiguity found:
   a. Assign the next CQ-NNN identifier
   b. Write a clear question
   c. Explain why it matters (what goes wrong if answered incorrectly)
   d. Mark as OPEN with blocking=yes/no
4. Check if any OPEN blocking questions prevent APPROVED status
5. Report findings

## What to look for

- Terms used without definition
- Acceptance criteria with multiple interpretations
- Undeclared edge cases (nulls, empty strings, boundary values)
- Implicit assumptions about order, timing, or concurrency
- Missing failure modes
- Ambiguous ownership of validation (adapter vs domain)

## Rules

- Every clarification must explain why it matters, not just what is unclear
- Blocking questions must be resolved before APPROVED
- Never resolve a question yourself — present options and let the human decide
