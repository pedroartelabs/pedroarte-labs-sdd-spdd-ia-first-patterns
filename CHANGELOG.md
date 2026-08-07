# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

While the major version is `0`, the public surface — policy schemas, Skill
names, script interfaces, directory layout — may change in a minor release.

## [Unreleased]

Nothing yet.

## [0.1.0] - 2026-08-06

Initial public release. Experimental: the patterns are complete and enforced,
but the API surface is expected to move before `1.0.0`.

### Added

**Governance and canonical policy**

- `governance/policies/` as the single machine-readable source of truth:
  architecture, AI-First, specification, testing, security and quality-gate
  policies.
- `governance/constitution.md` with ten non-negotiable articles.
- Deterministic generation of every agent instruction file from that policy via
  `scripts/generate-agent-rules.py`, and drift detection via
  `scripts/check-generated-rule-drift.py` — which distinguishes "policy changed
  without regeneration" from "a human edited a generated file".
- Architecture exception register with mandatory expiry dates.

**Spec-Driven Development (SDD)**

- Specification lifecycle `DRAFT → IN_REVIEW → APPROVED → IMPLEMENTING →
  VERIFIED → RELEASED` plus `REJECTED`, `SUPERSEDED`, `DEPRECATED`, `CANCELLED`
  and `HOTFIX`, with enforced entry requirements per state.
- Templates for feature, bug-fix, hotfix and architecture-change specifications,
  clarification logs, architecture plans, task plans, test plans, evidence
  reports and traceability manifests.
- JSON Schemas for specifications, prompts, traceability, evidence and the
  architecture policy itself.
- `scripts/validate-specs.py` with actionable failure messages that name the
  missing section rather than reporting a generic schema error.

**Structured Prompt-Driven Development (SPDD)**

- The REASONS model — Requirements, Entities, Approach, Structure, Operations,
  Norms, Safeguards — as a versioned, reviewable engineering artifact.
- Prompt templates for implementation, refactoring, test generation and
  migration; system prompts for architecture, specification and secure-coding
  guardians; review prompts for pull requests, architecture, security and test
  quality.
- `scripts/validate-prompts.py` enforcing prompt identity, versioning and
  linkage to a specification.

**Claude Code integration**

- Eleven Skills covering the full lifecycle: `/sdd-init`, `/sdd-specify`,
  `/sdd-clarify`, `/sdd-plan`, `/spdd-generate`, `/implement-java-feature`,
  `/implement-python-feature`, `/architecture-check`, `/review-change`,
  `/create-adr`, `/close-spec`.
- Nine specialised subagents including an Architecture Guardian able to reject a
  change on structural grounds.
- `PreToolUse`, `PostToolUse` and `Stop` hooks with their own automated test
  suite covering permitted operations, missing specification, generated-file
  edits, destructive commands and completion with failing tests.

**Java reference**

- Seven-module Maven project enforcing hexagonal boundaries at compile time:
  domain, application, inbound REST adapter, in-memory and persistence outbound
  adapters, bootstrap, and a dedicated architecture-test module.
- ArchUnit rules covering dependency direction, adapter isolation, cycles,
  forbidden framework imports, port naming and composition.

**Python reference**

- `src`-layout package with the same bounded context, `Protocol`-based ports and
  the same functional intent, written idiomatically rather than transliterated
  from Java.
- Import Linter contracts as executable architecture fitness functions.

**Negative proofs**

- Six fixture projects, three of them deliberately invalid, with tests asserting
  the controls *reject* them. Valid code alone proves nothing about enforcement.

**CI and supply chain**

- Eleven focused workflows: repository validation, specification gate,
  architecture gate, Java CI, Python CI, security, CodeQL, dependency review,
  documentation, AI review and release.
- Least-privilege `permissions` in every workflow, no unsafe
  `pull_request_target`, fork pull requests without secrets.
- Provider-agnostic AI review tool that degrades explicitly when credentials are
  absent instead of failing silently.

**Documentation**

- Bilingual entry points (`README.md`, `README.pt-BR.md`), concept guides,
  lifecycle workflows, adoption guides, reference catalogues and seven ADRs.

### Known limitations

- Single maintainer; `CODEOWNERS` points at an individual rather than a team.
- The persistence adapter uses an embedded database. Testcontainers-based
  integration tests are scaffolded but exercised only where Docker is available.
- Mutation testing is configured but runs on a schedule, not on every pull
  request.
- The `Create PIX Payment` example is educational: no real bank integration, no
  real PIX endpoint, no real personal or banking data.

[Unreleased]: https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/releases/tag/v0.1.0
