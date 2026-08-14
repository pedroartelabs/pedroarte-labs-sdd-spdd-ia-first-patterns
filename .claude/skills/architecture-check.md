---
name: architecture-check
description: Run all architecture fitness functions and report results
user_invocable: true
---

# /architecture-check

Run all architecture fitness functions and report whether the codebase respects
its declared architecture.

## Steps

1. Run Python architecture checks:
   ```bash
   cd examples/python-hexagonal
   lint-imports
   python -m pytest tests/architecture/ -v
   ```
2. Run Java architecture checks (if JDK available):
   ```bash
   cd examples/java-hexagonal
   ./mvnw test -pl payment-architecture-tests
   ```
3. Run rule drift check:
   ```bash
   python scripts/check-generated-rule-drift.py
   ```
4. Report results:
   - Which contracts are KEPT
   - Which contracts are BROKEN (with the violated rule)
   - Whether negative fixtures are still properly rejected
   - Whether generated files match canonical policy

## Output format

```
Architecture check: PASS / FAIL

Python Import Linter: 6/6 contracts KEPT
Negative fixtures: 3/3 correctly rejected
Rule drift: no drift detected
Java ArchUnit: [result or NOT_EXECUTED]
```
