---
name: create-adr
description: Create an Architecture Decision Record in the standard format
user_invocable: true
---

# /create-adr

Create a new ADR in `docs/decisions/`.

## Steps

1. Determine the next ADR number from existing files
2. Ask for the decision title and context
3. Create `docs/decisions/ADR-{NNNN}-{kebab-case-title}.md` with:

```markdown
# ADR-{NNNN}: {title}

## Status

Proposed

## Context

{What is the issue that motivates this decision?}

## Decision

{What is the change that we're proposing and/or doing?}

## Consequences

### Positive

-

### Negative

-

### Neutral

-

## Compliance

- **Architecture rules affected:** {list of ARCH-NNN}
- **Fitness functions:** {how the decision is enforced}
- **Review date:** {YYYY-MM-DD, max 90 days from creation}
```

4. Link the ADR from the relevant specification

## Rules

- Every ADR must list affected architecture rules
- Every ADR must have a review date (max 90 days)
- Status values: Proposed, Accepted, Deprecated, Superseded
- Never delete an ADR — supersede it with a new one
