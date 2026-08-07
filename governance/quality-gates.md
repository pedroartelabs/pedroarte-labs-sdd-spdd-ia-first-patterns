# Quality gates

The human-readable companion to [`policies/quality-gates.yaml`](policies/quality-gates.yaml),
which is the binding, machine-readable source.

## The principle

**A gate is only real if something automated enforces it.**

Every gate below names the script, workflow or test suite that proves it. A rule
with no enforcer is an aspiration, and this repository deletes aspirations rather
than documenting them — because a catalogue of unenforced rules teaches people
that the catalogue can be ignored.

## The 23 gates

### Specification and process

| ID | Fails when | Enforced by |
| --- | --- | --- |
| `GATE-001` | Production code changes without an approved `SPEC-ID` | `check-pr-spec-link.py` |
| `GATE-002` | A specification's frontmatter, id, state or required section is invalid | `validate-specs.py` |
| `GATE-003` | A specification enters a state whose entry requirements are unmet | `validate-specs.py` |
| `GATE-004` | A prompt has no version, no id, or no linked specification | `validate-prompts.py` |
| `GATE-018` | `traceability.yaml` references a file, test or prompt that does not exist | `validate-traceability.py` |
| `GATE-022` | The pull request records no executed verification command | `check-pr-spec-link.py` |

### Architecture

| ID | Fails when | Enforced by |
| --- | --- | --- |
| `GATE-005` | Domain imports a forbidden framework | ArchUnit + Import Linter |
| `GATE-006` | Application depends on an adapter | ArchUnit + Import Linter |
| `GATE-007` | An inbound adapter imports an outbound adapter, or vice versa | ArchUnit + Import Linter |
| `GATE-008` | Any package or module cycle exists | ArchUnit slices + Import Linter |
| `GATE-009` | Any architecture test fails | architecture test suites |
| `GATE-010` | A deliberately invalid fixture is **accepted** | fixture rejection tests |

`GATE-010` is the one that makes the rest trustworthy. Passing tests on valid
code prove that valid code passes. Only a rejected invalid fixture proves the
control can actually fail.

### Testing

| ID | Fails when | Enforced by |
| --- | --- | --- |
| `GATE-011` | A test is disabled without a linked issue and a reason | repository validation |
| `GATE-012` | Coverage drops below threshold | JaCoCo + pytest-cov |
| `GATE-021` | A lint or type suppression carries no justification | repository validation |

Coverage floors: domain and application at 95% line / 90% branch; repository
overall at 85% line / 75% branch. These are floors, not targets. A covered line
is not a tested behaviour.

### Policy integrity

| ID | Fails when | Enforced by |
| --- | --- | --- |
| `GATE-013` | A policy changed but generated adapters were not regenerated | `check-generated-rule-drift.py` |
| `GATE-014` | A generated file was edited by hand | `check-generated-rule-drift.py` |
| `GATE-015` | A gate was weakened with no ADR | CODEOWNERS + policy validation |
| `GATE-019` | A required repository document is missing or empty | repository validation |
| `GATE-020` | A `TODO` or `FIXME` has no issue reference | repository validation |

`GATE-013` and `GATE-014` look identical in a plain diff, so the checker
compares the policy checksum embedded in each generated header and reports them
separately — because the fixes differ. One says "run the generator"; the other
says "revert your edit and change the policy instead".

### Security

| ID | Fails when | Enforced by |
| --- | --- | --- |
| `GATE-016` | A credential pattern appears anywhere in the tree | gitleaks |
| `GATE-017` | A dependency change introduces a high or critical advisory | dependency review |
| `GATE-023` | A workflow declares no explicit `permissions` block | repository validation |

## Required status checks

These job names are referenced by the `main` branch ruleset and must match the
implemented jobs exactly. A ruleset pointing at a check that does not exist
blocks every merge forever; one pointing at a renamed check silently protects
nothing.

```
repository-validation
specification-gate
architecture-gate
java-build
python-build
security-scan
documentation-check
```

The `ai-review` job is deliberately **absent** from that list. Constitution
Article 6.

## Exceptions

No exception is permanent. Maximum 90 days. Every exception carries an id, gate,
justification, owner, creation date, expiry, risk, ADR and removal plan, and
lives in [`architecture-exceptions.md`](architecture-exceptions.md).

## False positives

A false positive is **a bug in the gate**, not a reason to delete the gate.

The correct sequence is: narrow the rule so it stops misfiring, add a dated
exception if you must ship before the fix lands, and open an issue to repair the
detector. Deleting the check because it was wrong once removes protection from
every future change — trading a small present annoyance for an unbounded future
cost.

## When a gate blocks you

Read the message. The validators are written to name the rule and the fix rather
than to report a generic failure:

```
SPEC-2026-004 cannot move to APPROVED:
- acceptance criteria are missing
- outbound ports are undefined
- test strategy is incomplete
```

If the gate is right, fix the change. If the gate is wrong, fix the gate. The
one option that is not available is making the gate quieter.
