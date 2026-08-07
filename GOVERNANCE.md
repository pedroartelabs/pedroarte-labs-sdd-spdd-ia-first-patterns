# Governance

How decisions get made in this repository, who can make them, and what cannot be
decided away.

The binding, machine-readable rules live in [`governance/policies/`](governance/policies/).
The non-negotiable principles live in [`governance/constitution.md`](governance/constitution.md).
This document explains the human process around them.

## Roles

| Role | Who | Can |
| --- | --- | --- |
| **Maintainer** | [@pedroartelabs](https://github.com/pedroartelabs) | Merge, release, change policy, grant roles |
| **Reviewer** | Appointed by a maintainer | Approve pull requests, block on architecture grounds |
| **Contributor** | Anyone | Open issues, propose specifications, submit pull requests |
| **AI agent** | Claude Code and equivalents | Analyse, plan, implement, test, review — **never approve** |

This is currently a single-maintainer project. That is a stated limitation, not
a design goal; see [ROADMAP.md](ROADMAP.md).

## What requires what

| Change | Requires |
| --- | --- |
| Typo, link fix, wording | 1 approval |
| Documentation | 1 approval |
| New example code | Approved spec + 1 approval + green gates |
| New architecture rule | Spec + **ADR** + CODEOWNERS approval |
| Change to `governance/policies/` | Spec + **ADR** + CODEOWNERS approval + regenerated adapters |
| Weakening any quality gate | **ADR** + CODEOWNERS approval + recorded risk |
| New Claude Skill or agent | Spec + 1 approval |
| Dependency bump | 1 approval, green gates |
| Emergency hotfix | Maintainer + retroactive spec within 5 business days |

## The decision hierarchy

When two goals conflict, resolve in this order. This ordering is itself a
decision, and it is deliberate: it is easier to recover from an inconvenient
process than from a security incident or a corrupted architecture.

1. Security
2. Functional correctness
3. Architectural integrity
4. Traceability
5. Testability
6. Reproducibility
7. Clarity
8. Developer experience
9. Performance
10. Convenience

Do not sacrifice architectural integrity merely to reduce the number of files.
Do not sacrifice security to automate more. Do not sacrifice traceability to
generate code faster.

## Architecture Decision Records

Any decision that is expensive to reverse gets an ADR in
[`docs/decisions/`](docs/decisions/). An ADR records status, context, forces,
options, the decision, positive and negative consequences, risks, and the
criteria under which it should be revisited.

Use `/create-adr` in Claude Code, or copy an existing ADR.

An ADR is **required** for:

- adopting or changing an architectural pattern;
- changing the canonical policies;
- weakening any quality gate;
- a deliberate, permanent deviation from an architecture rule;
- changing the supported toolchain versions.

ADRs are immutable once accepted. Superseding an ADR means writing a new one
that references it, not editing history.

## Exceptions

Deliberate rule violations are recorded in
[`governance/architecture-exceptions.md`](governance/architecture-exceptions.md).
Every exception carries an id, justification, owner, creation date, **expiry
date**, risk, linked ADR and removal plan.

No exception is permanent by default. The maximum duration is 90 days. An
expired exception fails the build — which is the entire point, because an
exception that never expires is just a rule that was quietly deleted.

## The role of AI

AI agents are first-class participants and are governed accordingly.

**They may**: analyse specifications, identify ambiguity, model the domain,
propose architecture, implement against an approved prompt, generate tests,
review changes, maintain documentation, operate tools.

**They may not**: approve a merge, decide that a gate may be weakened, assert
that a command passed without it having run, or author credentials.

The AI review workflow is advisory. When provider credentials are absent it
reports so explicitly and the deterministic gates continue unchanged:

```
AI review skipped: provider credentials are not configured.
Deterministic architecture and quality gates remain active.
```

The reasoning is in [ADR-0005](docs/decisions/ADR-0005-ai-review-is-not-the-only-gate.md):
a probabilistic reviewer is a useful second opinion and a terrible sole gate.

## Branch protection

`main` is protected by a ruleset ([`.github/rulesets/main-branch-ruleset.json`](.github/rulesets/main-branch-ruleset.json)):
pull request required, at least one approval, stale approvals dismissed,
conversations resolved, required status checks green, linear history, no force
push, no deletion.

**Emergency bypass.** Only the maintainer may bypass, only for a security
incident or a production-breaking defect, and every bypass requires:

1. a public issue opened within 24 hours explaining what was bypassed and why;
2. a retroactive specification within 5 business days;
3. a follow-up pull request restoring full compliance.

A bypass that is not documented afterwards is a governance failure in its own
right.

## Releases

Semantic Versioning. While the major version is `0`, the public surface —
policy schemas, Skill names, script interfaces — may change in a minor release;
changes are always recorded in [CHANGELOG.md](CHANGELOG.md).

A release is cut only when every essential gate passes, the changelog is
updated, and the version honestly represents the maturity of the work.

## Changing this document

Governance changes through the same process it describes: an issue, a
specification, an ADR, a pull request, and a CODEOWNERS approval.
