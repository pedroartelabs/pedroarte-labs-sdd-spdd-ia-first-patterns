# ADR-0005: Canonical policy layer as single source of truth

## Status

Accepted

## Context

Multiple AI tools (Claude Code, GitHub Copilot, Cursor) each need instruction
files in different formats. Maintaining these independently leads to drift:
one tool's instructions contradict another's, and nobody notices until the wrong
code ships.

## Decision

`governance/policies/*.yaml` is the single source of truth. A deterministic
generator (`scripts/policy_lib.py`) produces all 13 agent instruction files
from it. Each generated file embeds a SHA-256 checksum of the policy content.
A drift checker distinguishes "policy changed without regeneration" from
"human edited a generated file" by comparing checksums.

## Consequences

### Positive

- One place to change a rule, 13 files updated deterministically
- Drift detection catches both kinds of staleness
- Generated files carry a DO NOT EDIT header

### Negative

- Adding a new tool format requires a new renderer in policy_lib.py
- Developers must run `make generate-agent-rules` after policy changes

### Neutral

- CI enforces the check; forgetting locally is caught before merge

## Compliance

- **Architecture rules affected:** THR-007, THR-008
- **Fitness functions:** check-generated-rule-drift.py, governance workflow
- **Review date:** 2026-11-06
