# Roadmap

Where this repository is going, and what it deliberately will not become.

Dates are intentions, not commitments. This is a community project maintained on
a best-effort basis.

## Now — v0.1.x (released 2026-08-06)

The foundation is in place and enforced:

- Canonical machine-readable policy with generated agent adapters and drift
  detection.
- Full SDD lifecycle with validated state transitions.
- SPDD REASONS prompts as versioned artifacts.
- Java and Python hexagonal references with architecture tests.
- Negative fixtures proving the controls actually reject violations.
- Claude Code Skills, subagents and tested hooks.
- Eleven CI workflows with least-privilege permissions.

**Focus for the patch line:** correcting what real adopters hit first —
documentation gaps, doctor script coverage on more platforms, clearer validator
messages.

## Next — v0.2.0

- **Second bounded context.** One context proves the layering; two prove the
  *package-by-bounded-context-first* strategy, which is the harder and more
  valuable claim. Likely a `ledger` context that consumes payment events.
- **Contract testing between contexts.** Consumer-driven contracts so a bounded
  context cannot break its neighbour silently.
- **Adoption scaffolding.** `make adopt` to copy the governance layer into an
  existing project and generate a tailored `.importlinter` / ArchUnit baseline
  from the code that is already there — the realistic path, since almost nobody
  starts from a clean sheet.
- **Exception expiry enforcement in CI.** The register already requires expiry
  dates; CI should fail on an expired one rather than trusting a human to notice.
- **Richer traceability reporting.** A generated coverage matrix showing which
  acceptance criteria have no test.

## Later — v0.3.0

- **A third language reference.** TypeScript or Go, to demonstrate that the
  policy layer is genuinely language-agnostic and that the generator is not
  quietly Java/Python-shaped.
- **Metrics.** Lead time from specification to release, gate failure rates by
  rule, exception age distribution. Governance that cannot be measured cannot be
  improved.
- **Agent evaluation harness.** Run a fixed set of specifications through an
  agent and score the output against the architecture gates automatically —
  making "does this prompt actually work?" an empirical question.
- **Policy versioning and migration.** A documented path for evolving
  `governance/policies/` without breaking downstream adopters.

## Under consideration

Not committed. Feedback welcome in [Discussions](https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/discussions).

- A GitHub App that enforces the specification gate across an organisation.
- Publishing the validators as an installable package so adopters do not vendor
  `scripts/`.
- Event-driven and CQRS variants of the reference architecture.
- Spring Modulith as an alternative Java boundary mechanism to multi-module Maven.
- A `.cursorrules` compatibility adapter, if the format proves still relevant.

## Explicit non-goals

Saying no clearly is part of the design.

- **This will not become a payment system.** The PIX example is educational and
  will stay that way: no real bank integration, no real endpoints, no real data.
- **This will not become a framework.** It is a set of patterns you copy and
  adapt. The moment it becomes a dependency you upgrade, it starts constraining
  the architectures it was meant to teach.
- **This will not make AI the approver.** Every version will keep deterministic
  gates as the blocking checks and AI review as advisory.
- **This will not chase every agent tool.** The canonical policy plus a generator
  is the extension point. Adding a new tool means adding a renderer, not a new
  source of truth.
- **This will not accumulate rules for their own sake.** A rule with no automated
  enforcer is an aspiration. Rules that cannot be checked get deleted rather
  than documented.

## How to influence this

Open an [issue](https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/issues/new/choose)
or start a [discussion](https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/discussions).
Reports from real adoption — what broke, what was over-engineered, what you had
to delete to make it usable — are more valuable than feature requests.
