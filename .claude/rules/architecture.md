<!-- GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: governance/policies/
     Regenerate with: make generate-agent-rules
     Policy checksum: sha256:0357a6ebe4ab8a4e3a4f6d22d43e091de336ef57c1e32c34c9d43b0a4c870768
-->

# Architecture rules

Dependencies point inward. The domain is the centre and knows nothing about frameworks, transports or storage. Application orchestrates use cases behind ports. Adapters implement ports and translate technology. Bootstrap is the only place allowed to wire everything together.

Strategy: `package-by-bounded-context-first-then-hexagonal-layers-inside`.

## Layers

| Layer | May depend on | Java package | Python module |
| --- | --- | --- | --- |
| `domain` | *(nothing)* | `..domain..` | `payment.domain` |
| `application` | domain | `..application..` | `payment.application` |
| `adapter_inbound` | domain, application | `..adapter.in..` | `payment.adapters.inbound` |
| `adapter_outbound` | domain, application | `..adapter.out..` | `payment.adapters.outbound` |
| `bootstrap` | domain, application, adapter_inbound, adapter_outbound | `..bootstrap..` | `payment.bootstrap` |

## Forbidden dependencies

- `domain` must not depend on `application`, `adapter_inbound`, `adapter_outbound`, `bootstrap` — The domain is the centre; nothing inside it may point outward.
- `application` must not depend on `adapter_inbound`, `adapter_outbound`, `bootstrap` — The application talks to technology only through ports it declares.
- `adapter_inbound` must not depend on `adapter_outbound`, `bootstrap` — Adapters are siblings; they must never call each other directly.
- `adapter_outbound` must not depend on `adapter_inbound`, `bootstrap` — Adapters are siblings; they must never call each other directly.

## Enforced rules

- **ARCH-001** (blocker) — Domain must not depend on frameworks. Enforced by: archunit, import-linter, post-edit-hook, architecture-gate.
- **ARCH-002** (blocker) — Domain must not depend on application, adapters or bootstrap. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-003** (blocker) — Application must not depend on adapters. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-004** (blocker) — Inbound adapters must not depend on outbound adapters. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-005** (blocker) — Outbound adapters must not depend on inbound adapters. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-006** (blocker) — There must be no dependency cycles between packages or modules. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-007** (blocker) — Only bootstrap may perform composition. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-008** (high) — Ports must not carry technology names. Enforced by: archunit, architecture-gate.
- **ARCH-009** (blocker) — Domain entities must not be ORM entities and must carry no technical annotations. Enforced by: archunit, import-linter, architecture-gate.
- **ARCH-010** (high) — Persistence models live in the outbound persistence adapter, transport DTOs live in the inbound adapter. Enforced by: archunit, architecture-gate.
- **ARCH-011** (high) — Technical exceptions must be translated at the adapter boundary. Enforced by: review, ai-review.
- **ARCH-012** (high) — Time, randomness and identifier generation must be abstracted behind outbound ports when they affect business rules. Enforced by: archunit, import-linter, review.
- **ARCH-013** (blocker) — Every deliberate deviation requires an ADR with owner, justification and review date. Enforced by: architecture-exceptions, review, validate-repository.

## Naming conventions

- **NAM-001** — Ports must not carry technology names. Forbidden substrings: Jpa, Jdbc, Rest, Http, Kafka, Sql, Mongo, Redis, Dynamo.
- **NAM-002** — Inbound ports are named after a business capability and end with UseCase.
- **NAM-003** — Outbound ports are named after a business responsibility (Repository, Publisher, Clock, IdGenerator).

## Exceptions

Deliberate deviations are recorded in `governance/architecture-exceptions.md` and require
an ADR, an owner, a risk statement and an expiry date. No exception is permanent.
