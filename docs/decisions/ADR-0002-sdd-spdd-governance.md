# ADR-0002: SDD and SPDD as the governance model

## Status

Accepted

## Context

AI-assisted development requires structured inputs (specifications, prompts) and
structured outputs (evidence, traceability) to maintain quality and
accountability. Without governance, AI becomes a black box that produces code
nobody can trace to requirements.

## Decision

Adopt Spec-Driven Development (SDD) with a full lifecycle state machine and
Structured Prompt-Driven Development (SPDD) using the REASONS model. Every
production code change traces to an approved specification and a versioned prompt.

## Consequences

### Positive

- Clear accountability: every change traces to a specification
- AI inputs are versioned, reviewable, and auditable
- Quality gates enforce the process automatically

### Negative

- Higher overhead per change (specification, prompt, evidence)
- Process may feel heavy for trivial changes

### Neutral

- Hotfix path exists for emergencies with retroactive specification

## Compliance

- **Architecture rules affected:** SPEC-GATE-001 through SPEC-GATE-041
- **Fitness functions:** validate-specs.py, validate-prompts.py, validate-traceability.py
- **Review date:** 2026-11-06
