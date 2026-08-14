# Structured Prompt-Driven Development (SPDD)

SPDD treats prompts as versioned engineering artifacts, not disposable chat
messages. Every implementation prompt follows the REASONS model and links to
its specification.

## The REASONS model

| Section | Must answer |
| --- | --- |
| **R**equirements | What SPEC-ID, which acceptance criteria, what constraints? |
| **E**ntities | Which aggregates, value objects, events, ports? |
| **A**pproach | Hexagonal layer, inside-out order, incremental steps? |
| **S**tructure | File paths, module boundaries, package layout? |
| **O**perations | Commands to run, verification steps, evidence to collect? |
| **N**orms | Coding standards, naming, error handling, forbidden patterns? |
| **S**afeguards | What must the agent never do? Scope limits, rollback? |

## Why structure matters

An unstructured prompt ("implement the payment feature") gives the agent freedom
to make decisions a human should make. A REASONS prompt constrains every axis:
which files to touch, which tests to write, which patterns to follow, and
which actions to avoid.

## Versioning

Prompts use semantic versioning:
- **Patch:** clarification without scope change
- **Minor:** new acceptance criteria or constraints added
- **Major:** fundamental approach change

## Change budget

Every prompt declares a change budget: the list of files the implementation
may create or modify. Anything outside the budget requires a prompt update.
