# Contributing

Thank you for considering a contribution. This repository practises what it
documents, so contributing here means going through the same governed process
the patterns describe. That is deliberate: a governance repository that bypasses
its own governance would prove nothing.

## Table of contents

- [Ground rules](#ground-rules)
- [Setting up](#setting-up)
- [What kind of change are you making?](#what-kind-of-change-are-you-making)
- [The golden path](#the-golden-path)
- [Commit convention](#commit-convention)
- [Pull request expectations](#pull-request-expectations)
- [Using AI assistance](#using-ai-assistance)
- [When a gate blocks you](#when-a-gate-blocks-you)

## Ground rules

1. **No production code without an approved specification.** Production paths are
   `examples/java-hexagonal/**/src/main/**`, `examples/python-hexagonal/src/**`
   and `tools/**/src/**`.
2. **Never edit a generated file.** `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`,
   `.github/copilot-instructions.md` and `.cursor/rules/*.mdc` are projections of
   `governance/policies/`. Edit the policy, run `make generate-agent-rules`.
3. **Never weaken a gate to make a build pass.** Lowering a coverage threshold,
   deleting an architecture rule or disabling a test requires an ADR and a
   CODEOWNERS approval.
4. **Evidence, not confidence.** Report the commands you actually ran and their
   actual results. `NOT_EXECUTED` is an acceptable and honest answer; a
   fabricated `PASS` is not.

## Setting up

```bash
git clone https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns.git
cd pedroarte-labs-sdd-spdd-ia-first-patterns
make doctor    # tells you exactly which tools are missing
make setup     # installs dev dependencies
make verify    # proves the checkout is healthy before you change anything
```

`make doctor` is not decoration. Run it first; it will tell you whether your
JDK, Python, Maven and GitHub CLI are usable, and it degrades gracefully — a
missing Docker only means integration tests are skipped locally, not that you
are blocked.

## What kind of change are you making?

| Change | Needs a spec? | Start with |
| --- | --- | --- |
| Typo, wording, broken link | No | A pull request |
| New or changed documentation | No | A pull request |
| New architecture pattern or rule | **Yes** | [Architecture pattern issue](https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/issues/new?template=architecture-pattern.yml) |
| Change to `governance/policies/` | **Yes** + ADR | An issue, then `/create-adr` |
| New feature in a reference example | **Yes** | `make spec-new` |
| Bug fix in a reference example | **Yes** (bug-fix spec) | `make spec-new TYPE=bug-fix` |
| New Claude Skill or agent | **Yes** | `make spec-new` |
| Dependency bump | No | A pull request (Dependabot usually gets there first) |

If you are unsure, open an issue and ask. Being told "no spec needed" costs you
one comment; discovering it after implementing costs you the implementation.

## The golden path

```bash
make spec-new NAME="create-payment" TYPE=feature
```

That scaffolds `specs/SPEC-<year>-<n>-create-payment/` with today's real date.
Then, inside Claude Code:

```
/sdd-specify SPEC-2026-001
/sdd-clarify SPEC-2026-001
/sdd-plan SPEC-2026-001
/spdd-generate SPEC-2026-001
/implement-java-feature SPEC-2026-001
/architecture-check SPEC-2026-001
/review-change SPEC-2026-001
/close-spec SPEC-2026-001
```

Every one of those commands maps to a real Skill in `.claude/skills/`. You are
not required to use Claude Code — the same steps are documented as manual
procedures in [`docs/workflows/golden-path.md`](docs/workflows/golden-path.md)
and the templates in `specs/templates/` work perfectly well by hand.

The specification moves `DRAFT → IN_REVIEW → APPROVED → IMPLEMENTING → VERIFIED
→ RELEASED`. `make validate-specs` refuses illegal transitions and tells you
precisely what is missing:

```
SPEC-2026-004 cannot move to APPROVED:
- acceptance criteria are missing
- outbound ports are undefined
- test strategy is incomplete
```

## Commit convention

[Conventional Commits](https://www.conventionalcommits.org/). Keep commits
logically separated — one concern per commit, so a reviewer can follow the
reasoning and a bisect can find the culprit.

```
feat:     a new capability
fix:      a bug fix
docs:     documentation only
test:     tests only
refactor: behaviour-preserving restructuring
ci:       workflows and automation
chore:    tooling, dependencies, housekeeping
perf:     performance
build:    build system
```

Scope is encouraged: `feat(java): add PaymentEventPublisher port`.

Reference the specification in the body, not in every line of code:

```
feat(python): add CreatePixPaymentUseCase

Implements REQ-001 and REQ-002.

Spec: SPEC-2026-001
Prompt: PROMPT-2026-001
```

## Pull request expectations

The [pull request template](.github/pull_request_template.md) asks for a
specification id, a prompt id, affected modules, architectural impact, tests
executed, evidence, security analysis, rollback considerations and an AI usage
declaration. It asks because reviewers need it, not to create paperwork.

Before you open a pull request:

```bash
make verify
```

If a step could not run in your environment, say so in the pull request rather
than omitting it. An honest gap is reviewable; a silent one is not.

Blocking checks are deterministic: repository validation, specification gate,
architecture gate, Java build, Python build, security scan, documentation check.
The AI review is **advisory** and never blocks a merge on its own — see
[ADR-0005](docs/decisions/ADR-0005-ai-review-is-not-the-only-gate.md).

## Using AI assistance

AI assistance is welcome and expected — this is an AI-First repository. It comes
with obligations:

- **Declare it.** The pull request template has an AI usage field. Options are
  `none`, `assisted`, `agent-generated-and-human-reviewed`.
- **Review it yourself first.** You are the author. "The agent wrote it" is not a
  defence for a change you cannot explain.
- **Version the prompt.** A non-trivial implementation carries a
  `prompt.reasons.md` following the REASONS model, linked to the specification.
- **Never let an agent weaken a gate.** If an agent proposes lowering a
  threshold, suppressing a rule or deleting a test to make CI green, that is the
  signal to stop and re-read the specification, not to accept the diff.

## When a gate blocks you

A failing gate is information. Read the message — the validators are written to
name the rule and the fix.

- **`check-rule-drift` fails.** You edited a generated file or changed a policy
  without regenerating. Run `make generate-agent-rules`.
- **An architecture test fails.** Read the rule id (`ARCH-0xx`) in
  [`docs/reference/policy-catalog.md`](docs/reference/policy-catalog.md). Usually
  the fix is to introduce the port you skipped.
- **You believe it is a false positive.** It might be. That is a bug in the
  detector, not a reason to delete the detector. Open an issue with the rule id
  and the triggering code. If you must ship first, add a dated, owned exception
  in [`governance/architecture-exceptions.md`](governance/architecture-exceptions.md)
  with an ADR and a removal plan. Exceptions expire; permanent ones do not exist.
- **A fixture test fails.** Check whether it is under `architecture-fixtures/`.
  Those files are invalid on purpose and the suite asserts they are *rejected*.
  If they start passing, the control broke.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Technical
disagreement is welcome; blocking a change because it violates an architecture
rule is normal review, not hostility. Point at the rule and the evidence, never
at the person.

## Licence

By contributing you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).
