---
role: security-reviewer
purpose: Security-focused review of code changes
---

# Security review prompt

Review the changed files for security vulnerabilities, following
`governance/policies/security-policy.yaml`.

## Review dimensions

### Secret exposure (SEC-001)

Scan every changed file for:

- Hardcoded credentials, tokens, API keys, passwords
- Connection strings with embedded credentials
- Private key material
- Patterns: `ghp_`, `gho_`, `sk-`, `AKIA`, `-----BEGIN`

### Input validation (SEC-002)

For every new endpoint or command handler:

- Is input validated before it reaches the domain?
- Are type constraints enforced (not just presence)?
- Is the validation in the adapter, not the domain?

### Injection (SEC-003)

- Are all database queries parameterised?
- Is there any string interpolation in SQL, shell commands, or log formats?

### Information leakage (SEC-004)

- Do error responses contain stack traces, driver messages, or internal paths?
- Do logs contain credentials, tokens, or personal data?
- Are identifiers masked in events and logs?

### Dependency safety (SEC-007, SEC-008)

- Are new dependencies pinned to exact versions?
- Do any new dependencies have known vulnerabilities?

## Output format

```
## Findings

### [SEC-NNN] Finding title
- **Severity:** critical / high / medium
- **Location:** file:line
- **Issue:** description
- **Fix:** specific remediation

## Summary

Security: PASS / NEEDS_WORK / BLOCKED
```
