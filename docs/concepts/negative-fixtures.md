# Negative Architecture Fixtures

A test that passes on valid code proves the tooling runs. It does not prove the
tooling catches violations. Negative fixtures close this gap.

## How it works

1. A **valid fixture** contains correct code — it should pass all contracts
2. An **invalid fixture** contains a deliberate violation — it should fail
3. Tests assert three things:
   - The invalid fixture is rejected
   - The correct rule fires (not a different one)
   - Only one rule fires (no false positives)

## Example

```
architecture-fixtures/
├── python-valid/                                    → KEPT (accepted)
├── python-invalid-domain-framework-import/          → BROKEN (ARCH-001)
└── python-invalid-adapter-dependency/               → BROKEN (ARCH-004/005)
```

The `python-invalid-domain-framework-import` fixture has `from sqlalchemy import
Numeric` in a domain file. The test asserts that Import Linter rejects it and
that the ARCH-001 contract is the one that fires.

## Meta-verification

Remove the violation from an invalid fixture. The test must fail, proving it
was the violation the test was checking. This was done during initial
development and recorded in the evidence report.

## Why this matters

A rule that has never failed is a rule nobody has verified. Negative fixtures
are the proof that enforcement capability exists, not just good intentions.
