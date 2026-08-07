# Support

## What this repository is

A public **reference and pattern library** for AI-First delivery under
governance: SDD, SPDD, Hexagonal Architecture, architecture tests, Claude Code
Skills and deterministic quality gates for Java and Python.

It is a set of patterns you copy and adapt. It is not a hosted service, not a
published library, and not a payment system.

## Where to go

| I want to… | Go here |
| --- | --- |
| Understand the concepts | [`docs/index.md`](docs/index.md) |
| Get running in five minutes | [README — Quick start](README.md#quick-start) |
| Read this in Portuguese | [`README.pt-BR.md`](README.pt-BR.md) |
| Follow the end-to-end process | [`docs/workflows/golden-path.md`](docs/workflows/golden-path.md) |
| Adopt this in an existing project | [`docs/guides/adopting-in-an-existing-project.md`](docs/guides/adopting-in-an-existing-project.md) |
| Configure Claude Code | [`docs/guides/configuring-claude-code.md`](docs/guides/configuring-claude-code.md) |
| Configure GitHub protection | [`docs/guides/configuring-github.md`](docs/guides/configuring-github.md) |
| Understand a rule I hit | [`docs/reference/policy-catalog.md`](docs/reference/policy-catalog.md) |
| Understand why a gate failed | [`docs/reference/quality-gates.md`](docs/reference/quality-gates.md) |
| Ask a question | [Discussions](https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/discussions) |
| Report a bug | [Bug issue template](https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/issues/new?template=bug.yml) |
| Propose a pattern | [Architecture pattern template](https://github.com/pedroartelabs/pedroarte-labs-sdd-spdd-ia-first-patterns/issues/new?template=architecture-pattern.yml) |
| Report a vulnerability | [`SECURITY.md`](SECURITY.md) — **not** a public issue |
| Contribute | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Before you open an issue

Run the doctor. Most environment problems answer themselves:

```bash
make doctor
```

Then run the full verification and include its real output in your report:

```bash
make verify
```

## Common situations

**`make check-rule-drift` fails.**
You edited a generated file, or you changed a policy without regenerating.
Generated files carry a `DO NOT EDIT` header. Edit `governance/policies/`
instead, then run `make generate-agent-rules` and commit the result.

**An architecture test fails and I think it is wrong.**
It might be. A false positive is a bug in the gate, not a reason to delete the
gate. Open an issue with the rule id (`ARCH-0xx`) and the code that triggered
it. If you need to ship before the detector is fixed, add a dated, owned
exception in [`governance/architecture-exceptions.md`](governance/architecture-exceptions.md)
with an ADR — never a permanent suppression.

**A test under `architecture-fixtures/` looks broken.**
Those files are invalid on purpose. The suite asserts that the controls
*reject* them. If they ever start passing, that is the real bug.

**`make verify-java` does not run.**
You need a JDK. See [`docs/guides/configuring-github.md`](docs/guides/configuring-github.md)
and the toolchain decision in
[`docs/decisions/ADR-0007-toolchain-versions.md`](docs/decisions/ADR-0007-toolchain-versions.md).

## Support expectations

This is a community project maintained on a best-effort basis by
[@pedroartelabs](https://github.com/pedroartelabs). There is no SLA. Security
reports get priority; everything else is handled as time allows.
