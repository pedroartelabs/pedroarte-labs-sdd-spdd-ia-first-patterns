# Quality gates

23 gates that must pass before a change reaches main.

## Specification gates

| Gate | Checks | Enforcement |
| --- | --- | --- |
| GATE-001 | Specification exists and is approved | validate-specs.py |
| GATE-002 | Acceptance criteria in Given/When/Then | validate-specs.py |
| GATE-003 | Architecture plan exists | validate-specs.py |
| GATE-004 | Task plan exists | validate-specs.py |
| GATE-005 | SPDD prompt linked | validate-specs.py |

## Code gates

| Gate | Checks | Enforcement |
| --- | --- | --- |
| GATE-006 | Python lint (ruff) | python-ci.yml |
| GATE-007 | Python types (mypy strict) | python-ci.yml |
| GATE-008 | Python tests pass | python-ci.yml |
| GATE-009 | Python coverage ≥ 85% line | python-ci.yml |
| GATE-010 | Python security (bandit) | python-ci.yml |
| GATE-011 | Java build (mvn verify) | java-ci.yml |
| GATE-012 | Java tests pass | java-ci.yml |
| GATE-013 | Java coverage (JaCoCo) | java-ci.yml |

## Architecture gates

| Gate | Checks | Enforcement |
| --- | --- | --- |
| GATE-014 | Import Linter contracts KEPT | python-ci.yml |
| GATE-015 | ArchUnit rules pass | java-ci.yml |
| GATE-016 | Negative fixtures rejected | python-ci.yml |
| GATE-017 | Generated files match policy | governance.yml |

## Security gates

| Gate | Checks | Enforcement |
| --- | --- | --- |
| GATE-018 | No secrets committed | security.yml |
| GATE-019 | Dependency review | security.yml |
| GATE-020 | Workflow permissions least-privilege | security.yml |

## Governance gates

| Gate | Checks | Enforcement |
| --- | --- | --- |
| GATE-021 | Traceability valid | governance.yml |
| GATE-022 | Evidence recorded | governance.yml |
| GATE-023 | Human approval on PR | branch ruleset |
