# Getting started

## Prerequisites

- Python 3.11+
- Git
- (Optional) JDK 21+ for the Java reference
- (Optional) Claude Code CLI

## Setup

```bash
git clone https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns.git
cd pedroarte-labs-sdd-spdd-ia-first-patterns
make doctor    # verify your toolchain
make setup     # install Python dev dependencies
```

## Verify everything works

```bash
make verify    # runs all checks
```

## Explore the example

The `specs/examples/SPEC-EXAMPLE-001-create-pix-payment/` directory contains a
complete specification, SPDD prompt, clarification log, architecture plan, task
plan, test plan, evidence report, and traceability manifest.

The `examples/python-hexagonal/` directory contains the implementation that was
built from that specification.

## Create your first specification

```bash
make spec-new NAME="your feature" TYPE=feature
```

Then follow the [golden path](../workflows/golden-path.md).

## Using Claude Code skills

If you have Claude Code installed, the repository ships with 11 skills:

```
/sdd-init            — Create a new specification
/sdd-specify         — Fill in a specification
/sdd-clarify         — Identify ambiguities
/sdd-plan            — Create architecture and task plans
/spdd-generate       — Generate a REASONS prompt
/implement-python-feature — Implement in Python
/implement-java-feature   — Implement in Java
/architecture-check  — Run architecture fitness functions
/review-change       — Review staged changes
/create-adr          — Create an Architecture Decision Record
/close-spec          — Close a specification
```
