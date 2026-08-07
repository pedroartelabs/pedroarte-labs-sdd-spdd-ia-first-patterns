# Architecture exception register

Every deliberate deviation from an architectural rule lives here. Constitution
[Article 9](constitution.md#article-9--exceptions-are-explicit).

## The rules of exceptions

1. **No exception is permanent.** Maximum duration is 90 days. An exception
   without an expiry date is invalid.
2. **Every exception has a named owner.** Not a team, not "TBD" — a person who
   will be asked about it.
3. **Every exception has an ADR.** The register records *that* it exists; the
   ADR records *why*, what was considered, and what it costs.
4. **Every exception has a removal plan.** If nobody can describe how it goes
   away, it is not an exception — it is a decision to change the rule, and it
   should be argued as one.
5. **An expired exception fails the build.** This is the entire point. An
   exception that quietly outlives its date is a rule that was deleted without
   anybody approving the deletion.

## Requesting an exception

1. Open an issue explaining the constraint.
2. Write an ADR in [`docs/decisions/`](../docs/decisions/) using `/create-adr`.
3. Add a row to the table below **and** a detail block underneath it.
4. Get a CODEOWNERS approval.

An exception is not a way to skip review. It is a way to make an unavoidable
compromise visible, owned and time-boxed.

## What is *not* an exception

- A failing gate you believe is a false positive. That is a **bug in the
  detector**. Open an issue; narrow the rule. Do not register an exception for a
  rule that is misfiring — you would be excusing correct code from a broken
  check, and the check stays broken.
- Code under [`architecture-fixtures/`](../architecture-fixtures/). Those files
  violate rules deliberately so the controls can be proven to reject them. They
  are excluded from production analysis by configuration, not by exception.
- A `TODO` you intend to get to. That is a backlog item.

## Active exceptions

| ID | Gate / Rule | Owner | Created | Expires | Risk | ADR | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | — | — | — | — | — | — | *(none)* |

**There are currently no active exceptions.**

That is a deliberate state for the initial release, and it is the honest one:
the reference implementations were written to satisfy the rules rather than
around them. If this table is still empty in a year of real adoption, be
suspicious — either the rules are too weak to ever bind, or someone is quietly
suppressing instead of registering.

## Expired exceptions

| ID | Gate / Rule | Owner | Expired | Outcome |
| --- | --- | --- | --- | --- |
| — | — | — | — | *(none)* |

## Exception detail template

Copy this block below the table when adding an exception.

```markdown
### EXC-0001 — <short title>

- **Rule violated:** ARCH-0xx / GATE-0xx
- **Scope:** exact files or modules, as narrowly as possible
- **Owner:** @github-handle
- **Created:** YYYY-MM-DD
- **Expires:** YYYY-MM-DD (maximum 90 days from creation)
- **ADR:** ADR-00xx
- **Risk if it stays:** what breaks or degrades while this is in place
- **Why now:** the constraint that made compliance impossible in this change
- **Alternatives rejected:** what else was tried, and why it did not work
- **Removal plan:** the concrete steps that will retire this exception
- **Tracking issue:** #NNN
```

## Review cadence

Exceptions are reviewed at every release and whenever one is within 14 days of
expiry. Renewal is not automatic: it requires a new ADR arguing why the original
removal plan did not happen, which is deliberately more effort than simply
completing the removal.
