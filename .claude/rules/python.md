<!-- GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: governance/policies/
     Regenerate with: make generate-agent-rules
     Policy checksum: sha256:0357a6ebe4ab8a4e3a4f6d22d43e091de336ef57c1e32c34c9d43b0a4c870768
-->

# Python rules

## Layout

`src` layout, one package per bounded context:

```
src/payment/
├── domain/
├── application/
│   ├── ports/{inbound,outbound}/
│   └── use_cases/
├── adapters/{inbound,outbound}/
└── bootstrap/
```

## Forbidden imports

- **Domain:** `fastapi`, `flask`, `django`, `starlette`, `sqlalchemy`, `pydantic`, `boto3`, `botocore`, `httpx`, `requests`, `aiohttp`, `kafka`, `confluent_kafka`, `redis`, `psycopg`, `pymongo`
- **Application:** `fastapi`, `flask`, `django`, `starlette`, `sqlalchemy`, `boto3`, `httpx`, `requests`, `kafka`, `redis`, `psycopg`

Note that `pydantic` is forbidden in the domain deliberately. It is an excellent
transport-validation library and a poor domain model: validation-on-construction
is not the same thing as an invariant that the type system and the aggregate
enforce together.

## Rules that apply to Python

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

## Typing

- Public APIs carry explicit type annotations.
- Ports are `typing.Protocol` definitions in the application layer.
- Domain models are plain dataclasses (frozen where they are value objects).
- No blanket `Any`; no bare `# type: ignore` without a written reason.
- `None` is handled explicitly, never by accident.
- DTO conversion happens in adapters, never in the domain.

## Tooling

Ruff (lint + format), mypy (strict), Import Linter (architecture), pytest with
pytest-cov, Hypothesis where property tests earn their keep, Bandit for security.
