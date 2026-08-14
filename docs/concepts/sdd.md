# Spec-Driven Development (SDD)

SDD makes the specification the centre of the engineering process. Every
production code change traces to an approved specification with acceptance
criteria, architecture decisions, and evidence.

## Lifecycle

```
DRAFT → IN_REVIEW → APPROVED → IMPLEMENTING → VERIFIED → RELEASED
```

Each transition has entry requirements (gates) that must be met before the
specification can advance.

## Key artifacts

| Artifact | Purpose |
| --- | --- |
| `spec.md` | Problem, acceptance criteria, domain model, ports, risks |
| `clarifications.md` | Ambiguities discovered and resolved during review |
| `architecture.md` | Module decomposition, ports, fitness functions |
| `tasks.md` | Phased implementation plan, individually verifiable |
| `test-plan.md` | What each test level proves |
| `evidence.md` | Actual commands and actual results |
| `traceability.yaml` | Requirement → code → test → evidence mapping |

## Why not just code?

Code answers *how*. A specification answers *what* and *why*. When an AI agent
generates code, the specification is what it generates *from*. When a human
reviews the result, the specification is what they review *against*.
