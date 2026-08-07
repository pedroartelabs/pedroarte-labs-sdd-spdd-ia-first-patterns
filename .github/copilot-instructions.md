<!-- GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: governance/policies/
     Regenerate with: make generate-agent-rules
     Policy checksum: sha256:0357a6ebe4ab8a4e3a4f6d22d43e091de336ef57c1e32c34c9d43b0a4c870768
-->

# GitHub Copilot instructions

This repository enforces AI-First delivery under governance. The canonical rules
live in `governance/policies/`; this file is generated from them.

## Before writing code

- A change to production code requires an approved specification under `specs/`.
- Production paths: `examples/java-hexagonal/**/src/main/**`, `examples/python-hexagonal/src/**`, `tools/**/src/**`.
- The implementation follows a versioned SPDD prompt (`prompt.reasons.md`).

## Architecture

Dependencies point inward. The domain is the centre and knows nothing about frameworks, transports or storage. Application orchestrates use cases behind ports. Adapters implement ports and translate technology. Bootstrap is the only place allowed to wire everything together.

| Layer | May depend on | Java package | Python module |
| --- | --- | --- | --- |
| `domain` | *(nothing)* | `..domain..` | `payment.domain` |
| `application` | domain | `..application..` | `payment.application` |
| `adapter_inbound` | domain, application | `..adapter.in..` | `payment.adapters.inbound` |
| `adapter_outbound` | domain, application | `..adapter.out..` | `payment.adapters.outbound` |
| `bootstrap` | domain, application, adapter_inbound, adapter_outbound | `..bootstrap..` | `payment.bootstrap` |

- `domain` must not depend on `application`, `adapter_inbound`, `adapter_outbound`, `bootstrap` — The domain is the centre; nothing inside it may point outward.
- `application` must not depend on `adapter_inbound`, `adapter_outbound`, `bootstrap` — The application talks to technology only through ports it declares.
- `adapter_inbound` must not depend on `adapter_outbound`, `bootstrap` — Adapters are siblings; they must never call each other directly.
- `adapter_outbound` must not depend on `adapter_inbound`, `bootstrap` — Adapters are siblings; they must never call each other directly.

## Never do this

- Import a framework into `domain` (Java: Spring, JPA, Hibernate, Jackson; Python: FastAPI, SQLAlchemy, Pydantic).
- Make an inbound adapter call an outbound adapter directly.
- Put a business rule in a controller or a repository implementation.
- Use an ORM entity or a transport DTO as a domain model.
- Disable a test or weaken a quality gate to make a build pass.
- Introduce a dependency cycle.
- Commit a secret, a token or real personal data.

## Always do this

- Declare an outbound port in `application/ports/outbound` before touching infrastructure.
- Keep ports free of technology names (no `Jpa`, `Rest`, `Kafka`, `Sql` in a port name).
- Translate technical exceptions at the adapter boundary.
- Abstract clock, randomness and id generation behind ports when they affect business rules.
- Write the test with the code, at the level that actually proves the behaviour.
- Record the exact verification commands you ran and their real results.

Run `make verify` before proposing a change.
