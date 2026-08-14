---
role: test-quality-reviewer
purpose: Review test quality, coverage and correct level placement
---

# Test quality review prompt

Review the test changes for quality, correct placement, and coverage.

## Review dimensions

### Level placement

For each test, verify it is at the correct level:

| Level | Characteristics |
| --- | --- |
| Domain | Pure, no framework, no I/O, microseconds |
| Application | Fakes for outbound ports, no real infrastructure |
| Contract | One suite parametrised over every port implementation |
| Integration | Real technology, technology-specific behaviour only |
| Architecture | Structural, deterministic, blocking |
| End-to-end | Full slice, few, representative, stable |

A test at the wrong level is slower, vaguer, or both.

### Assertion quality

- Are assertions specific? (`assert status == PENDING` not `assert result`)
- Do tests assert outcomes, not implementation details?
- Are property tests used where a law exists?

### Test doubles

- Are fakes preferred over mocks?
- Do fakes implement the port protocol?
- Are fakes shared via `tests/support.py`?

### Independence

- Do tests depend on execution order?
- Do tests depend on wall-clock time?
- Do tests share mutable state?

### Coverage

- Domain + application: ≥ 95% line, ≥ 90% branch
- Overall: ≥ 85% line, ≥ 75% branch
- Is any coverage threshold being weakened?

## Output format

```
## Findings

### Finding title
- **Rule:** TEST-NNN
- **Location:** file:line
- **Issue:** description
- **Fix:** what to change

## Summary

Test quality: PASS / NEEDS_WORK
Coverage: within thresholds / below thresholds
```
