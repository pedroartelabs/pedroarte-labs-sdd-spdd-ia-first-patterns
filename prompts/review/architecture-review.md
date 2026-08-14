---
role: architecture-reviewer
purpose: Deep architecture review focused on hexagonal boundaries and fitness functions
---

# Architecture review prompt

Perform a focused architecture review of the changed files. This is deeper than
the pull request review — it examines structural fitness, not just rule
compliance.

## Review dimensions

### Dependency direction

For every import in the changed files:

1. Identify the source layer (domain, application, adapter, bootstrap)
2. Identify the target layer
3. Verify the dependency points inward or is at the same layer

### Port design

- Are ports defined in the application layer?
- Do port names describe business responsibilities, not technologies?
- Are port methods cohesive — does each port have a single reason to change?

### Mapping boundaries

- Is mapping between representations explicit?
- Does the domain model shape itself around business rules, not transport or storage?
- Are DTOs confined to their adapter?

### Fitness function coverage

- Is every architectural rule enforced by an automated check?
- Are negative fixtures present for new rules?
- Do the `.importlinter` contracts (Python) or ArchUnit tests (Java) cover the change?

## Output format

```
## Findings

### [severity] Finding title
- **Rule:** ARCH-NNN
- **Location:** file:line
- **Issue:** description
- **Recommendation:** what to change

## Summary

Architecture fitness: PASS / NEEDS_WORK / VIOLATION
```
