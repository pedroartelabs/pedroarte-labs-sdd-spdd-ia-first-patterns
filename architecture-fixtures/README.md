# Architecture fixtures — negative proofs

**The code in the `*-invalid-*` directories is broken on purpose.**

If a scanner flags it, that is the fixture working. See [`SECURITY.md`](../SECURITY.md)
— these paths are explicitly out of scope for vulnerability reports.

## Why this directory exists

A test suite that only runs against correct code proves that correct code
passes. It says nothing at all about whether the control can *fail*.

This is the most common way architecture governance quietly dies: someone adds
an ArchUnit rule with a typo in the package pattern, it matches nothing, it
reports green forever, and two years later the domain is full of JPA
annotations. Every gate was passing the entire time.

So each control here ships with a deliberately invalid fixture and a test
asserting the control **rejects** it. The repository's own suite passes because
the violations are detected, not because they are absent.

## The fixtures

| Fixture | Expectation | Violates |
| --- | --- | --- |
| `python-valid/` | accepted | — |
| `python-invalid-domain-framework-import/` | **rejected** | `ARCH-001` |
| `python-invalid-adapter-dependency/` | **rejected** | `ARCH-004` |
| `java-valid/` | accepted | — |
| `java-invalid-domain-framework-import/` | **rejected** | `ARCH-001` |
| `java-invalid-adapter-dependency/` | **rejected** | `ARCH-004` |

The canonical list lives in
[`governance/policies/testing-policy.yaml`](../governance/policies/testing-policy.yaml)
under `negative_fixtures.cases`, and the tests read it from there — so adding a
fixture to the policy without writing it, or writing one without registering it,
fails the build.

## The domain

The fixtures use a `shopcart` bounded context rather than `payment`, deliberately.
Reusing the real example's package name would risk a fixture shadowing the real
package on `sys.path` and producing a confusing failure in an unrelated test.

Each fixture is the smallest hexagon that can express the violation:

```
shopcart/
├── domain/        Cart, CartItem — pure
├── application/   AddItemUseCase + the ports it needs
├── adapters/
│   ├── inbound/   controller
│   └── outbound/  repository
└── bootstrap/     composition root
```

## What each invalid fixture does wrong

**`*-invalid-domain-framework-import`** — the domain imports a persistence
framework (`sqlalchemy` in Python, `jakarta.persistence` in Java). This is the
violation that starts as one convenient annotation and ends with a domain that
cannot be constructed without an open session.

**`*-invalid-adapter-dependency`** — the inbound adapter imports the outbound
adapter directly, skipping the application layer. Every rule the use case would
have applied now exists only on the HTTP path, invisible to the CLI, the
consumer and the scheduler.

## Running the proofs

```bash
make verify-architecture
```

Or directly:

```bash
# Python
pytest examples/python-hexagonal/tests/architecture -v

# Java
cd examples/java-hexagonal && ./mvnw -pl payment-architecture-tests test
```

## Adding a fixture

1. Register it in `governance/policies/testing-policy.yaml` under
   `negative_fixtures.cases` with its `expectation` and the rule it `violates`.
2. Create the directory with the smallest code that expresses the violation.
3. Run the suite. The new case is picked up from the policy automatically.

Keep it minimal. A fixture is a proof, not a sample application — every line
that is not required to trigger the violation makes the proof harder to read.

## These are excluded from production analysis

By configuration, not by exception:

- `.gitattributes` marks the directory `linguist-vendored`.
- The Python example's Ruff, mypy and pytest configuration is scoped to
  `examples/python-hexagonal/`.
- The Java fixtures are not Maven modules of the reference build.
- CodeQL and Bandit skip this path.

They are never registered in
[`governance/architecture-exceptions.md`](../governance/architecture-exceptions.md).
An exception excuses real code from a rule; these are test data for the rule
itself.
