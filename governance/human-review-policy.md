# Human review policy

What a human reviewer is responsible for in a process where a machine may have
written most of the diff.

## Why this needs stating

When an agent produces a clean, well-formatted, fully-tested-looking change, the
natural reviewer response is to skim it. That instinct is calibrated for human
authors, where clean formatting correlates with care. It does not transfer:
generated code is uniformly well-presented whether or not it is correct.

The reviewer's job therefore shifts. Less "is this tidy", more "is this the
thing we agreed to build, and do these tests actually prove it".

## What only a human can decide

Deterministic gates already cover dependency direction, cycles, forbidden
imports, coverage floors, secrets and schema validity. Do not spend review
attention re-checking what the pipeline checked. Spend it on:

1. **Does this match the specification's intent?** Not just its letter. A change
   can satisfy every acceptance criterion and still solve the wrong problem.
2. **Is the domain model right?** Naming, invariants, aggregate boundaries. A
   wrong boundary passes every architecture test — the tests check that the
   layers are respected, not that you drew them in the right place.
3. **Do the tests prove the behaviour, or just execute it?** Coverage is a
   floor. A test that asserts "no exception was thrown" moves the metric and
   proves nothing.
4. **Is the abstraction earned?** A port introduced for one implementation that
   will never have a second is ceremony. The policy demands ports at boundaries,
   not everywhere.
5. **What happens when this fails?** Timeouts, retries, partial writes,
   idempotency on replay, concurrent execution.
6. **Is anything here outside the declared scope?** Especially with agent-generated
   changes, where an unrelated "improvement" can arrive quietly.

## Required approvals

| Change | Approvals | CODEOWNERS required |
| --- | --- | --- |
| Documentation, typo | 1 | No |
| Example code | 1 | No |
| New architecture rule | 1 | **Yes** |
| `governance/policies/` | 1 | **Yes** |
| `.github/`, `.claude/`, `schemas/`, `scripts/` | 1 | **Yes** |
| Weakening any gate | 1 + ADR | **Yes** |
| Architecture test suites | 1 | **Yes** |

Stale approvals are dismissed on new commits. Conversations must be resolved
before merge.

## A reviewer may block on

- The specification and the implementation disagree.
- A business rule ended up in an adapter.
- A framework reached the domain.
- A missing port — infrastructure touched directly from the application.
- A dependency cycle, or a boundary crossed sideways.
- A gate weakened without an ADR.
- A test disabled without a linked issue and a reason.
- Evidence claimed but not recorded.
- A secret, or real personal or banking data.
- Changes materially outside the declared scope.

"Blocking" here means requesting changes with the rule named. Point at the rule
and the evidence, never at the person — see [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).

## What a reviewer must not do

- **Approve because the pipeline is green.** Green means no known rule was
  broken. It does not mean the change is right.
- **Approve because an AI review found nothing.** Article 6. An AI review that
  finds nothing is not evidence of safety.
- **Approve their own change**, including a change an agent produced under their
  direction.
- **Suggest weakening a gate** to unblock a review. Suggest an expiring, owned
  exception with an ADR instead.

## Reviewing agent-generated changes specifically

Ask the author for the `PROMPT-ID` and read the prompt. It is often faster than
reading the diff, and it reveals the actual failure mode: a prompt whose
`Structure` section allowed files it should not have, or whose `Safeguards`
section was thin.

Watch for the characteristic patterns:

- **Plausible-but-unused abstraction.** Interfaces with one implementation and no
  prospect of a second.
- **Tests written against the implementation** rather than the acceptance
  criteria — they pass, and they will keep passing when the behaviour breaks.
- **Silent scope creep.** Refactors bundled into a feature change.
- **Confident comments describing behaviour the code does not have.**
- **Error handling that catches broadly and logs**, converting a failure into a
  silent wrong answer.

## Evidence

Every pull request records the verification commands that were run and their
real results. A reviewer should check that the recorded evidence is plausible
for the change — and treat `NOT_EXECUTED` with a stated reason as a normal,
acceptable entry. It is far better than an unearned `PASS`, and a reviewer who
punishes honesty here will stop receiving it.

## Turnaround

Best effort, single maintainer. Security reports get priority. If a review is
blocking you and has gone quiet for a week, comment on the pull request.
