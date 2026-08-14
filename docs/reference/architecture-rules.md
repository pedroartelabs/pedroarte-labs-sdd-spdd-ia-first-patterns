# Architecture rules

13 rules enforced by automated fitness functions.

| Rule | Severity | Description | Enforced by |
| --- | --- | --- | --- |
| ARCH-001 | blocker | Domain must not depend on frameworks | ArchUnit, Import Linter |
| ARCH-002 | blocker | Domain must not depend on outer layers | ArchUnit, Import Linter |
| ARCH-003 | blocker | Application must not depend on adapters | ArchUnit, Import Linter |
| ARCH-004 | blocker | Inbound adapters must not depend on outbound | ArchUnit, Import Linter |
| ARCH-005 | blocker | Outbound adapters must not depend on inbound | ArchUnit, Import Linter |
| ARCH-006 | blocker | No dependency cycles | ArchUnit, Import Linter |
| ARCH-007 | blocker | Only bootstrap may compose | ArchUnit, Import Linter |
| ARCH-008 | high | Ports must not carry technology names | ArchUnit |
| ARCH-009 | blocker | Domain entities are not ORM entities | ArchUnit, Import Linter |
| ARCH-010 | high | Persistence models in adapter, DTOs in adapter | ArchUnit |
| ARCH-011 | high | Technical exceptions translated at boundary | Review |
| ARCH-012 | high | Time/identity abstracted behind ports | ArchUnit, Import Linter |
| ARCH-013 | blocker | Deviations require an ADR | Review |

## Forbidden imports

### Domain layer

**Java:** `org.springframework`, `jakarta.persistence`, `jakarta.servlet`,
`javax.persistence`, `org.hibernate`, `com.fasterxml.jackson`, `org.apache.kafka`,
`software.amazon.awssdk`, `java.sql`, `javax.sql`, `java.net.http`, `io.micrometer`,
`org.slf4j`

**Python:** `fastapi`, `flask`, `django`, `starlette`, `sqlalchemy`, `pydantic`,
`boto3`, `botocore`, `httpx`, `requests`, `aiohttp`, `kafka`, `confluent_kafka`,
`redis`, `psycopg`, `pymongo`

## Exceptions

Deliberate deviations are recorded in `governance/architecture-exceptions.md`
and require an ADR, an owner, a risk statement, and an expiry date (max 90 days).
