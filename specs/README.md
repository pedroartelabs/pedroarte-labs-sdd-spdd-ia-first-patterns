# Specifications

Every change to production code starts here. A specification captures intent,
scope, acceptance criteria, architecture decisions, risks and traceability
before a single line of code is written.

## Directory structure

```
specs/
├── README.md               ← you are here
├── templates/              ← starting points for new specifications
│   ├── feature-spec.md
│   ├── bug-fix-spec.md
│   ├── hotfix-spec.md
│   ├── architecture-change-spec.md
│   ├── clarification-log.md
│   ├── architecture-plan.md
│   ├── task-plan.md
│   ├── test-plan.md
│   ├── evidence-report.md
│   └── traceability.yaml
└── examples/
    └── SPEC-EXAMPLE-001-create-pix-payment/
        ├── spec.md
        ├── prompt.reasons.md
        ├── clarifications.md
        ├── architecture.md
        ├── tasks.md
        ├── test-plan.md
        ├── evidence.md
        └── traceability.yaml
```

## Creating a new specification

```bash
make spec-new NAME="short-description" TYPE=feature
```

Or use the Claude Code skill:

```
/sdd-init
```

## Lifecycle

DRAFT → IN_REVIEW → APPROVED → IMPLEMENTING → VERIFIED → RELEASED

See `governance/policies/specification-policy.yaml` for the full state machine,
allowed transitions, and entry requirements.

## Naming convention

```
SPEC-{YEAR}-{SEQ}   e.g. SPEC-2026-001
SPEC-EXAMPLE-{SEQ}  e.g. SPEC-EXAMPLE-001  (for reference examples)
```

Each specification lives in its own directory:

```
specs/SPEC-2026-001-short-description/
```
