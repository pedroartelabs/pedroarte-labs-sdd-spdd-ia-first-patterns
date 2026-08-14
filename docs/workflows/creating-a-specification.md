# Creating a specification

## Quick start

```bash
make spec-new NAME="create refund payment" TYPE=feature
```

Or use the Claude Code skill:

```
/sdd-init
```

## What happens

1. A directory is created under `specs/` with the next available SPEC-ID
2. `spec.md` is populated from the template with frontmatter
3. `clarifications.md` is created for the clarification log

## Filling in the specification

Use `/sdd-specify` to complete the specification interactively, or fill in the
template manually:

1. **Problem statement** — What is the problem, who has it, why does it matter?
2. **Expected outcome** — What is true when this work is done?
3. **Acceptance criteria** — Given/When/Then form, testable
4. **Domain model** — Aggregates, value objects, events
5. **Invariants** — Business rules the domain enforces
6. **Ports** — Inbound and outbound, with responsibilities
7. **Use case flow** — Happy path first, then failure paths
8. **Risks** — What could go wrong, how to mitigate
9. **Test strategy** — Which test levels, what each proves
10. **Ubiquitous language** — Terms and their definitions

## Moving to IN_REVIEW

The specification must have a problem statement and expected outcome before
it can be reviewed (SPEC-GATE-001, SPEC-GATE-002).
