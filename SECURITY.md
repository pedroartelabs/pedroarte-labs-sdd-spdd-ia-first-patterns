# Security Policy

The canonical, machine-readable security policy lives in
[`governance/policies/security-policy.yaml`](governance/policies/security-policy.yaml).
This document is the human entry point.

## Reporting a vulnerability

Please **do not** open a public issue for a security problem.

Report privately through GitHub's
[private vulnerability reporting](https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/security/advisories/new)
on this repository.

Include, as far as you can:

- what the vulnerability is and where it lives (file, workflow, script);
- how to reproduce it;
- what an attacker gains;
- any suggested remediation.

**Response targets**

| Stage | Target |
| --- | --- |
| Acknowledgement | 5 business days |
| Initial assessment | 10 business days |
| Fix or mitigation plan | depends on severity, communicated in the assessment |

We follow coordinated disclosure. We will credit you in the advisory unless you
ask us not to.

## Scope

This repository is a **reference and pattern library**. It ships no production
service. The most valuable security reports here are therefore about the
*process and its automation*, not about a running system:

**In scope**

- GitHub Actions workflow misconfiguration (privilege escalation, secret
  exposure, unsafe handling of fork pull requests).
- Claude Code hook bypass: a way to make the `PreToolUse` guard permit an action
  it should block.
- Prompt-injection paths that would let untrusted repository content (an issue
  body, a pull request description, a fixture file) steer an agent.
- Weaknesses in the generated-file drift check that would let policy and agent
  instructions silently diverge.
- A quality gate that can be bypassed without detection.
- Secrets, credentials or real personal data committed anywhere in the tree.
- Vulnerable dependencies in `scripts/`, `tools/ai-review/`, or the example
  projects.

**Out of scope**

- The deliberately invalid code under `architecture-fixtures/`. Those files
  violate architecture rules **on purpose**, so that the automated controls can
  be proven to reject them. That is the point of the directory, not a defect.
- The `Create PIX Payment` example. It is educational: there is no real bank
  integration, no real PIX endpoint, and no real personal or banking data. It
  is not intended to be, and must not be used as, a payment implementation.
- Findings that require an attacker to already have write access to `main`.
- Results from an automated scanner pasted without analysis.

## Threat model

The full threat model for the AI-First process itself — prompt injection,
malicious fork pull requests, secret exfiltration, destructive agent commands,
supply chain compromise, policy tampering, automatic approval without human
supervision — is documented in
[`governance/policies/security-policy.yaml`](governance/policies/security-policy.yaml)
and rendered for agents in [`.claude/rules/security.md`](.claude/rules/security.md).

## Security controls in this repository

- Explicit least-privilege `permissions` in every workflow.
- No `pull_request_target` combined with a checkout of untrusted code; fork
  pull requests never receive repository secrets.
- Secret scanning (gitleaks) plus a `PreToolUse` hook that refuses to write
  known credential patterns to disk.
- CodeQL static analysis and dependency review on every pull request.
- Dependabot for automated, reviewed dependency updates.
- CODEOWNERS review required for `governance/`, `.github/`, `.claude/`,
  `schemas/`, `scripts/` and the architecture test suites.
- Branch ruleset on `main`: pull request required, at least one approval, no
  force push, no deletion, linear history.
- AI review is advisory and cannot approve a merge.

## A note on credentials

There are no real credentials in this repository and there never will be. Any
`.env.example` contains fictitious values. If a scanner flags something that
looks like a key here, it is either a fictitious example or a genuine mistake —
please report it and we will treat it as the latter until proven otherwise.
