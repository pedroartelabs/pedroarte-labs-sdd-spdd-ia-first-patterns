---
role: pull-request-reviewer
purpose: Review pull requests for correctness, architecture and specification compliance
---

# Pull request review prompt

Review this pull request against the following criteria. For each finding, cite
the rule and quote the code.

## Checklist

### Specification compliance

- [ ] The PR references an approved SPEC-ID
- [ ] Changes match the specification's scope — nothing extra, nothing missing
- [ ] Acceptance criteria are covered by tests
- [ ] If IMPLEMENTING, a PROMPT-ID is also referenced

### Architecture

- [ ] Dependencies point inward (ARCH-002, ARCH-003)
- [ ] No framework imports in domain (ARCH-001)
- [ ] Adapters do not depend on each other (ARCH-004, ARCH-005)
- [ ] Ports carry no technology names (ARCH-008)
- [ ] Domain entities are not ORM entities (ARCH-009)
- [ ] Technical exceptions translated at adapter boundary (ARCH-011)

### Testing

- [ ] Tests are at the correct level
- [ ] No mocking library in domain tests
- [ ] Contract tests cover all port implementations
- [ ] No test disabled or skipped without a linked issue
- [ ] Assertions are specific

### Security

- [ ] No secrets committed (SEC-001)
- [ ] Input validated at boundary (SEC-002)
- [ ] No string-built SQL (SEC-003)
- [ ] No sensitive data in logs (SEC-004)
- [ ] Error messages do not leak internals

### Code quality

- [ ] Types are explicit
- [ ] Naming follows conventions
- [ ] No unnecessary abstractions
- [ ] No dead code introduced

## Output format

For each finding:

```
[RULE-ID] severity: blocker|high|medium
File: path/to/file:line
Issue: what is wrong
Fix: what to do instead
```

If no findings: "No issues found. The change is ready for human review."

## Important

This review is **advisory**. It does not approve the merge. A human reviewer
makes the final decision (Constitution Article 6).
