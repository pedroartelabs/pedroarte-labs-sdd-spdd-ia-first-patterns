# Evidence report — SPEC-EXAMPLE-001

Recorded commands and their actual results. Constitution Article 7: evidence
before completion; `NOT_EXECUTED` is honest, fabricated `PASS` is governance
failure.

## EVIDENCE-001 — Python test suite

**Command:**

```bash
cd examples/python-hexagonal
python -m pytest tests/ -v --tb=short -q
```

**Result:** PASS — 181 tests passed, 0 failed, 0 skipped.

**Recorded:** 2026-08-06

<details>
<summary>Abbreviated output</summary>

```
tests/unit/test_money.py ......................                       [ 12%]
tests/unit/test_pix_key.py .................                         [ 21%]
tests/unit/test_payment_aggregate.py ........................        [ 34%]
tests/unit/test_create_pix_payment_use_case.py ....................  [ 45%]
tests/contract/test_payment_repository_contract.py ..................[ 55%]
tests/integration/test_sql_payment_repository.py .........          [ 60%]
tests/architecture/test_import_contracts.py ....                    [ 62%]
tests/architecture/test_fixtures_are_rejected.py ........           [ 67%]
tests/architecture/test_contracts_match_policy.py ....              [ 69%]
tests/end_to_end/test_create_payment_api.py ..................      [ 79%]
...
181 passed in 6.42s
```

</details>

## EVIDENCE-002 — Python coverage

**Command:**

```bash
cd examples/python-hexagonal
python -m pytest tests/ --cov=payment --cov-report=term-missing --cov-branch -q
```

**Result:** PASS — 97.79% line coverage, branch coverage above thresholds.

**Recorded:** 2026-08-06

<details>
<summary>Coverage summary</summary>

```
Name                                                          Stmts   Miss  Cover
payment/domain/money.py                                          32      0   100%
payment/domain/pix_key.py                                        42      0   100%
payment/domain/payment.py                                        68      0   100%
payment/domain/events.py                                          8      0   100%
payment/domain/errors.py                                         12      0   100%
payment/application/use_cases/create_pix_payment.py              30      0   100%
payment/application/ports/inbound/create_pix_payment.py          18      0   100%
payment/application/ports/outbound/payment_repository.py          8      0   100%
payment/adapters/inbound/rest/payment_controller.py              38      1    97%
payment/adapters/outbound/persistence/sql_payment_repository.py  42      1    98%
...
TOTAL                                                           362      8    98%
```

</details>

## EVIDENCE-003 — Architecture contracts (Import Linter)

**Command:**

```bash
cd examples/python-hexagonal
lint-imports
```

**Result:** PASS — 6 contracts checked, all KEPT.

**Recorded:** 2026-08-06

<details>
<summary>Output</summary>

```
=============
Import Linter
=============

Contracts: 6 found
-----
layers [ARCH-002/003/007] ... KEPT
adapter-independence [ARCH-004/005] ... KEPT
domain-is-framework-free [ARCH-001] ... KEPT
application-is-framework-free [ARCH-001] ... KEPT
domain-has-no-ambient-io [ARCH-012] ... KEPT
bootstrap-is-not-imported [ARCH-007] ... KEPT
-----
6 contracts checked; 0 broken.
```

</details>

## EVIDENCE-004 — Negative architecture fixtures

**Command:**

```bash
cd examples/python-hexagonal
python -m pytest tests/architecture/test_fixtures_are_rejected.py -v
```

**Result:** PASS — valid fixture accepted, both invalid fixtures rejected by the
correct rule and only the correct rule.

**Recorded:** 2026-08-06

<details>
<summary>Output</summary>

```
tests/architecture/test_fixtures_are_rejected.py::test_the_control_reaches_the_expected_verdict[python-valid-True] PASSED
tests/architecture/test_fixtures_are_rejected.py::test_the_control_reaches_the_expected_verdict[python-invalid-domain-framework-import-False] PASSED
tests/architecture/test_fixtures_are_rejected.py::test_the_control_reaches_the_expected_verdict[python-invalid-adapter-dependency-False] PASSED
tests/architecture/test_fixtures_are_rejected.py::test_only_the_intended_rule_fires[python-invalid-domain-framework-import-ARCH-001] PASSED
tests/architecture/test_fixtures_are_rejected.py::test_only_the_intended_rule_fires[python-invalid-adapter-dependency-ARCH-004/005] PASSED
...
8 passed in 4.12s
```

</details>

## EVIDENCE-005 — Type checking (mypy strict)

**Command:**

```bash
cd examples/python-hexagonal
python -m mypy src/ tests/ --strict
```

**Result:** PASS — 0 errors.

**Recorded:** 2026-08-06

## EVIDENCE-006 — Linting and formatting (ruff)

**Command:**

```bash
cd examples/python-hexagonal
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/
```

**Result:** PASS — 0 violations, formatting matches.

**Recorded:** 2026-08-06

## EVIDENCE-007 — Security scan (bandit)

**Command:**

```bash
cd examples/python-hexagonal
python -m bandit -r src/ -c pyproject.toml
```

**Result:** PASS — 0 issues.

**Recorded:** 2026-08-06

## EVIDENCE-008 — Rule drift check

**Command:**

```bash
python scripts/check-generated-rule-drift.py
```

**Result:** PASS — all 13 generated files match canonical policy checksum.

**Recorded:** 2026-08-06

## EVIDENCE-009 — Java reference

**Status:** NOT_EXECUTED

**Reason:** The authoring environment has no JDK installed. Java source is
written but `mvn verify` was never executed locally. This will be verified in CI
once the GitHub Actions workflow runs on a JDK-equipped runner.

This is recorded as `NOT_EXECUTED` rather than claimed as passing — Constitution
Article 7.
