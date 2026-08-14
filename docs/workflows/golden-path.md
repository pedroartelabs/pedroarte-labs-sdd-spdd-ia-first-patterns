# Golden Path

The standard workflow from idea to release.

## Steps

1. **Intake** — Problem identified, roughly scoped
2. **Draft specification** — `/sdd-init` then `/sdd-specify`
3. **Clarification** — `/sdd-clarify` to surface ambiguities
4. **Specification review** — Human reviews, resolves open questions
5. **Approval** — All gate checks pass, status → APPROVED
6. **Architecture plan** — `/sdd-plan` creates architecture.md and tasks.md
7. **Task decomposition** — Phased, inside-out, individually verifiable
8. **SPDD prompt generation** — `/spdd-generate` creates the REASONS prompt
9. **Implementation** — `/implement-python-feature` or `/implement-java-feature`
10. **Automated verification** — Tests, linting, type checking, architecture
11. **Architecture review** — `/architecture-check`
12. **Human review** — Pull request review by a human
13. **Evidence collection** — Record actual commands and results
14. **Release** — Status → RELEASED
15. **Specification closure** — `/close-spec`

## Key principle

No production code without an approved specification. The specification is not
a document to file and forget — it is the source of intent, scope, and
acceptance criteria throughout the lifecycle.
