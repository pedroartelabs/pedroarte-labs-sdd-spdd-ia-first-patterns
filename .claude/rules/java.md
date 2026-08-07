<!-- GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: governance/policies/
     Regenerate with: make generate-agent-rules
     Policy checksum: sha256:0357a6ebe4ab8a4e3a4f6d22d43e091de336ef57c1e32c34c9d43b0a4c870768
-->

# Java rules

## Module boundaries

The Java reference is multi-module on purpose: Maven refuses a dependency that
the architecture forbids, so violations fail at compile time rather than at
review time.

```
payment-domain                  -> depends on nothing
payment-application             -> payment-domain
payment-adapter-in-rest         -> payment-application, payment-domain
payment-adapter-out-memory      -> payment-application, payment-domain
payment-adapter-out-persistence -> payment-application, payment-domain
payment-bootstrap               -> whatever composition requires
payment-architecture-tests      -> inspects the modules above
```

## Forbidden imports

- **Domain:** `org.springframework`, `jakarta.persistence`, `jakarta.servlet`, `javax.persistence`, `org.hibernate`, `com.fasterxml.jackson`, `org.apache.kafka`, `software.amazon.awssdk`, `java.sql`, `javax.sql`, `java.net.http`, `io.micrometer`, `org.slf4j`
- **Application:** `org.springframework`, `jakarta.persistence`, `org.hibernate`, `com.fasterxml.jackson`, `org.apache.kafka`, `software.amazon.awssdk`, `java.sql`, `java.net.http`

Frameworks are welcome in adapters and bootstrap. They are never welcome in
`payment-domain`. A domain entity is not a JPA entity and carries no Jackson,
Spring or persistence annotation.

## Rules that apply to Java

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

## Testing

- JUnit 5 + AssertJ for behaviour, ArchUnit for structure.
- Prefer hand-written fakes over mocks for outbound ports; a fake that
  implements the port is also a contract test subject.
- JaCoCo enforces coverage; PIT runs mutation testing in a separate job.
- Every architecture rule ships with a negative fixture proving it fires.
